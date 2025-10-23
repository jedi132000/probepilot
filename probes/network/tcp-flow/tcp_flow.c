/*
 * TCP Flow Monitor eBPF Probe
 * Tracks TCP connection lifecycle, throughput, and latency
 * 
 * This probe attaches to kernel tracepoints to monitor:
 * - TCP connection establishment
 * - Data transfer rates
 * - Connection teardown
 * - Latency measurements
 */

#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define AF_INET 2
#define AF_INET6 10
#define MAX_ENTRIES 10240

/* Data structures for storing flow information */
struct flow_key {
    __u32 saddr;
    __u32 daddr;
    __u16 sport;
    __u16 dport;
    __u8 protocol;
};

struct flow_data {
    __u64 bytes_tx;
    __u64 bytes_rx;
    __u64 packets_tx;
    __u64 packets_rx;
    __u64 first_seen;
    __u64 last_seen;
    __u32 rtt_samples;
    __u32 rtt_total;
    __u8 state;
};

struct tcp_event {
    __u64 timestamp;
    __u32 pid;
    __u32 saddr;
    __u32 daddr;
    __u16 sport;
    __u16 dport;
    __u32 bytes;
    __u32 rtt;
    __u8 event_type; // 1=connect, 2=accept, 3=send, 4=recv, 5=close
    char comm[16];
};

/* BPF Maps for storing flow data */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, struct flow_key);
    __type(value, struct flow_data);
} flow_map SEC(".maps");

/* Ring buffer for sending events to userspace */
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

/* Configuration map */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, __u32);
} config_map SEC(".maps");

/* Helper function to create flow key */
static __always_inline void make_flow_key(struct flow_key *key, 
                                         __u32 saddr, __u32 daddr,
                                         __u16 sport, __u16 dport) {
    key->saddr = saddr;
    key->daddr = daddr;
    key->sport = sport;
    key->dport = dport;
    key->protocol = IPPROTO_TCP;
}

/* Helper function to send event to userspace */
static __always_inline void send_event(__u8 event_type, struct sock *sk,
                                      __u32 bytes, __u32 rtt) {
    struct tcp_event *event;
    struct inet_sock *inet;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return;
    
    event->timestamp = bpf_ktime_get_ns();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->event_type = event_type;
    event->bytes = bytes;
    event->rtt = rtt;
    
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    // Extract socket information
    inet = (struct inet_sock *)sk;
    BPF_CORE_READ_INTO(&event->saddr, inet, inet_saddr);
    BPF_CORE_READ_INTO(&event->daddr, inet, inet_daddr);
    BPF_CORE_READ_INTO(&event->sport, inet, inet_sport);
    BPF_CORE_READ_INTO(&event->dport, inet, inet_dport);
    
    // Convert to host byte order
    event->sport = bpf_ntohs(event->sport);
    event->dport = bpf_ntohs(event->dport);
    
    bpf_ringbuf_submit(event, 0);
}

/* Trace TCP connection establishment */
SEC("tp/sock/inet_sock_set_state")
int trace_tcp_state_change(struct trace_event_raw_inet_sock_set_state *ctx) {
    struct sock *sk = (struct sock *)ctx->skaddr;
    __u16 family = ctx->family;
    __u16 sport = ctx->sport;
    __u16 dport = ctx->dport;
    __u32 saddr = ctx->saddr;
    __u32 daddr = ctx->daddr;
    int oldstate = ctx->oldstate;
    int newstate = ctx->newstate;
    
    // Only track IPv4 TCP connections
    if (family != AF_INET)
        return 0;
    
    // Track connection establishment
    if (oldstate == TCP_SYN_SENT && newstate == TCP_ESTABLISHED) {
        send_event(1, sk, 0, 0); // Connect event
    }
    
    // Track connection acceptance
    if (oldstate == TCP_SYN_RECV && newstate == TCP_ESTABLISHED) {
        send_event(2, sk, 0, 0); // Accept event
    }
    
    // Track connection close
    if (newstate == TCP_CLOSE) {
        send_event(5, sk, 0, 0); // Close event
    }
    
    return 0;
}

/* Trace TCP data transmission */
SEC("tp/tcp/tcp_probe")
int trace_tcp_probe(struct trace_event_raw_tcp_probe *ctx) {
    struct sock *sk = (struct sock *)ctx->sk;
    __u32 snd_nxt = ctx->snd_nxt;
    __u32 snd_una = ctx->snd_una;
    __u32 snd_cwnd = ctx->snd_cwnd;
    __u32 ssthresh = ctx->ssthresh;
    __u32 snd_wnd = ctx->snd_wnd;
    __u32 srtt = ctx->srtt;
    
    // Calculate bytes in flight
    __u32 bytes_in_flight = snd_nxt - snd_una;
    
    // Send probe event with RTT information
    send_event(3, sk, bytes_in_flight, srtt);
    
    return 0;
}

/* Trace TCP retransmissions */
SEC("tp/tcp/tcp_retransmit_skb")
int trace_tcp_retransmit(struct trace_event_raw_tcp_retransmit_skb *ctx) {
    struct sock *sk = (struct sock *)ctx->sk;
    
    // Send retransmit event
    send_event(6, sk, 0, 0);
    
    return 0;
}

/* Kprobe for tcp_sendmsg to track outbound data */
SEC("kprobe/tcp_sendmsg")
int BPF_KPROBE(tcp_sendmsg, struct sock *sk, struct msghdr *msg, size_t size) {
    struct flow_key key = {};
    struct flow_data *flow;
    struct inet_sock *inet;
    __u64 ts = bpf_ktime_get_ns();
    
    // Extract socket information
    inet = (struct inet_sock *)sk;
    __u32 saddr, daddr;
    __u16 sport, dport;
    
    BPF_CORE_READ_INTO(&saddr, inet, inet_saddr);
    BPF_CORE_READ_INTO(&daddr, inet, inet_daddr);
    BPF_CORE_READ_INTO(&sport, inet, inet_sport);
    BPF_CORE_READ_INTO(&dport, inet, inet_dport);
    
    make_flow_key(&key, saddr, daddr, bpf_ntohs(sport), bpf_ntohs(dport));
    
    // Update flow statistics
    flow = bpf_map_lookup_elem(&flow_map, &key);
    if (!flow) {
        struct flow_data new_flow = {};
        new_flow.first_seen = ts;
        new_flow.last_seen = ts;
        new_flow.bytes_tx = size;
        new_flow.packets_tx = 1;
        bpf_map_update_elem(&flow_map, &key, &new_flow, BPF_ANY);
    } else {
        flow->bytes_tx += size;
        flow->packets_tx += 1;
        flow->last_seen = ts;
    }
    
    // Send transmission event
    send_event(3, sk, size, 0);
    
    return 0;
}

/* Kprobe for tcp_cleanup_rbuf to track inbound data */
SEC("kprobe/tcp_cleanup_rbuf")
int BPF_KPROBE(tcp_cleanup_rbuf, struct sock *sk, int copied) {
    struct flow_key key = {};
    struct flow_data *flow;
    struct inet_sock *inet;
    __u64 ts = bpf_ktime_get_ns();
    
    if (copied <= 0)
        return 0;
    
    // Extract socket information
    inet = (struct inet_sock *)sk;
    __u32 saddr, daddr;
    __u16 sport, dport;
    
    BPF_CORE_READ_INTO(&saddr, inet, inet_saddr);
    BPF_CORE_READ_INTO(&daddr, inet, inet_daddr);
    BPF_CORE_READ_INTO(&sport, inet, inet_sport);
    BPF_CORE_READ_INTO(&dport, inet, inet_dport);
    
    make_flow_key(&key, saddr, daddr, bpf_ntohs(sport), bpf_ntohs(dport));
    
    // Update flow statistics
    flow = bpf_map_lookup_elem(&flow_map, &key);
    if (!flow) {
        struct flow_data new_flow = {};
        new_flow.first_seen = ts;
        new_flow.last_seen = ts;
        new_flow.bytes_rx = copied;
        new_flow.packets_rx = 1;
        bpf_map_update_elem(&flow_map, &key, &new_flow, BPF_ANY);
    } else {
        flow->bytes_rx += copied;
        flow->packets_rx += 1;
        flow->last_seen = ts;
    }
    
    // Send receive event
    send_event(4, sk, copied, 0);
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
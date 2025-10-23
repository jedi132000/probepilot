/*
 * CPU Performance Profiler eBPF Probe
 * Tracks CPU usage, process scheduling, and performance metrics
 * 
 * This probe monitors:
 * - CPU usage per process and system-wide
 * - Process scheduling events
 * - Context switches and preemptions
 * - CPU frequency scaling events
 * - Load balancing across cores
 */

#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_ENTRIES 10240
#define MAX_CPUS 256
#define TASK_COMM_LEN 16

/* Data structures */
struct cpu_sample {
    __u64 timestamp;
    __u32 pid;
    __u32 cpu;
    __u64 runtime;
    __u64 vruntime;
    __u32 prio;
    __u32 weight;
    char comm[TASK_COMM_LEN];
};

struct process_stats {
    __u64 total_runtime;
    __u64 schedule_count;
    __u64 voluntary_switches;
    __u64 involuntary_switches;
    __u64 last_seen;
    __u32 min_cpu;
    __u32 max_cpu;
};

struct cpu_stats {
    __u64 idle_time;
    __u64 user_time;
    __u64 system_time;
    __u64 irq_time;
    __u64 softirq_time;
    __u64 context_switches;
    __u32 frequency;
    __u32 load_avg;
};

/* BPF Maps */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, __u32); // PID
    __type(value, struct process_stats);
} process_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
    __uint(max_entries, MAX_CPUS);
    __type(key, __u32); // CPU ID
    __type(value, struct cpu_stats);
} cpu_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

/* Configuration */
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 4);
    __type(key, __u32);
    __type(value, __u32);
} config_map SEC(".maps");

/* Helper function to send CPU sample to userspace */
static __always_inline void send_cpu_sample(struct task_struct *task, 
                                           __u32 cpu, __u64 runtime) {
    struct cpu_sample *sample;
    
    sample = bpf_ringbuf_reserve(&events, sizeof(*sample), 0);
    if (!sample)
        return;
    
    sample->timestamp = bpf_ktime_get_ns();
    sample->cpu = cpu;
    sample->runtime = runtime;
    
    BPF_CORE_READ_INTO(&sample->pid, task, pid);
    BPF_CORE_READ_INTO(&sample->prio, task, prio);
    BPF_CORE_READ_INTO(&sample->comm, task, comm);
    
    // Read scheduling entity information if available
    struct sched_entity *se = &task->se;
    if (se) {
        BPF_CORE_READ_INTO(&sample->vruntime, se, vruntime);
        BPF_CORE_READ_INTO(&sample->weight, se, load.weight);
    }
    
    bpf_ringbuf_submit(sample, 0);
}

/* Trace process scheduling events */
SEC("tp/sched/sched_switch")
int trace_sched_switch(struct trace_event_raw_sched_switch *ctx) {
    struct task_struct *prev = (struct task_struct *)ctx->prev_pid;
    struct task_struct *next = (struct task_struct *)ctx->next_pid;
    __u32 prev_pid = ctx->prev_pid;
    __u32 next_pid = ctx->next_pid;
    __u32 cpu = bpf_get_smp_processor_id();
    __u64 ts = bpf_ktime_get_ns();
    
    // Update process statistics for outgoing task
    if (prev_pid > 0) {
        struct process_stats *stats = bpf_map_lookup_elem(&process_map, &prev_pid);
        if (!stats) {
            struct process_stats new_stats = {};
            new_stats.last_seen = ts;
            new_stats.min_cpu = cpu;
            new_stats.max_cpu = cpu;
            bpf_map_update_elem(&process_map, &prev_pid, &new_stats, BPF_ANY);
        } else {
            stats->last_seen = ts;
            if (cpu < stats->min_cpu) stats->min_cpu = cpu;
            if (cpu > stats->max_cpu) stats->max_cpu = cpu;
            
            // Determine if switch was voluntary or involuntary
            if (ctx->prev_state == TASK_RUNNING) {
                stats->involuntary_switches++;
            } else {
                stats->voluntary_switches++;
            }
        }
    }
    
    // Update process statistics for incoming task
    if (next_pid > 0) {
        struct process_stats *stats = bpf_map_lookup_elem(&process_map, &next_pid);
        if (!stats) {
            struct process_stats new_stats = {};
            new_stats.schedule_count = 1;
            new_stats.last_seen = ts;
            new_stats.min_cpu = cpu;
            new_stats.max_cpu = cpu;
            bpf_map_update_elem(&process_map, &next_pid, &new_stats, BPF_ANY);
        } else {
            stats->schedule_count++;
            stats->last_seen = ts;
            if (cpu < stats->min_cpu) stats->min_cpu = cpu;
            if (cpu > stats->max_cpu) stats->max_cpu = cpu;
        }
    }
    
    // Update CPU statistics
    struct cpu_stats *cpu_stats = bpf_map_lookup_elem(&cpu_map, &cpu);
    if (cpu_stats) {
        cpu_stats->context_switches++;
    }
    
    return 0;
}

/* Trace process wakeup events */
SEC("tp/sched/sched_wakeup")
int trace_sched_wakeup(struct trace_event_raw_sched_wakeup *ctx) {
    __u32 pid = ctx->pid;
    __u32 cpu = ctx->target_cpu;
    
    // Send wakeup sample
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    send_cpu_sample(task, cpu, 0);
    
    return 0;
}

/* Sample CPU performance periodically */
SEC("perf_event")
int sample_cpu_perf(struct bpf_perf_event_data *ctx) {
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u32 cpu = bpf_get_smp_processor_id();
    __u64 ts = bpf_ktime_get_ns();
    
    // Skip kernel threads
    if (pid == 0)
        return 0;
    
    // Update process runtime statistics
    struct process_stats *stats = bpf_map_lookup_elem(&process_map, &pid);
    if (!stats) {
        struct process_stats new_stats = {};
        new_stats.total_runtime = 1;
        new_stats.last_seen = ts;
        new_stats.min_cpu = cpu;
        new_stats.max_cpu = cpu;
        bpf_map_update_elem(&process_map, &pid, &new_stats, BPF_ANY);
    } else {
        stats->total_runtime++;
        stats->last_seen = ts;
        if (cpu < stats->min_cpu) stats->min_cpu = cpu;
        if (cpu > stats->max_cpu) stats->max_cpu = cpu;
    }
    
    // Send CPU sample
    send_cpu_sample(task, cpu, stats ? stats->total_runtime : 1);
    
    return 0;
}

/* Monitor CPU frequency changes */
SEC("tp/power/cpu_frequency")
int trace_cpu_frequency(struct trace_event_raw_cpu_frequency *ctx) {
    __u32 cpu = ctx->cpu_id;
    __u32 frequency = ctx->state;
    
    // Update CPU frequency in stats
    struct cpu_stats *stats = bpf_map_lookup_elem(&cpu_map, &cpu);
    if (stats) {
        stats->frequency = frequency;
    }
    
    return 0;
}

/* Monitor CPU idle events */
SEC("tp/power/cpu_idle")
int trace_cpu_idle(struct trace_event_raw_cpu_idle *ctx) {
    __u32 cpu = bpf_get_smp_processor_id();
    __u32 state = ctx->state;
    
    struct cpu_stats *stats = bpf_map_lookup_elem(&cpu_map, &cpu);
    if (!stats)
        return 0;
    
    // Track idle time (state != -1 means entering idle)
    if (state != (__u32)-1) {
        stats->idle_time++;
    }
    
    return 0;
}

/* Monitor IRQ handling */
SEC("tp/irq/irq_handler_entry")
int trace_irq_entry(struct trace_event_raw_irq_handler_entry *ctx) {
    __u32 cpu = bpf_get_smp_processor_id();
    
    struct cpu_stats *stats = bpf_map_lookup_elem(&cpu_map, &cpu);
    if (stats) {
        stats->irq_time++;
    }
    
    return 0;
}

/* Monitor soft IRQ handling */
SEC("tp/irq/softirq_entry")
int trace_softirq_entry(struct trace_event_raw_softirq_entry *ctx) {
    __u32 cpu = bpf_get_smp_processor_id();
    
    struct cpu_stats *stats = bpf_map_lookup_elem(&cpu_map, &cpu);
    if (stats) {
        stats->softirq_time++;
    }
    
    return 0;
}

/* Kprobe for more detailed scheduling information */
SEC("kprobe/finish_task_switch")
int BPF_KPROBE(finish_task_switch, struct task_struct *prev) {
    struct task_struct *current = (struct task_struct *)bpf_get_current_task();
    __u32 prev_pid, curr_pid;
    __u32 cpu = bpf_get_smp_processor_id();
    __u64 ts = bpf_ktime_get_ns();
    
    BPF_CORE_READ_INTO(&prev_pid, prev, pid);
    BPF_CORE_READ_INTO(&curr_pid, current, pid);
    
    // Calculate runtime for the previous task
    if (prev_pid > 0) {
        struct process_stats *stats = bpf_map_lookup_elem(&process_map, &prev_pid);
        if (stats) {
            __u64 runtime = ts - stats->last_seen;
            stats->total_runtime += runtime;
            
            // Send detailed sample
            send_cpu_sample(prev, cpu, runtime);
        }
    }
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
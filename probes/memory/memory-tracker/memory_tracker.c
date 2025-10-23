/*
 * Memory Tracker eBPF Probe
 * Monitors memory allocation, deallocation, and usage patterns
 * 
 * This probe tracks:
 * - Memory allocations and deallocations
 * - Page faults and memory pressure
 * - Process memory usage (RSS, VSZ, heap)
 * - System-wide memory statistics
 * - Memory leaks and fragmentation
 */

#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define MAX_ENTRIES 10240
#define MAX_STACK_DEPTH 20
#define TASK_COMM_LEN 16

/* Memory allocation event types */
enum alloc_type {
    ALLOC_MALLOC = 1,
    ALLOC_CALLOC,
    ALLOC_REALLOC,
    ALLOC_FREE,
    ALLOC_MMAP,
    ALLOC_MUNMAP,
    ALLOC_BRK,
    ALLOC_PAGE,
};

/* Data structures */
struct memory_event {
    __u64 timestamp;
    __u32 pid;
    __u32 tid;
    __u64 addr;
    __u64 size;
    __u64 old_addr;  // for realloc
    __u32 type;      // enum alloc_type
    __u32 flags;
    __u64 stack_id;
    char comm[TASK_COMM_LEN];
};

struct process_memory {
    __u64 total_allocated;
    __u64 total_freed;
    __u64 current_usage;
    __u64 peak_usage;
    __u64 allocation_count;
    __u64 free_count;
    __u64 page_faults;
    __u64 major_faults;
    __u64 rss_pages;
    __u64 vmem_pages;
};

struct system_memory {
    __u64 total_memory;
    __u64 free_memory;
    __u64 available_memory;
    __u64 cached_memory;
    __u64 buffer_memory;
    __u64 slab_memory;
    __u64 page_cache_size;
    __u32 memory_pressure;
};

struct allocation_info {
    __u64 size;
    __u64 timestamp;
    __u64 stack_id;
    __u32 pid;
};

/* BPF Maps */
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES);
    __type(key, __u32); // PID
    __type(value, struct process_memory);
} process_memory_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, MAX_ENTRIES * 4);
    __type(key, __u64); // Address
    __type(value, struct allocation_info);
} allocation_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 1);
    __type(key, __u32);
    __type(value, struct system_memory);
} system_memory_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_STACK_TRACE);
    __uint(max_entries, 1024);
    __uint(key_size, sizeof(__u32));
    __uint(value_size, MAX_STACK_DEPTH * sizeof(__u64));
} stack_traces SEC(".maps");

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

/* Helper function to send memory event to userspace */
static __always_inline void send_memory_event(__u32 pid, __u64 addr, 
                                             __u64 size, __u32 type,
                                             __u64 old_addr) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return;
    
    event->timestamp = bpf_ktime_get_ns();
    event->pid = pid;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = addr;
    event->size = size;
    event->old_addr = old_addr;
    event->type = type;
    event->flags = 0;
    
    // Capture stack trace
    event->stack_id = bpf_get_stackid(bpf_get_current_task(), &stack_traces, 
                                     BPF_F_USER_STACK);
    
    // Get process name
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
}

/* Helper function to update process memory statistics */
static __always_inline void update_process_memory(__u32 pid, __s64 size_delta,
                                                 __u32 is_allocation) {
    struct process_memory *mem = bpf_map_lookup_elem(&process_memory_map, &pid);
    if (!mem) {
        struct process_memory new_mem = {};
        bpf_map_update_elem(&process_memory_map, &pid, &new_mem, BPF_ANY);
        mem = bpf_map_lookup_elem(&process_memory_map, &pid);
        if (!mem) return;
    }
    
    if (is_allocation) {
        mem->total_allocated += size_delta;
        mem->allocation_count++;
        mem->current_usage += size_delta;
        if (mem->current_usage > mem->peak_usage) {
            mem->peak_usage = mem->current_usage;
        }
    } else {
        mem->total_freed += size_delta;
        mem->free_count++;
        if (mem->current_usage >= size_delta) {
            mem->current_usage -= size_delta;
        }
    }
}

/* Trace malloc calls */
SEC("uprobe/malloc")
int trace_malloc(struct pt_regs *ctx) {
    __u64 size = PT_REGS_PARM1(ctx);
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || size == 0)
        return 0;
    
    send_memory_event(pid, 0, size, ALLOC_MALLOC, 0);
    return 0;
}

SEC("uretprobe/malloc")
int trace_malloc_ret(struct pt_regs *ctx) {
    __u64 addr = PT_REGS_RC(ctx);
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || addr == 0)
        return 0;
    
    // We need to correlate this with the size from the entry probe
    // For now, we'll store the allocation in a temporary map
    return 0;
}

/* Trace free calls */
SEC("uprobe/free")
int trace_free(struct pt_regs *ctx) {
    __u64 addr = PT_REGS_PARM1(ctx);
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || addr == 0)
        return 0;
    
    // Look up allocation info
    struct allocation_info *info = bpf_map_lookup_elem(&allocation_map, &addr);
    __u64 size = 0;
    if (info) {
        size = info->size;
        bpf_map_delete_elem(&allocation_map, &addr);
        update_process_memory(pid, size, 0);
    }
    
    send_memory_event(pid, addr, size, ALLOC_FREE, 0);
    return 0;
}

/* Trace mmap calls */
SEC("tp/syscalls/sys_enter_mmap")
int trace_mmap_enter(struct trace_event_raw_sys_enter *ctx) {
    __u64 size = ((__u64)ctx->args[1]);
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || size == 0)
        return 0;
    
    send_memory_event(pid, 0, size, ALLOC_MMAP, 0);
    return 0;
}

SEC("tp/syscalls/sys_exit_mmap")
int trace_mmap_exit(struct trace_event_raw_sys_exit *ctx) {
    __u64 addr = ctx->ret;
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || (__s64)addr < 0)
        return 0;
    
    // Store allocation info for future munmap
    struct allocation_info info = {};
    info.timestamp = bpf_ktime_get_ns();
    info.pid = pid;
    // info.size would need to be retrieved from entry
    
    bpf_map_update_elem(&allocation_map, &addr, &info, BPF_ANY);
    return 0;
}

/* Trace munmap calls */
SEC("tp/syscalls/sys_enter_munmap")
int trace_munmap(struct trace_event_raw_sys_enter *ctx) {
    __u64 addr = ctx->args[0];
    __u64 size = ctx->args[1];
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0 || addr == 0)
        return 0;
    
    struct allocation_info *info = bpf_map_lookup_elem(&allocation_map, &addr);
    if (info) {
        bpf_map_delete_elem(&allocation_map, &addr);
        update_process_memory(pid, size, 0);
    }
    
    send_memory_event(pid, addr, size, ALLOC_MUNMAP, 0);
    return 0;
}

/* Trace brk syscall */
SEC("tp/syscalls/sys_enter_brk")
int trace_brk(struct trace_event_raw_sys_enter *ctx) {
    __u64 addr = ctx->args[0];
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0)
        return 0;
    
    send_memory_event(pid, addr, 0, ALLOC_BRK, 0);
    return 0;
}

/* Trace page faults */
SEC("tp/exceptions/page_fault_user")
int trace_page_fault(struct trace_event_raw_page_fault_user *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u64 address = ctx->address;
    __u32 error_code = ctx->error_code;
    
    if (pid == 0)
        return 0;
    
    struct process_memory *mem = bpf_map_lookup_elem(&process_memory_map, &pid);
    if (!mem) {
        struct process_memory new_mem = {};
        bpf_map_update_elem(&process_memory_map, &pid, &new_mem, BPF_ANY);
        mem = bpf_map_lookup_elem(&process_memory_map, &pid);
        if (!mem) return 0;
    }
    
    mem->page_faults++;
    
    // Check if this is a major fault (page not in memory)
    if (error_code & 0x4) { // Major fault flag
        mem->major_faults++;
    }
    
    send_memory_event(pid, address, 4096, ALLOC_PAGE, 0);
    return 0;
}

/* Monitor memory pressure events */
SEC("tp/vmscan/mm_vmscan_wakeup_kswapd")
int trace_memory_pressure(void *ctx) {
    __u32 key = 0;
    struct system_memory *sys_mem = bpf_map_lookup_elem(&system_memory_map, &key);
    if (sys_mem) {
        sys_mem->memory_pressure++;
    }
    return 0;
}

/* Trace OOM killer events */
SEC("tp/oom/mark_victim")
int trace_oom_victim(struct trace_event_raw_mark_victim *ctx) {
    __u32 pid = ctx->pid;
    
    // Send OOM event
    send_memory_event(pid, 0, 0, 0xFF, 0); // Special type for OOM
    return 0;
}

/* Sample memory statistics periodically */
SEC("perf_event")
int sample_memory_stats(struct bpf_perf_event_data *ctx) {
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    if (pid == 0)
        return 0;
    
    // Read memory statistics from task struct
    struct mm_struct *mm;
    BPF_CORE_READ_INTO(&mm, task, mm);
    
    if (!mm)
        return 0;
    
    struct process_memory *mem = bpf_map_lookup_elem(&process_memory_map, &pid);
    if (!mem) {
        struct process_memory new_mem = {};
        bpf_map_update_elem(&process_memory_map, &pid, &new_mem, BPF_ANY);
        mem = bpf_map_lookup_elem(&process_memory_map, &pid);
        if (!mem) return 0;
    }
    
    // Update RSS and virtual memory statistics
    __u64 rss_pages, vmem_pages;
    BPF_CORE_READ_INTO(&rss_pages, mm, rss_stat.count[0].counter);
    BPF_CORE_READ_INTO(&vmem_pages, mm, total_vm);
    
    mem->rss_pages = rss_pages;
    mem->vmem_pages = vmem_pages;
    
    return 0;
}

/* Kprobe for detailed allocation tracking */
SEC("kprobe/__alloc_pages")
int BPF_KPROBE(__alloc_pages, gfp_t gfp_mask, unsigned int order) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u64 size = (1ULL << order) * 4096; // Pages to bytes
    
    if (pid == 0)
        return 0;
    
    update_process_memory(pid, size, 1);
    send_memory_event(pid, 0, size, ALLOC_PAGE, 0);
    return 0;
}

SEC("kprobe/__free_pages")
int BPF_KPROBE(__free_pages, struct page *page, unsigned int order) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    __u64 size = (1ULL << order) * 4096; // Pages to bytes
    
    if (pid == 0)
        return 0;
    
    update_process_memory(pid, size, 0);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
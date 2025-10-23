// Memory Tracker Userspace Agent
// Collects and processes memory allocation data from eBPF probe

package main

import (
    "bytes"
    "context"
    "encoding/binary"
    "fmt"
    "log"
    "os"
    "os/signal"
    "sort"
    "syscall"
    "time"
    "unsafe"

    "github.com/cilium/ebpf"
    "github.com/cilium/ebpf/link"
    "github.com/cilium/ebpf/ringbuf"
    "github.com/cilium/ebpf/rlimit"
)

// Memory allocation types
const (
    AllocMalloc = 1
    AllocCalloc = 2
    AllocRealloc = 3
    AllocFree = 4
    AllocMmap = 5
    AllocMunmap = 6
    AllocBrk = 7
    AllocPage = 8
    AllocOOM = 0xFF
)

var allocTypeNames = map[uint32]string{
    AllocMalloc:  "malloc",
    AllocCalloc:  "calloc", 
    AllocRealloc: "realloc",
    AllocFree:    "free",
    AllocMmap:    "mmap",
    AllocMunmap:  "munmap",
    AllocBrk:     "brk",
    AllocPage:    "page",
    AllocOOM:     "oom",
}

// Data structures matching eBPF program
type MemoryEvent struct {
    Timestamp uint64
    PID       uint32
    TID       uint32
    Addr      uint64
    Size      uint64
    OldAddr   uint64
    Type      uint32
    Flags     uint32
    StackID   uint64
    Comm      [16]int8
}

type ProcessMemory struct {
    TotalAllocated  uint64
    TotalFreed      uint64
    CurrentUsage    uint64
    PeakUsage       uint64
    AllocationCount uint64
    FreeCount       uint64
    PageFaults      uint64
    MajorFaults     uint64
    RSSPages        uint64
    VMemPages       uint64
}

type SystemMemory struct {
    TotalMemory     uint64
    FreeMemory      uint64
    AvailableMemory uint64
    CachedMemory    uint64
    BufferMemory    uint64
    SlabMemory      uint64
    PageCacheSize   uint64
    MemoryPressure  uint32
}

type AllocationInfo struct {
    Size      uint64
    Timestamp uint64
    StackID   uint64
    PID       uint32
}

type MemoryTracker struct {
    spec        *ebpf.CollectionSpec
    coll        *ebpf.Collection
    eventReader *ringbuf.Reader
    links       []link.Link
    
    // Statistics
    totalEvents       uint64
    allocationEvents  uint64
    freeEvents        uint64
    pageEvents        uint64
    oomEvents         uint64
    processStats      map[uint32]*ProcessMemory
    leaks             map[uint64]*AllocationInfo
    startTime         time.Time
}

func NewMemoryTracker() (*MemoryTracker, error) {
    if err := rlimit.RemoveMemlock(); err != nil {
        return nil, fmt.Errorf("failed to remove memlock: %v", err)
    }

    tracker := &MemoryTracker{
        processStats: make(map[uint32]*ProcessMemory),
        leaks:        make(map[uint64]*AllocationInfo),
        startTime:    time.Now(),
    }

    return tracker, nil
}

func (mt *MemoryTracker) Load() error {
    spec, err := ebpf.LoadCollectionSpec("memory_tracker.o")
    if err != nil {
        return fmt.Errorf("failed to load eBPF spec: %v", err)
    }
    mt.spec = spec

    coll, err := ebpf.NewCollection(spec)
    if err != nil {
        return fmt.Errorf("failed to create eBPF collection: %v", err)
    }
    mt.coll = coll

    // Create event reader
    reader, err := ringbuf.NewReader(coll.Maps["events"])
    if err != nil {
        return fmt.Errorf("failed to create ring buffer reader: %v", err)
    }
    mt.eventReader = reader

    return nil
}

func (mt *MemoryTracker) Attach() error {
    // Attach tracepoints
    tracepoints := []struct {
        group string
        name  string
        prog  string
    }{
        {"syscalls", "sys_enter_mmap", "trace_mmap_enter"},
        {"syscalls", "sys_exit_mmap", "trace_mmap_exit"},
        {"syscalls", "sys_enter_munmap", "trace_munmap"},
        {"syscalls", "sys_enter_brk", "trace_brk"},
        {"exceptions", "page_fault_user", "trace_page_fault"},
        {"vmscan", "mm_vmscan_wakeup_kswapd", "trace_memory_pressure"},
        {"oom", "mark_victim", "trace_oom_victim"},
    }
    
    for _, tp := range tracepoints {
        l, err := link.Tracepoint(link.TracepointOptions{
            Group:   tp.group,
            Name:    tp.name,
            Program: mt.coll.Programs[tp.prog],
        })
        if err != nil {
            log.Printf("Warning: failed to attach tracepoint %s:%s: %v", tp.group, tp.name, err)
            continue
        }
        mt.links = append(mt.links, l)
    }

    // Attach kprobes for kernel allocation tracking
    kprobes := []struct {
        symbol string
        prog   string
    }{
        {"__alloc_pages", "__alloc_pages"},
        {"__free_pages", "__free_pages"},
    }
    
    for _, kp := range kprobes {
        l, err := link.Kprobe(link.KprobeOptions{
            Symbol:  kp.symbol,
            Program: mt.coll.Programs[kp.prog],
        })
        if err != nil {
            log.Printf("Warning: failed to attach kprobe %s: %v", kp.symbol, err)
            continue
        }
        mt.links = append(mt.links, l)
    }

    // Try to attach uprobes for malloc/free tracking
    // Note: This requires the binary path and may fail in some environments
    mt.attachUprobes()

    log.Printf("Attached %d eBPF programs", len(mt.links))
    return nil
}

func (mt *MemoryTracker) attachUprobes() {
    // Common libc paths to try
    libcPaths := []string{
        "/lib/x86_64-linux-gnu/libc.so.6",
        "/usr/lib/x86_64-linux-gnu/libc.so.6",
        "/lib64/libc.so.6",
        "/usr/lib64/libc.so.6",
    }
    
    functions := []string{"malloc", "free"}
    
    for _, libcPath := range libcPaths {
        if _, err := os.Stat(libcPath); err != nil {
            continue
        }
        
        for _, funcName := range functions {
            // Attach uprobe
            l, err := link.Uprobe(link.UprobeOptions{
                Path:    libcPath,
                Symbol:  funcName,
                Program: mt.coll.Programs["trace_"+funcName],
            })
            if err != nil {
                log.Printf("Warning: failed to attach uprobe %s:%s: %v", libcPath, funcName, err)
                continue
            }
            mt.links = append(mt.links, l)
            
            // Attach uretprobe for malloc
            if funcName == "malloc" {
                l, err := link.Uprobe(link.UprobeOptions{
                    Path:       libcPath,
                    Symbol:     funcName,
                    Program:    mt.coll.Programs["trace_malloc_ret"],
                    ReturnProbe: true,
                })
                if err != nil {
                    log.Printf("Warning: failed to attach uretprobe %s:%s: %v", libcPath, funcName, err)
                    continue
                }
                mt.links = append(mt.links, l)
            }
        }
        break // Use first available libc
    }
}

func (mt *MemoryTracker) processEvent(record ringbuf.Record) error {
    if len(record.RawSample) < int(unsafe.Sizeof(MemoryEvent{})) {
        return fmt.Errorf("invalid sample size")
    }

    var event MemoryEvent
    err := binary.Read(bytes.NewReader(record.RawSample), binary.LittleEndian, &event)
    if err != nil {
        return fmt.Errorf("failed to parse event: %v", err)
    }

    mt.totalEvents++
    
    // Convert C string to Go string
    comm := make([]byte, 0, 16)
    for _, c := range event.Comm {
        if c == 0 {
            break
        }
        comm = append(comm, byte(c))
    }
    
    // Update statistics based on event type
    switch event.Type {
    case AllocMalloc, AllocMmap, AllocBrk, AllocPage:
        mt.allocationEvents++
        mt.trackAllocation(event.PID, event.Addr, event.Size)
    case AllocFree, AllocMunmap:
        mt.freeEvents++
        mt.trackDeallocation(event.PID, event.Addr, event.Size)
    case AllocOOM:
        mt.oomEvents++
        log.Printf("OOM event detected for PID %d (%s)", event.PID, string(comm))
    }
    
    // Print interesting events
    if event.Size > 1024*1024 || event.Type == AllocOOM { // Large allocations or OOM
        typeName, ok := allocTypeNames[event.Type]
        if !ok {
            typeName = fmt.Sprintf("unknown(%d)", event.Type)
        }
        
        fmt.Printf("Memory Event: PID=%d, Type=%s, Addr=0x%x, Size=%d, Comm=%s\n",
            event.PID, typeName, event.Addr, event.Size, string(comm))
    }

    return nil
}

func (mt *MemoryTracker) trackAllocation(pid uint32, addr, size uint64) {
    if addr == 0 {
        return
    }
    
    // Track potential leaks
    mt.leaks[addr] = &AllocationInfo{
        Size:      size,
        Timestamp: time.Now().UnixNano(),
        PID:       pid,
    }
    
    // Update process statistics
    if _, exists := mt.processStats[pid]; !exists {
        mt.processStats[pid] = &ProcessMemory{}
    }
    
    stats := mt.processStats[pid]
    stats.TotalAllocated += size
    stats.AllocationCount++
    stats.CurrentUsage += size
    
    if stats.CurrentUsage > stats.PeakUsage {
        stats.PeakUsage = stats.CurrentUsage
    }
}

func (mt *MemoryTracker) trackDeallocation(pid uint32, addr, size uint64) {
    if addr == 0 {
        return
    }
    
    // Remove from leak tracking
    if _, exists := mt.leaks[addr]; exists {
        delete(mt.leaks, addr)
    }
    
    // Update process statistics
    if stats, exists := mt.processStats[pid]; exists {
        stats.TotalFreed += size
        stats.FreeCount++
        if stats.CurrentUsage >= size {
            stats.CurrentUsage -= size
        }
    }
}

func (mt *MemoryTracker) Run(ctx context.Context) error {
    fmt.Println("Starting memory tracker...")

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            record, err := mt.eventReader.Read()
            if err != nil {
                if err == ringbuf.ErrClosed {
                    return nil
                }
                log.Printf("Error reading from ring buffer: %v", err)
                continue
            }

            if err := mt.processEvent(record); err != nil {
                log.Printf("Error processing event: %v", err)
            }
        }
    }
}

func (mt *MemoryTracker) PrintStats() {
    fmt.Printf("\n=== Memory Tracker Statistics ===\n")
    fmt.Printf("Runtime: %v\n", time.Since(mt.startTime))
    fmt.Printf("Total events: %d\n", mt.totalEvents)
    fmt.Printf("Allocation events: %d\n", mt.allocationEvents)
    fmt.Printf("Free events: %d\n", mt.freeEvents)
    fmt.Printf("Page fault events: %d\n", mt.pageEvents)
    fmt.Printf("OOM events: %d\n", mt.oomEvents)
    fmt.Printf("Tracked processes: %d\n", len(mt.processStats))
    fmt.Printf("Potential leaks: %d\n", len(mt.leaks))

    // Top memory consumers
    fmt.Printf("\nTop 10 memory consumers:\n")
    type processInfo struct {
        pid     uint32
        current uint64
        peak    uint64
        allocs  uint64
    }
    
    var processes []processInfo
    for pid, stats := range mt.processStats {
        processes = append(processes, processInfo{
            pid:     pid,
            current: stats.CurrentUsage,
            peak:    stats.PeakUsage,
            allocs:  stats.AllocationCount,
        })
    }
    
    sort.Slice(processes, func(i, j int) bool {
        return processes[i].current > processes[j].current
    })
    
    count := len(processes)
    if count > 10 {
        count = 10
    }
    
    for i := 0; i < count; i++ {
        p := processes[i]
        fmt.Printf("  PID %d: Current=%s, Peak=%s, Allocs=%d\n", 
            p.pid, formatBytes(p.current), formatBytes(p.peak), p.allocs)
    }
    
    // Memory leaks
    if len(mt.leaks) > 0 {
        fmt.Printf("\nPotential memory leaks (top 10):\n")
        type leakInfo struct {
            addr uint64
            size uint64
            age  time.Duration
            pid  uint32
        }
        
        var leaks []leakInfo
        now := time.Now().UnixNano()
        for addr, info := range mt.leaks {
            leaks = append(leaks, leakInfo{
                addr: addr,
                size: info.Size,
                age:  time.Duration(now - info.Timestamp),
                pid:  info.PID,
            })
        }
        
        sort.Slice(leaks, func(i, j int) bool {
            return leaks[i].size > leaks[j].size
        })
        
        leakCount := len(leaks)
        if leakCount > 10 {
            leakCount = 10
        }
        
        for i := 0; i < leakCount; i++ {
            l := leaks[i]
            fmt.Printf("  Addr=0x%x, Size=%s, Age=%v, PID=%d\n",
                l.addr, formatBytes(l.size), l.age.Truncate(time.Second), l.pid)
        }
    }
    
    // Read current memory statistics from maps
    mt.readMemoryMaps()
}

func (mt *MemoryTracker) readMemoryMaps() {
    processMap := mt.coll.Maps["process_memory_map"]
    
    fmt.Printf("\nProcess Memory Map (from eBPF):\n")
    var key uint32
    var stats ProcessMemory
    iter := processMap.Iterate()
    
    count := 0
    for iter.Next(&key, &stats) && count < 5 {
        fmt.Printf("  PID %d: Alloc=%s, Free=%s, Current=%s, Peak=%s\n",
            key, 
            formatBytes(stats.TotalAllocated),
            formatBytes(stats.TotalFreed),
            formatBytes(stats.CurrentUsage),
            formatBytes(stats.PeakUsage))
        count++
    }
}

func formatBytes(bytes uint64) string {
    const unit = 1024
    if bytes < unit {
        return fmt.Sprintf("%dB", bytes)
    }
    div, exp := int64(unit), 0
    for n := bytes / unit; n >= unit; n /= unit {
        div *= unit
        exp++
    }
    return fmt.Sprintf("%.1f%cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}

func (mt *MemoryTracker) Close() error {
    if mt.eventReader != nil {
        mt.eventReader.Close()
    }

    for _, l := range mt.links {
        l.Close()
    }

    if mt.coll != nil {
        mt.coll.Close()
    }

    return nil
}

func main() {
    tracker, err := NewMemoryTracker()
    if err != nil {
        log.Fatalf("Failed to create memory tracker: %v", err)
    }
    defer tracker.Close()

    if err := tracker.Load(); err != nil {
        log.Fatalf("Failed to load eBPF program: %v", err)
    }

    if err := tracker.Attach(); err != nil {
        log.Fatalf("Failed to attach eBPF programs: %v", err)
    }

    // Handle interrupts gracefully
    ctx, cancel := context.WithCancel(context.Background())
    sigChan := make(chan os.Signal, 1)
    signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

    go func() {
        <-sigChan
        log.Println("Received interrupt signal, shutting down...")
        cancel()
    }()

    // Start stats printer goroutine
    go func() {
        ticker := time.NewTicker(15 * time.Second)
        defer ticker.Stop()
        
        for {
            select {
            case <-ctx.Done():
                return
            case <-ticker.C:
                tracker.PrintStats()
            }
        }
    }()

    // Run the tracker
    if err := tracker.Run(ctx); err != nil && err != context.Canceled {
        log.Fatalf("Memory tracker error: %v", err)
    }

    // Print final statistics
    tracker.PrintStats()
    log.Println("Memory tracker stopped")
}
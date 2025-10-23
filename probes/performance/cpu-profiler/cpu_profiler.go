// CPU Profiler Userspace Agent
// Collects and processes CPU performance data from eBPF probe

package main

import (
    "bytes"
    "context"
    "encoding/binary"
    "fmt"
    "log"
    "os"
    "os/signal"
    "syscall"
    "time"
    "unsafe"

    "github.com/cilium/ebpf"
    "github.com/cilium/ebpf/link"
    "github.com/cilium/ebpf/perf"
    "github.com/cilium/ebpf/ringbuf"
    "github.com/cilium/ebpf/rlimit"
)

// Data structures matching eBPF program
type CPUSample struct {
    Timestamp uint64
    PID       uint32
    CPU       uint32
    Runtime   uint64
    VRuntime  uint64
    Priority  uint32
    Weight    uint32
    Comm      [16]int8
}

type ProcessStats struct {
    TotalRuntime        uint64
    ScheduleCount       uint64
    VoluntarySwitches   uint64
    InvoluntarySwitches uint64
    LastSeen            uint64
    MinCPU              uint32
    MaxCPU              uint32
}

type CPUStats struct {
    IdleTime       uint64
    UserTime       uint64
    SystemTime     uint64
    IRQTime        uint64
    SoftIRQTime    uint64
    ContextSwitches uint64
    Frequency      uint32
    LoadAvg        uint32
}

type CPUProfiler struct {
    spec        *ebpf.CollectionSpec
    coll        *ebpf.Collection
    eventReader *ringbuf.Reader
    links       []link.Link
    
    // Statistics
    totalSamples uint64
    processStats map[uint32]*ProcessStats
    cpuStats     map[uint32]*CPUStats
    startTime    time.Time
}

func NewCPUProfiler() (*CPUProfiler, error) {
    if err := rlimit.RemoveMemlock(); err != nil {
        return nil, fmt.Errorf("failed to remove memlock: %v", err)
    }

    profiler := &CPUProfiler{
        processStats: make(map[uint32]*ProcessStats),
        cpuStats:     make(map[uint32]*CPUStats),
        startTime:    time.Now(),
    }

    return profiler, nil
}

func (cp *CPUProfiler) Load() error {
    spec, err := ebpf.LoadCollectionSpec("cpu_profiler.o")
    if err != nil {
        return fmt.Errorf("failed to load eBPF spec: %v", err)
    }
    cp.spec = spec

    coll, err := ebpf.NewCollection(spec)
    if err != nil {
        return fmt.Errorf("failed to create eBPF collection: %v", err)
    }
    cp.coll = coll

    // Create event reader
    reader, err := ringbuf.NewReader(coll.Maps["events"])
    if err != nil {
        return fmt.Errorf("failed to create ring buffer reader: %v", err)
    }
    cp.eventReader = reader

    return nil
}

func (cp *CPUProfiler) Attach() error {
    var err error
    
    // Attach tracepoints
    tracepoints := []string{
        "sched_switch",
        "sched_wakeup", 
        "cpu_frequency",
        "cpu_idle",
        "irq_handler_entry",
        "softirq_entry",
    }
    
    for _, tp := range tracepoints {
        var group, name string
        switch tp {
        case "sched_switch", "sched_wakeup":
            group, name = "sched", tp
        case "cpu_frequency", "cpu_idle":
            group, name = "power", tp
        case "irq_handler_entry", "softirq_entry":
            group, name = "irq", tp
        }
        
        l, err := link.Tracepoint(link.TracepointOptions{
            Group:   group,
            Name:    name,
            Program: cp.coll.Programs["trace_"+tp],
        })
        if err != nil {
            log.Printf("Warning: failed to attach tracepoint %s: %v", tp, err)
            continue
        }
        cp.links = append(cp.links, l)
    }

    // Attach kprobe
    kprobeLink, err := link.Kprobe(link.KprobeOptions{
        Symbol:  "finish_task_switch",
        Program: cp.coll.Programs["finish_task_switch"],
    })
    if err != nil {
        log.Printf("Warning: failed to attach kprobe: %v", err)
    } else {
        cp.links = append(cp.links, kprobeLink)
    }

    // Attach perf event for CPU sampling
    perfLink, err := link.AttachPerfEvent(link.PerfEventOptions{
        Type:    perf.TypeSoftware,
        Config:  perf.ConfigSoftwareCPUClock,
        Program: cp.coll.Programs["sample_cpu_perf"],
        SampleFreq: 99, // 99Hz sampling
    })
    if err != nil {
        log.Printf("Warning: failed to attach perf event: %v", err)
    } else {
        cp.links = append(cp.links, perfLink)
    }

    log.Printf("Attached %d eBPF programs", len(cp.links))
    return nil
}

func (cp *CPUProfiler) processEvent(record ringbuf.Record) error {
    if len(record.RawSample) < int(unsafe.Sizeof(CPUSample{})) {
        return fmt.Errorf("invalid sample size")
    }

    var sample CPUSample
    err := binary.Read(bytes.NewReader(record.RawSample), binary.LittleEndian, &sample)
    if err != nil {
        return fmt.Errorf("failed to parse sample: %v", err)
    }

    cp.totalSamples++
    
    // Convert C string to Go string
    comm := make([]byte, 0, 16)
    for _, c := range sample.Comm {
        if c == 0 {
            break
        }
        comm = append(comm, byte(c))
    }
    
    // Update process statistics
    if _, exists := cp.processStats[sample.PID]; !exists {
        cp.processStats[sample.PID] = &ProcessStats{}
    }
    
    stats := cp.processStats[sample.PID]
    stats.TotalRuntime += sample.Runtime
    stats.ScheduleCount++
    stats.LastSeen = sample.Timestamp
    
    if stats.MinCPU == 0 || sample.CPU < stats.MinCPU {
        stats.MinCPU = sample.CPU
    }
    if sample.CPU > stats.MaxCPU {
        stats.MaxCPU = sample.CPU
    }

    // Print sample information
    fmt.Printf("CPU Sample: PID=%d, CPU=%d, Comm=%s, Runtime=%d, VRuntime=%d, Prio=%d\n",
        sample.PID, sample.CPU, string(comm), sample.Runtime, sample.VRuntime, sample.Priority)

    return nil
}

func (cp *CPUProfiler) Run(ctx context.Context) error {
    fmt.Println("Starting CPU profiler...")

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            record, err := cp.eventReader.Read()
            if err != nil {
                if err == ringbuf.ErrClosed {
                    return nil
                }
                log.Printf("Error reading from ring buffer: %v", err)
                continue
            }

            if err := cp.processEvent(record); err != nil {
                log.Printf("Error processing event: %v", err)
            }
        }
    }
}

func (cp *CPUProfiler) PrintStats() {
    fmt.Printf("\n=== CPU Profiler Statistics ===\n")
    fmt.Printf("Runtime: %v\n", time.Since(cp.startTime))
    fmt.Printf("Total samples: %d\n", cp.totalSamples)
    fmt.Printf("Tracked processes: %d\n", len(cp.processStats))

    fmt.Printf("\nTop 10 processes by runtime:\n")
    type processInfo struct {
        pid     uint32
        runtime uint64
        count   uint64
    }
    
    var processes []processInfo
    for pid, stats := range cp.processStats {
        processes = append(processes, processInfo{
            pid:     pid,
            runtime: stats.TotalRuntime,
            count:   stats.ScheduleCount,
        })
    }
    
    // Simple bubble sort for top 10
    for i := 0; i < len(processes)-1; i++ {
        for j := 0; j < len(processes)-i-1; j++ {
            if processes[j].runtime < processes[j+1].runtime {
                processes[j], processes[j+1] = processes[j+1], processes[j]
            }
        }
    }
    
    count := len(processes)
    if count > 10 {
        count = 10
    }
    
    for i := 0; i < count; i++ {
        p := processes[i]
        fmt.Printf("  PID %d: Runtime=%d, Schedules=%d\n", 
            p.pid, p.runtime, p.count)
    }
    
    // Read current CPU statistics from maps
    fmt.Printf("\nCPU Statistics:\n")
    cp.readCPUStats()
}

func (cp *CPUProfiler) readCPUStats() {
    processMap := cp.coll.Maps["process_map"]
    cpuMap := cp.coll.Maps["cpu_map"]
    
    // Iterate through process map
    var key uint32
    var stats ProcessStats
    iter := processMap.Iterate()
    
    fmt.Printf("Process Map Contents:\n")
    count := 0
    for iter.Next(&key, &stats) && count < 5 {
        fmt.Printf("  PID %d: Runtime=%d, Schedules=%d, Vol/Invol=%d/%d\n",
            key, stats.TotalRuntime, stats.ScheduleCount,
            stats.VoluntarySwitches, stats.InvoluntarySwitches)
        count++
    }
    
    // Read CPU map for a few CPUs
    fmt.Printf("CPU Map Contents:\n")
    for i := uint32(0); i < 4; i++ { // Check first 4 CPUs
        var cpuStats CPUStats
        err := cpuMap.Lookup(i, &cpuStats)
        if err == nil && cpuStats.ContextSwitches > 0 {
            fmt.Printf("  CPU %d: CtxSwitches=%d, IRQ=%d, SoftIRQ=%d, Freq=%dMHz\n",
                i, cpuStats.ContextSwitches, cpuStats.IRQTime, 
                cpuStats.SoftIRQTime, cpuStats.Frequency/1000)
        }
    }
}

func (cp *CPUProfiler) Close() error {
    if cp.eventReader != nil {
        cp.eventReader.Close()
    }

    for _, l := range cp.links {
        l.Close()
    }

    if cp.coll != nil {
        cp.coll.Close()
    }

    return nil
}

func main() {
    profiler, err := NewCPUProfiler()
    if err != nil {
        log.Fatalf("Failed to create CPU profiler: %v", err)
    }
    defer profiler.Close()

    if err := profiler.Load(); err != nil {
        log.Fatalf("Failed to load eBPF program: %v", err)
    }

    if err := profiler.Attach(); err != nil {
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
        ticker := time.NewTicker(10 * time.Second)
        defer ticker.Stop()
        
        for {
            select {
            case <-ctx.Done():
                return
            case <-ticker.C:
                profiler.PrintStats()
            }
        }
    }()

    // Run the profiler
    if err := profiler.Run(ctx); err != nil && err != context.Canceled {
        log.Fatalf("CPU profiler error: %v", err)
    }

    // Print final statistics
    profiler.PrintStats()
    log.Println("CPU profiler stopped")
}
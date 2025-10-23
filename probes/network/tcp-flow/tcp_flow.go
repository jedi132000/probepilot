package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
	"unsafe"

	"github.com/cilium/ebpf"
	"github.com/cilium/ebpf/link"
	"github.com/cilium/ebpf/ringbuf"
	"github.com/cilium/ebpf/rlimit"
)

// TCPEvent represents a TCP event from the eBPF program
type TCPEvent struct {
	Timestamp uint64
	PID       uint32
	SAddr     uint32
	DAddr     uint32
	SPort     uint16
	DPort     uint16
	Bytes     uint32
	RTT       uint32
	EventType uint8
	Comm      [16]byte
}

// FlowKey represents a network flow identifier
type FlowKey struct {
	SAddr    uint32
	DAddr    uint32
	SPort    uint16
	DPort    uint16
	Protocol uint8
}

// FlowData represents flow statistics
type FlowData struct {
	BytesTX    uint64
	BytesRX    uint64
	PacketsTX  uint64
	PacketsRX  uint64
	FirstSeen  uint64
	LastSeen   uint64
	RTTSamples uint32
	RTTTotal   uint32
	State      uint8
}

// TCPFlowMonitor represents the TCP flow monitoring probe
type TCPFlowMonitor struct {
	spec     *ebpf.CollectionSpec
	coll     *ebpf.Collection
	links    []link.Link
	reader   *ringbuf.Reader
	config   Config
	flows    map[FlowKey]*FlowData
	stats    ProbeStats
}

// Config holds probe configuration
type Config struct {
	SamplingRate uint32
	MaxFlows     uint32
	ReportInterval time.Duration
	FilterPorts  []uint16
	FilterIPs    []string
}

// ProbeStats holds probe statistics
type ProbeStats struct {
	EventsProcessed uint64
	ActiveFlows     uint64
	TotalConnections uint64
	TotalBytes      uint64
	StartTime       time.Time
}

// NewTCPFlowMonitor creates a new TCP flow monitor instance
func NewTCPFlowMonitor(config Config) (*TCPFlowMonitor, error) {
	// Remove memory limit for eBPF
	if err := rlimit.RemoveMemlock(); err != nil {
		return nil, fmt.Errorf("failed to remove memlock: %w", err)
	}

	// Load pre-compiled eBPF program
	spec, err := ebpf.LoadCollectionSpec("tcp_flow.o")
	if err != nil {
		return nil, fmt.Errorf("failed to load eBPF spec: %w", err)
	}

	// Load eBPF program into kernel
	coll, err := ebpf.NewCollection(spec)
	if err != nil {
		return nil, fmt.Errorf("failed to create eBPF collection: %w", err)
	}

	monitor := &TCPFlowMonitor{
		spec:   spec,
		coll:   coll,
		config: config,
		flows:  make(map[FlowKey]*FlowData),
		stats: ProbeStats{
			StartTime: time.Now(),
		},
	}

	return monitor, nil
}

// Start begins monitoring TCP flows
func (m *TCPFlowMonitor) Start(ctx context.Context) error {
	// Attach to tracepoints and kprobes
	if err := m.attachProbes(); err != nil {
		return fmt.Errorf("failed to attach probes: %w", err)
	}

	// Set up ring buffer reader
	reader, err := ringbuf.NewReader(m.coll.Maps["events"])
	if err != nil {
		return fmt.Errorf("failed to create ring buffer reader: %w", err)
	}
	m.reader = reader

	// Start event processing goroutine
	go m.processEvents(ctx)

	// Start periodic reporting
	go m.periodicReport(ctx)

	log.Printf("TCP Flow Monitor started successfully")
	log.Printf("Monitoring configuration: sampling_rate=%d, max_flows=%d",
		m.config.SamplingRate, m.config.MaxFlows)

	return nil
}

// Stop stops the TCP flow monitor
func (m *TCPFlowMonitor) Stop() error {
	// Close ring buffer reader
	if m.reader != nil {
		m.reader.Close()
	}

	// Detach all probes
	for _, l := range m.links {
		l.Close()
	}

	// Close eBPF collection
	if m.coll != nil {
		m.coll.Close()
	}

	log.Printf("TCP Flow Monitor stopped")
	return nil
}

// attachProbes attaches eBPF programs to kernel hooks
func (m *TCPFlowMonitor) attachProbes() error {
	var links []link.Link

	// Attach to inet_sock_set_state tracepoint
	l1, err := link.Tracepoint(link.TracepointOptions{
		Group:   "sock",
		Name:    "inet_sock_set_state",
		Program: m.coll.Programs["trace_tcp_state_change"],
	})
	if err != nil {
		return fmt.Errorf("failed to attach inet_sock_set_state: %w", err)
	}
	links = append(links, l1)

	// Attach to tcp_probe tracepoint
	l2, err := link.Tracepoint(link.TracepointOptions{
		Group:   "tcp",
		Name:    "tcp_probe",
		Program: m.coll.Programs["trace_tcp_probe"],
	})
	if err != nil {
		log.Printf("Warning: failed to attach tcp_probe (may not be available): %v", err)
	} else {
		links = append(links, l2)
	}

	// Attach to tcp_retransmit_skb tracepoint
	l3, err := link.Tracepoint(link.TracepointOptions{
		Group:   "tcp",
		Name:    "tcp_retransmit_skb",
		Program: m.coll.Programs["trace_tcp_retransmit"],
	})
	if err != nil {
		log.Printf("Warning: failed to attach tcp_retransmit_skb: %v", err)
	} else {
		links = append(links, l3)
	}

	// Attach kprobes
	l4, err := link.Kprobe(link.KprobeOptions{
		Symbol:  "tcp_sendmsg",
		Program: m.coll.Programs["tcp_sendmsg"],
	})
	if err != nil {
		log.Printf("Warning: failed to attach tcp_sendmsg kprobe: %v", err)
	} else {
		links = append(links, l4)
	}

	l5, err := link.Kprobe(link.KprobeOptions{
		Symbol:  "tcp_cleanup_rbuf",
		Program: m.coll.Programs["tcp_cleanup_rbuf"],
	})
	if err != nil {
		log.Printf("Warning: failed to attach tcp_cleanup_rbuf kprobe: %v", err)
	} else {
		links = append(links, l5)
	}

	m.links = links
	log.Printf("Attached %d eBPF probes successfully", len(links))
	return nil
}

// processEvents processes events from the eBPF ring buffer
func (m *TCPFlowMonitor) processEvents(ctx context.Context) {
	for {
		select {
		case <-ctx.Done():
			return
		default:
			record, err := m.reader.Read()
			if err != nil {
				if err == ringbuf.ErrClosed {
					return
				}
				log.Printf("Error reading from ring buffer: %v", err)
				continue
			}

			if len(record.RawSample) < int(unsafe.Sizeof(TCPEvent{})) {
				continue
			}

			var event TCPEvent
			err = binary.Read(bytes.NewReader(record.RawSample), binary.LittleEndian, &event)
			if err != nil {
				log.Printf("Error parsing event: %v", err)
				continue
			}

			m.handleEvent(&event)
			m.stats.EventsProcessed++
		}
	}
}

// handleEvent processes a single TCP event
func (m *TCPFlowMonitor) handleEvent(event *TCPEvent) {
	// Convert to human-readable format
	srcIP := intToIP(event.SAddr)
	dstIP := intToIP(event.DAddr)
	comm := string(bytes.TrimRight(event.Comm[:], "\x00"))
	
	timestamp := time.Unix(0, int64(event.Timestamp))
	
	switch event.EventType {
	case 1: // Connect
		log.Printf("[CONNECT] %s %s:%d -> %s:%d (PID: %d)",
			timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort, event.PID)
		m.stats.TotalConnections++
		
	case 2: // Accept
		log.Printf("[ACCEPT] %s %s:%d <- %s:%d (PID: %d)",
			timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort, event.PID)
		m.stats.TotalConnections++
		
	case 3: // Send
		if event.Bytes > 0 {
			log.Printf("[SEND] %s %s:%d -> %s:%d %d bytes (RTT: %dms, %s)",
				timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort,
				event.Bytes, event.RTT/8000, comm) // Convert srtt to milliseconds
			m.stats.TotalBytes += uint64(event.Bytes)
		}
		
	case 4: // Receive
		if event.Bytes > 0 {
			log.Printf("[RECV] %s %s:%d <- %s:%d %d bytes (%s)",
				timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort,
				event.Bytes, comm)
			m.stats.TotalBytes += uint64(event.Bytes)
		}
		
	case 5: // Close
		log.Printf("[CLOSE] %s %s:%d <-> %s:%d (PID: %d)",
			timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort, event.PID)
		
	case 6: // Retransmit
		log.Printf("[RETX] %s %s:%d -> %s:%d (%s)",
			timestamp.Format("15:04:05.000"), srcIP, event.SPort, dstIP, event.DPort, comm)
	}

	// Update flow statistics
	m.updateFlowStats(event)
}

// updateFlowStats updates flow statistics
func (m *TCPFlowMonitor) updateFlowStats(event *TCPEvent) {
	key := FlowKey{
		SAddr:    event.SAddr,
		DAddr:    event.DAddr,
		SPort:    event.SPort,
		DPort:    event.DPort,
		Protocol: 6, // TCP
	}

	flow, exists := m.flows[key]
	if !exists {
		flow = &FlowData{
			FirstSeen: event.Timestamp,
		}
		m.flows[key] = flow
	}

	flow.LastSeen = event.Timestamp

	switch event.EventType {
	case 3: // Send
		flow.BytesTX += uint64(event.Bytes)
		flow.PacketsTX++
	case 4: // Receive
		flow.BytesRX += uint64(event.Bytes)
		flow.PacketsRX++
	}

	if event.RTT > 0 {
		flow.RTTSamples++
		flow.RTTTotal += event.RTT
	}
}

// periodicReport prints periodic statistics
func (m *TCPFlowMonitor) periodicReport(ctx context.Context) {
	ticker := time.NewTicker(m.config.ReportInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			m.printStats()
		}
	}
}

// printStats prints current statistics
func (m *TCPFlowMonitor) printStats() {
	uptime := time.Since(m.stats.StartTime)
	activeFlows := len(m.flows)
	
	log.Printf("=== TCP Flow Monitor Stats ===")
	log.Printf("Uptime: %v", uptime.Truncate(time.Second))
	log.Printf("Events processed: %d", m.stats.EventsProcessed)
	log.Printf("Active flows: %d", activeFlows)
	log.Printf("Total connections: %d", m.stats.TotalConnections)
	log.Printf("Total bytes: %.2f MB", float64(m.stats.TotalBytes)/(1024*1024))
	
	if m.stats.EventsProcessed > 0 {
		rate := float64(m.stats.EventsProcessed) / uptime.Seconds()
		log.Printf("Event rate: %.2f events/sec", rate)
	}
	
	log.Printf("==============================")
}

// intToIP converts a uint32 IP address to net.IP
func intToIP(ip uint32) net.IP {
	return net.IPv4(byte(ip), byte(ip>>8), byte(ip>>16), byte(ip>>24))
}

func main() {
	// Configuration
	config := Config{
		SamplingRate:   1000,
		MaxFlows:      10000,
		ReportInterval: 30 * time.Second,
	}

	// Create monitor
	monitor, err := NewTCPFlowMonitor(config)
	if err != nil {
		log.Fatalf("Failed to create TCP flow monitor: %v", err)
	}

	// Set up signal handling
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	go func() {
		<-sigCh
		log.Printf("Received signal, shutting down...")
		cancel()
	}()

	// Start monitoring
	if err := monitor.Start(ctx); err != nil {
		log.Fatalf("Failed to start TCP flow monitor: %v", err)
	}

	// Wait for shutdown
	<-ctx.Done()

	// Clean up
	if err := monitor.Stop(); err != nil {
		log.Printf("Error stopping monitor: %v", err)
	}

	log.Printf("TCP Flow Monitor terminated")
}
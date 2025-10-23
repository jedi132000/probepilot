# ProbePilot eBPF Probes 🔬

## Kernel-Level Observability Agents

ProbePilot's eBPF probes provide deep, kernel-level insights into system behavior with minimal overhead. These probes are the core data collection agents that power the entire observability platform.

## Probe Categories

### 🌐 Network Observability
- **TCP Flow Tracking**: Connection lifecycle, throughput, and latency
- **UDP Monitoring**: Packet loss, jitter, and flow patterns
- **HTTP/HTTPS Analysis**: Request/response timing and status codes
- **DNS Resolution**: Query performance and failure analysis
- **Network Topology**: Service mesh and connectivity mapping

### ⚡ Performance Monitoring
- **CPU Profiling**: Function-level performance analysis
- **Memory Tracking**: Allocation patterns and leak detection
- **I/O Monitoring**: Disk and network I/O performance
- **Scheduler Analysis**: Process scheduling and context switches
- **Lock Contention**: Mutex and semaphore performance

### 🔒 Security Observability
- **System Call Auditing**: Comprehensive syscall monitoring
- **Process Lifecycle**: Process creation, execution, and termination
- **File Access Tracking**: File system access patterns
- **Network Security**: Connection monitoring and anomaly detection
- **Privilege Escalation**: Security event detection

### 🎯 Application-Specific
- **Database Monitoring**: Query performance and connection pooling
- **Web Server Analysis**: Request handling and response times
- **Container Runtime**: Docker/containerd performance metrics
- **Kubernetes Events**: Pod lifecycle and resource usage

## Probe Architecture

### Core Components
```
┌─────────────────────────────────────────────┐
│            ProbePilot Probe                 │
├─────────────────────────────────────────────┤
│  eBPF Kernel Program                        │
│  ├── Event Collection                       │
│  ├── Data Filtering                         │
│  ├── Aggregation Logic                      │
│  └── Ring Buffer Output                     │
├─────────────────────────────────────────────┤
│  Userspace Agent                            │
│  ├── Probe Management                       │
│  ├── Data Processing                        │
│  ├── Configuration Updates                  │
│  └── Backend Communication                  │
└─────────────────────────────────────────────┘
```

## Probe Development Framework

### SDK Components
- **Probe Templates**: Pre-built probe skeletons for common use cases
- **Helper Functions**: Kernel version compatibility abstractions
- **Data Structures**: Optimized data collection formats
- **Testing Framework**: Comprehensive probe validation tools
- **Packaging System**: Automated probe compilation and distribution

### Development Workflow
1. **Design**: Define probe objectives and data collection requirements
2. **Implementation**: Write eBPF C code using ProbePilot SDK
3. **Testing**: Validate probe behavior in controlled environments
4. **Compilation**: Generate bytecode for target kernel versions
5. **Deployment**: Package and distribute through ProbePilot platform
6. **Monitoring**: Track probe performance and health

## Probe Structure

```
probes/
├── network/
│   ├── tcp-flow/              # TCP connection monitoring
│   ├── http-latency/          # HTTP request tracking
│   ├── dns-resolver/          # DNS query monitoring
│   └── packet-loss/           # Network packet analysis
├── performance/
│   ├── cpu-profiler/          # CPU usage profiling
│   ├── memory-tracker/        # Memory allocation monitoring
│   ├── io-monitor/            # I/O performance tracking
│   └── scheduler-analysis/    # Process scheduling insights
├── security/
│   ├── syscall-auditor/       # System call monitoring
│   ├── process-tracker/       # Process lifecycle tracking
│   ├── file-monitor/          # File access auditing
│   └── network-security/      # Network security events
├── custom/
│   ├── examples/              # Example custom probes
│   ├── templates/             # Probe development templates
│   └── sdk/                   # Development SDK
└── shared/
    ├── common.h               # Shared headers and utilities
    ├── helpers.h              # Kernel compatibility helpers
    └── data-structures.h      # Standard data formats
```

## Key Features

### 🎯 Zero-Overhead Observability
- **Efficient Sampling**: Smart sampling strategies to minimize impact
- **In-Kernel Filtering**: Reduce userspace processing overhead
- **Batch Processing**: Aggregate data in kernel space before export
- **Resource Limits**: Built-in safeguards against resource exhaustion

### 🔧 Dynamic Configuration
- **Hot Updates**: Modify probe behavior without restart
- **Conditional Activation**: Enable/disable based on system state
- **Parameter Tuning**: Adjust sampling rates and filters dynamically
- **Feature Flags**: Toggle specific probe capabilities

### 🛡️ Safety & Reliability
- **Kernel Verifier**: Ensures probe safety before loading
- **Graceful Degradation**: Fallback modes for older kernel versions
- **Error Handling**: Comprehensive error detection and recovery
- **Resource Monitoring**: Self-monitoring for resource usage

### 📊 Rich Data Collection
- **Multi-dimensional Metrics**: Comprehensive data point collection
- **Event Correlation**: Link related events across subsystems
- **Metadata Enrichment**: Add context to raw telemetry data
- **Timestamp Precision**: High-resolution timing information

## Deployment Models

### 1. DaemonSet Deployment (Kubernetes)
- Automatic probe distribution across all nodes
- Centralized configuration management
- Rolling updates and health monitoring
- Integration with Kubernetes RBAC

### 2. Agent-Based Deployment (Bare Metal)
- Standalone probe agents on individual servers
- Remote configuration and management
- Secure communication with backend
- Local data caching and retry logic

### 3. Sidecar Deployment (Service Mesh)
- Application-specific probe injection
- Per-service observability configuration
- Integration with Istio/Linkerd service mesh
- Fine-grained access control

## Performance Characteristics

### Resource Usage
- **CPU Overhead**: <1% under normal load
- **Memory Footprint**: <50MB per probe agent
- **Network Bandwidth**: <1Mbps for telemetry data
- **Storage Requirements**: Minimal local caching

### Data Collection Rates
- **Network Events**: 100K+ events/second per probe
- **System Calls**: 1M+ syscalls/second monitoring
- **Performance Metrics**: Millisecond resolution sampling
- **Security Events**: Real-time threat detection

## Compatibility

### Kernel Versions
- **Minimum**: Linux 4.4+ (basic eBPF support)
- **Recommended**: Linux 5.4+ (full feature support)
- **Latest**: Linux 6.0+ (advanced eBPF features)

### Container Runtimes
- Docker (all versions)
- containerd
- CRI-O
- Podman

### Cloud Platforms
- AWS (EC2, EKS, Fargate)
- Google Cloud (GCE, GKE)
- Azure (VMs, AKS)
- On-premises Kubernetes

---

*ProbePilot probes represent the cutting edge of eBPF-based observability, providing unprecedented visibility into system behavior with minimal performance impact.*
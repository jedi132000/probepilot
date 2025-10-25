"""
Enhanced eBPF-style Probe Simulator
Provides comprehensive system observability simulating deep kernel-level metrics
"""

import asyncio
import time
import psutil
import subprocess
import socket
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
import json
import os
import glob
import random
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SystemCallEvent:
    """Represents a system call event"""
    pid: int
    process_name: str
    syscall_name: str
    args: List[str]
    return_value: int
    latency_ns: int
    timestamp: datetime
    cpu_id: int

@dataclass
class NetworkFlow:
    """Represents a network flow"""
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    packets_sent: int
    packets_received: int
    connection_state: str
    latency_ms: float
    timestamp: datetime

@dataclass
class ProcessMetrics:
    """Comprehensive process metrics"""
    pid: int
    name: str
    cmd: str
    status: str
    cpu_percent: float
    memory_rss: int
    memory_vms: int
    memory_percent: float
    num_threads: int
    num_fds: int
    read_bytes: int
    write_bytes: int
    read_count: int
    write_count: int
    create_time: datetime
    context_switches: int
    cpu_times: Dict[str, float]

@dataclass
class KernelMetrics:
    """Kernel-level metrics"""
    interrupts_per_sec: int
    context_switches_per_sec: int
    page_faults_per_sec: int
    major_page_faults_per_sec: int
    cpu_migrations: int
    cache_misses: int
    cache_references: int
    branch_misses: int
    branch_instructions: int
    task_clock: float
    instructions: int
    cycles: int

class EnhancedProbeSimulator:
    """Enhanced probe simulator with eBPF-style deep observability"""
    
    def __init__(self):
        self.running = False
        self.probe_types = {
            'syscall_tracer': self._collect_syscall_events,
            'network_monitor': self._collect_network_flows,
            'process_profiler': self._collect_process_metrics,
            'kernel_profiler': self._collect_kernel_metrics,
            'io_monitor': self._collect_io_metrics,
            'security_monitor': self._collect_security_events,
            'performance_profiler': self._collect_performance_metrics,
            'memory_tracker': self._collect_memory_events,
            'scheduler_tracer': self._collect_scheduler_events,
            'filesystem_monitor': self._collect_filesystem_events
        }
        self.cache = {}
        self.last_collection = {}
        
    async def collect_probe_data(self, probe_type: str) -> Dict[str, Any]:
        """Collect data for a specific probe type"""
        if probe_type not in self.probe_types:
            logger.warning(f"Unknown probe type: {probe_type}")
            return {}
            
        try:
            collector_func = self.probe_types[probe_type]
            data = await collector_func()
            
            # Update cache
            self.cache[probe_type] = data
            self.last_collection[probe_type] = datetime.now()
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting data for probe {probe_type}: {e}")
            return {}
    
    async def _collect_syscall_events(self) -> Dict[str, Any]:
        """Simulate syscall tracing data"""
        # In real eBPF, this would trace actual syscalls
        # Here we simulate based on process activity
        
        syscalls = []
        common_syscalls = [
            'read', 'write', 'open', 'close', 'stat', 'fstat', 
            'lstat', 'poll', 'lseek', 'mmap', 'mprotect', 'munmap',
            'brk', 'clone', 'execve', 'exit', 'wait4', 'kill',
            'getpid', 'socket', 'connect', 'accept', 'sendto', 'recvfrom'
        ]
        
        try:
            # Get current processes and simulate syscalls
            processes = list(psutil.process_iter(['pid', 'name', 'create_time']))
            
            for _ in range(random.randint(50, 200)):  # Simulate syscall volume
                proc = random.choice(processes)
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    
                    syscall_event = SystemCallEvent(
                        pid=pid,
                        process_name=name,
                        syscall_name=random.choice(common_syscalls),
                        args=[f"arg{i}" for i in range(random.randint(1, 4))],
                        return_value=random.choice([0, -1, random.randint(1, 1000)]),
                        latency_ns=random.randint(100, 50000),  # nanoseconds
                        timestamp=datetime.now(),
                        cpu_id=random.randint(0, psutil.cpu_count() - 1)
                    )
                    
                    syscalls.append(asdict(syscall_event))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Aggregate statistics
            syscall_stats = {}
            for syscall in syscalls:
                name = syscall['syscall_name']
                if name not in syscall_stats:
                    syscall_stats[name] = {
                        'count': 0,
                        'total_latency_ns': 0,
                        'avg_latency_ns': 0,
                        'errors': 0
                    }
                
                syscall_stats[name]['count'] += 1
                syscall_stats[name]['total_latency_ns'] += syscall['latency_ns']
                if syscall['return_value'] < 0:
                    syscall_stats[name]['errors'] += 1
            
            # Calculate averages
            for stats in syscall_stats.values():
                if stats['count'] > 0:
                    stats['avg_latency_ns'] = stats['total_latency_ns'] / stats['count']
            
            return {
                'type': 'syscall_tracer',
                'events': syscalls,
                'total_events': len(syscalls),
                'syscall_stats': syscall_stats,
                'collection_time': datetime.now().isoformat(),
                'data_size': len(syscalls) * 150  # Simulate data size
            }
            
        except Exception as e:
            logger.error(f"Error collecting syscall events: {e}")
            return {'type': 'syscall_tracer', 'error': str(e)}
    
    async def _collect_network_flows(self) -> Dict[str, Any]:
        """Simulate network flow monitoring"""
        flows = []
        
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            net_io = psutil.net_io_counters()
            
            for conn in connections[:50]:  # Limit to prevent overflow
                try:
                    if conn.laddr and conn.raddr:
                        flow = NetworkFlow(
                            src_ip=conn.laddr.ip,
                            dst_ip=conn.raddr.ip,
                            src_port=conn.laddr.port,
                            dst_port=conn.raddr.port,
                            protocol='TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                            bytes_sent=random.randint(100, 10000),
                            bytes_received=random.randint(100, 10000),
                            packets_sent=random.randint(1, 100),
                            packets_received=random.randint(1, 100),
                            connection_state=conn.status,
                            latency_ms=random.uniform(0.1, 50.0),
                            timestamp=datetime.now()
                        )
                        flows.append(asdict(flow))
                except Exception:
                    continue
            
            # Network interface statistics
            net_interfaces = {}
            try:
                for interface, stats in psutil.net_io_counters(pernic=True).items():
                    net_interfaces[interface] = {
                        'bytes_sent': stats.bytes_sent,
                        'bytes_recv': stats.bytes_recv,
                        'packets_sent': stats.packets_sent,
                        'packets_recv': stats.packets_recv,
                        'errin': stats.errin,
                        'errout': stats.errout,
                        'dropin': stats.dropin,
                        'dropout': stats.dropout
                    }
            except Exception:
                pass
            
            return {
                'type': 'network_monitor',
                'flows': flows,
                'total_flows': len(flows),
                'active_connections': len(connections),
                'interface_stats': net_interfaces,
                'global_net_io': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'collection_time': datetime.now().isoformat(),
                'data_size': len(flows) * 200
            }
            
        except Exception as e:
            logger.error(f"Error collecting network flows: {e}")
            return {'type': 'network_monitor', 'error': str(e)}
    
    async def _collect_process_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive process metrics"""
        processes = []
        
        try:
            for proc in psutil.process_iter([
                'pid', 'name', 'cmdline', 'status', 'create_time',
                'cpu_percent', 'memory_info', 'memory_percent', 
                'num_threads', 'num_fds'
            ]):
                try:
                    pinfo = proc.info
                    
                    # Get additional metrics
                    try:
                        cpu_times = proc.cpu_times()._asdict()
                        io_counters = proc.io_counters()
                        ctx_switches = proc.num_ctx_switches()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        cpu_times = {}
                        io_counters = None
                        ctx_switches = None
                    
                    process_metrics = ProcessMetrics(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        cmd=' '.join(pinfo.get('cmdline', [])) if pinfo.get('cmdline') else '',
                        status=pinfo['status'],
                        cpu_percent=pinfo.get('cpu_percent', 0),
                        memory_rss=pinfo.get('memory_info', type('obj', (object,), {'rss': 0})).rss,
                        memory_vms=pinfo.get('memory_info', type('obj', (object,), {'vms': 0})).vms,
                        memory_percent=pinfo.get('memory_percent', 0),
                        num_threads=pinfo.get('num_threads', 0),
                        num_fds=pinfo.get('num_fds', 0),
                        read_bytes=io_counters.read_bytes if io_counters else 0,
                        write_bytes=io_counters.write_bytes if io_counters else 0,
                        read_count=io_counters.read_count if io_counters else 0,
                        write_count=io_counters.write_count if io_counters else 0,
                        create_time=datetime.fromtimestamp(pinfo.get('create_time', time.time())),
                        context_switches=ctx_switches.voluntary + ctx_switches.involuntary if ctx_switches else 0,
                        cpu_times=cpu_times
                    )
                    
                    processes.append(asdict(process_metrics))
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
                # Limit to prevent memory issues
                if len(processes) >= 100:
                    break
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Calculate aggregate statistics
            total_processes = len(processes)
            total_threads = sum(p.get('num_threads', 0) for p in processes)
            total_memory = sum(p.get('memory_rss', 0) for p in processes)
            avg_cpu = sum(p.get('cpu_percent', 0) for p in processes) / max(1, total_processes)
            
            return {
                'type': 'process_profiler',
                'processes': processes,
                'total_processes': total_processes,
                'total_threads': total_threads,
                'total_memory_bytes': total_memory,
                'average_cpu_percent': avg_cpu,
                'top_cpu_processes': processes[:10],
                'top_memory_processes': sorted(processes, key=lambda x: x.get('memory_rss', 0), reverse=True)[:10],
                'collection_time': datetime.now().isoformat(),
                'data_size': len(processes) * 300
            }
            
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            return {'type': 'process_profiler', 'error': str(e)}
    
    async def _collect_kernel_metrics(self) -> Dict[str, Any]:
        """Simulate kernel-level performance metrics"""
        try:
            # Get CPU stats for context switches and interrupts
            cpu_stats = psutil.cpu_stats()
            
            # Simulate performance counters (in real eBPF, these would be actual perf events)
            kernel_metrics = KernelMetrics(
                interrupts_per_sec=cpu_stats.interrupts // 60,  # Rough estimate
                context_switches_per_sec=cpu_stats.ctx_switches // 60,
                page_faults_per_sec=random.randint(100, 1000),
                major_page_faults_per_sec=random.randint(1, 50),
                cpu_migrations=random.randint(0, 100),
                cache_misses=random.randint(1000, 100000),
                cache_references=random.randint(100000, 1000000),
                branch_misses=random.randint(1000, 50000),
                branch_instructions=random.randint(100000, 5000000),
                task_clock=time.time(),
                instructions=random.randint(1000000, 100000000),
                cycles=random.randint(1000000, 500000000)
            )
            
            # Additional kernel information
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            # Get loadavg if available
            try:
                load_avg = os.getloadavg()
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]
            
            # Memory statistics
            memory = psutil.virtual_memory()
            
            return {
                'type': 'kernel_profiler',
                'kernel_metrics': asdict(kernel_metrics),
                'system_info': {
                    'boot_time': boot_time,
                    'uptime_seconds': uptime_seconds,
                    'load_average': {
                        '1min': load_avg[0],
                        '5min': load_avg[1],
                        '15min': load_avg[2]
                    },
                    'cpu_count': psutil.cpu_count(),
                    'cpu_count_logical': psutil.cpu_count(logical=True),
                    'memory_total': memory.total,
                    'memory_available': memory.available
                },
                'performance_counters': {
                    'cache_hit_rate': 1 - (kernel_metrics.cache_misses / max(1, kernel_metrics.cache_references)),
                    'branch_prediction_rate': 1 - (kernel_metrics.branch_misses / max(1, kernel_metrics.branch_instructions)),
                    'ipc': kernel_metrics.instructions / max(1, kernel_metrics.cycles),  # Instructions per cycle
                    'context_switch_rate': kernel_metrics.context_switches_per_sec,
                    'interrupt_rate': kernel_metrics.interrupts_per_sec
                },
                'collection_time': datetime.now().isoformat(),
                'data_size': 500
            }
            
        except Exception as e:
            logger.error(f"Error collecting kernel metrics: {e}")
            return {'type': 'kernel_profiler', 'error': str(e)}
    
    async def _collect_io_metrics(self) -> Dict[str, Any]:
        """Collect I/O subsystem metrics"""
        try:
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_partitions = psutil.disk_partitions()
            
            # Per-disk metrics
            disk_io_per_device = psutil.disk_io_counters(perdisk=True)
            
            # Disk usage for all mounted partitions
            disk_usage = {}
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Simulate I/O latency distribution
            io_latency_histogram = {
                '0-1ms': random.randint(1000, 5000),
                '1-5ms': random.randint(500, 2000),
                '5-10ms': random.randint(100, 500),
                '10-50ms': random.randint(50, 200),
                '50-100ms': random.randint(10, 50),
                '100ms+': random.randint(1, 20)
            }
            
            return {
                'type': 'io_monitor',
                'global_disk_io': {
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count,
                    'read_bytes': disk_io.read_bytes,
                    'write_bytes': disk_io.write_bytes,
                    'read_time': disk_io.read_time,
                    'write_time': disk_io.write_time,
                    'busy_time': getattr(disk_io, 'busy_time', 0)
                },
                'per_device_io': dict(disk_io_per_device),
                'disk_usage': disk_usage,
                'io_latency_histogram': io_latency_histogram,
                'io_patterns': {
                    'sequential_reads': random.randint(100, 1000),
                    'random_reads': random.randint(50, 500),
                    'sequential_writes': random.randint(80, 800),
                    'random_writes': random.randint(30, 300)
                },
                'collection_time': datetime.now().isoformat(),
                'data_size': 400
            }
            
        except Exception as e:
            logger.error(f"Error collecting I/O metrics: {e}")
            return {'type': 'io_monitor', 'error': str(e)}
    
    async def _collect_security_events(self) -> Dict[str, Any]:
        """Simulate security monitoring events"""
        try:
            security_events = []
            
            # Simulate various security events
            event_types = [
                'failed_login', 'privilege_escalation', 'suspicious_process',
                'network_anomaly', 'file_access_violation', 'port_scan'
            ]
            
            for _ in range(random.randint(0, 10)):  # 0-10 security events
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': random.choice(event_types),
                    'severity': random.choice(['low', 'medium', 'high', 'critical']),
                    'source_ip': f"192.168.1.{random.randint(1, 254)}",
                    'target': f"process_{random.randint(1000, 9999)}",
                    'details': f"Security event detected at {datetime.now()}",
                    'mitigated': random.choice([True, False])
                }
                security_events.append(event)
            
            # Count events by severity
            severity_counts = {}
            for event in security_events:
                severity = event['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                'type': 'security_monitor',
                'events': security_events,
                'total_events': len(security_events),
                'severity_distribution': severity_counts,
                'threat_level': 'low' if len(security_events) < 5 else 'medium' if len(security_events) < 15 else 'high',
                'collection_time': datetime.now().isoformat(),
                'data_size': len(security_events) * 100
            }
            
        except Exception as e:
            logger.error(f"Error collecting security events: {e}")
            return {'type': 'security_monitor', 'error': str(e)}
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        try:
            # CPU detailed metrics
            cpu_times = psutil.cpu_times()
            cpu_percent_per_cpu = psutil.cpu_percent(percpu=True, interval=0.1)
            cpu_freq = psutil.cpu_freq()
            
            # Memory detailed breakdown
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Temperature (if available)
            try:
                temps = psutil.sensors_temperatures()
            except AttributeError:
                temps = {}
            
            # Battery (if available)
            try:
                battery = psutil.sensors_battery()
                battery_info = {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'secsleft': battery.secsleft
                } if battery else None
            except AttributeError:
                battery_info = None
            
            # Performance score calculation
            cpu_score = max(0, 100 - psutil.cpu_percent(interval=0.1))
            memory_score = max(0, 100 - memory.percent)
            
            # Simulate performance bottlenecks
            bottlenecks = []
            if psutil.cpu_percent() > 80:
                bottlenecks.append({'type': 'cpu', 'severity': 'high', 'description': 'High CPU usage detected'})
            if memory.percent > 85:
                bottlenecks.append({'type': 'memory', 'severity': 'high', 'description': 'High memory usage detected'})
            
            return {
                'type': 'performance_profiler',
                'cpu_metrics': {
                    'usage_percent': psutil.cpu_percent(),
                    'per_cpu_percent': cpu_percent_per_cpu,
                    'cpu_times': cpu_times._asdict(),
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else 0,
                        'min': cpu_freq.min if cpu_freq else 0,
                        'max': cpu_freq.max if cpu_freq else 0
                    }
                },
                'memory_metrics': {
                    'virtual': memory._asdict(),
                    'swap': swap._asdict(),
                    'memory_pressure': max(0, (memory.percent - 70) / 30)  # 0-1 scale above 70%
                },
                'performance_scores': {
                    'cpu_score': cpu_score,
                    'memory_score': memory_score,
                    'overall_score': (cpu_score + memory_score) / 2
                },
                'bottlenecks': bottlenecks,
                'thermal_info': temps,
                'battery_info': battery_info,
                'collection_time': datetime.now().isoformat(),
                'data_size': 600
            }
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {'type': 'performance_profiler', 'error': str(e)}
    
    async def _collect_memory_events(self) -> Dict[str, Any]:
        """Collect memory subsystem events"""
        try:
            memory = psutil.virtual_memory()
            
            # Simulate memory allocation patterns
            allocation_events = []
            for _ in range(random.randint(10, 50)):
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'pid': random.randint(1, 32768),
                    'operation': random.choice(['alloc', 'free', 'realloc']),
                    'size': random.randint(1024, 1024*1024*10),  # 1KB to 10MB
                    'address': f"0x{random.randint(0x1000, 0xffffffff):08x}",
                    'success': random.choice([True, True, True, False])  # Mostly successful
                }
                allocation_events.append(event)
            
            # Memory pool statistics
            memory_pools = {
                'kernel': {'allocated': random.randint(100*1024*1024, 500*1024*1024), 'free': random.randint(50*1024*1024, 200*1024*1024)},
                'user': {'allocated': memory.used, 'free': memory.available},
                'cache': {'allocated': getattr(memory, 'cached', 0), 'free': random.randint(10*1024*1024, 100*1024*1024)},
                'buffers': {'allocated': getattr(memory, 'buffers', 0), 'free': random.randint(5*1024*1024, 50*1024*1024)}
            }
            
            return {
                'type': 'memory_tracker',
                'allocation_events': allocation_events,
                'memory_pools': memory_pools,
                'memory_fragmentation': random.uniform(0.1, 0.3),  # 10-30% fragmentation
                'oom_events': random.randint(0, 2),  # Out of memory events
                'page_faults': {
                    'minor': random.randint(100, 10000),
                    'major': random.randint(1, 100)
                },
                'collection_time': datetime.now().isoformat(),
                'data_size': len(allocation_events) * 80
            }
            
        except Exception as e:
            logger.error(f"Error collecting memory events: {e}")
            return {'type': 'memory_tracker', 'error': str(e)}
    
    async def _collect_scheduler_events(self) -> Dict[str, Any]:
        """Collect CPU scheduler events"""
        try:
            # Get process information for scheduler analysis
            processes = list(psutil.process_iter(['pid', 'name', 'nice', 'status']))
            
            # Simulate scheduler events
            scheduler_events = []
            for _ in range(random.randint(50, 200)):
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'pid': random.choice(processes).info['pid'] if processes else random.randint(1, 1000),
                    'event_type': random.choice(['task_switch', 'wakeup', 'sleep', 'migrate']),
                    'cpu_from': random.randint(0, psutil.cpu_count() - 1),
                    'cpu_to': random.randint(0, psutil.cpu_count() - 1),
                    'priority': random.randint(-20, 19),
                    'runtime_ns': random.randint(1000, 1000000)
                }
                scheduler_events.append(event)
            
            # CPU load balancing
            cpu_loads = psutil.cpu_percent(percpu=True, interval=0.1)
            load_balance_score = 1.0 - (max(cpu_loads) - min(cpu_loads)) / 100.0
            
            return {
                'type': 'scheduler_tracer',
                'scheduler_events': scheduler_events,
                'cpu_loads': cpu_loads,
                'load_balance_score': load_balance_score,
                'runqueue_lengths': [random.randint(0, 10) for _ in range(psutil.cpu_count())],
                'context_switches_per_sec': psutil.cpu_stats().ctx_switches // 60,
                'collection_time': datetime.now().isoformat(),
                'data_size': len(scheduler_events) * 60
            }
            
        except Exception as e:
            logger.error(f"Error collecting scheduler events: {e}")
            return {'type': 'scheduler_tracer', 'error': str(e)}
    
    async def _collect_filesystem_events(self) -> Dict[str, Any]:
        """Collect filesystem events"""
        try:
            # Get disk usage
            partitions = psutil.disk_partitions()
            filesystem_stats = {}
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    filesystem_stats[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Simulate file operations
            file_operations = []
            operations = ['open', 'read', 'write', 'close', 'create', 'delete', 'rename']
            
            for _ in range(random.randint(20, 100)):
                op = {
                    'timestamp': datetime.now().isoformat(),
                    'operation': random.choice(operations),
                    'path': f"/tmp/file_{random.randint(1, 1000)}.txt",
                    'pid': random.randint(1, 32768),
                    'bytes': random.randint(1, 1024*1024) if random.choice(operations) in ['read', 'write'] else 0,
                    'latency_ms': random.uniform(0.1, 10.0),
                    'success': random.choice([True, True, True, False])
                }
                file_operations.append(op)
            
            # Inode usage
            try:
                # Simulate inode statistics (would be real in eBPF)
                total_inodes = random.randint(1000000, 10000000)
                used_inodes = random.randint(100000, total_inodes // 2)
                
                inode_stats = {
                    'total': total_inodes,
                    'used': used_inodes,
                    'free': total_inodes - used_inodes,
                    'percent': (used_inodes / total_inodes) * 100
                }
            except Exception:
                inode_stats = {}
            
            return {
                'type': 'filesystem_monitor',
                'filesystem_stats': filesystem_stats,
                'file_operations': file_operations,
                'inode_stats': inode_stats,
                'hot_files': [  # Most accessed files
                    {'path': '/var/log/syslog', 'access_count': random.randint(100, 1000)},
                    {'path': '/tmp/cache.db', 'access_count': random.randint(50, 500)},
                    {'path': '/etc/passwd', 'access_count': random.randint(10, 100)}
                ],
                'collection_time': datetime.now().isoformat(),
                'data_size': len(file_operations) * 70
            }
            
        except Exception as e:
            logger.error(f"Error collecting filesystem events: {e}")
            return {'type': 'filesystem_monitor', 'error': str(e)}

# Global enhanced probe simulator
enhanced_probe_simulator = EnhancedProbeSimulator()
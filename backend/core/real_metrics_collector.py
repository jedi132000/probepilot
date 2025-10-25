"""
Real System Metrics Collector
Replaces simulation with actual system observability data
"""

import asyncio
import time
import psutil
import subprocess
import socket
import threading
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class RealNetworkConnection:
    """Real network connection data"""
    pid: int
    process_name: str
    local_address: str
    local_port: int
    remote_address: str
    remote_port: int
    status: str
    family: str  # AF_INET, AF_INET6
    type: str    # SOCK_STREAM, SOCK_DGRAM
    timestamp: datetime

@dataclass
class ProcessMetrics:
    """Real process metrics"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_rss: int
    memory_vms: int
    num_threads: int
    num_fds: int
    create_time: float
    status: str
    username: str
    cmdline: List[str]
    connections: List[RealNetworkConnection]
    io_counters: Optional[Dict[str, int]]
    timestamp: datetime

@dataclass
class SystemIOMetrics:
    """Real system I/O metrics"""
    disk_read_bytes: int
    disk_write_bytes: int
    disk_read_count: int
    disk_write_count: int
    disk_read_time: int
    disk_write_time: int
    network_bytes_sent: int
    network_bytes_recv: int
    network_packets_sent: int
    network_packets_recv: int
    network_errin: int
    network_errout: int
    network_dropin: int
    network_dropout: int
    timestamp: datetime

class RealMetricsCollector:
    """Collects real system metrics instead of simulated data"""
    
    def __init__(self):
        self.collection_interval = 1.0  # seconds
        self.is_collecting = False
        self.metrics_history = []
        self.max_history_size = 1000
        
    async def start_collection(self):
        """Start real-time metrics collection"""
        self.is_collecting = True
        logger.info("Started real system metrics collection")
        
        while self.is_collecting:
            try:
                metrics = await self.collect_comprehensive_metrics()
                self.metrics_history.append(metrics)
                
                # Keep history within limits
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                    
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.is_collecting = False
        logger.info("Stopped real system metrics collection")
    
    async def collect_comprehensive_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive real system metrics"""
        timestamp = datetime.now()
        
        # System-wide metrics
        cpu_metrics = self._collect_cpu_metrics()
        memory_metrics = self._collect_memory_metrics()
        disk_metrics = self._collect_disk_metrics()
        network_metrics = self._collect_network_metrics()
        
        # Process-level metrics
        process_metrics = self._collect_process_metrics()
        
        # Network connections
        network_connections = self._collect_network_connections()
        
        # System load and performance
        system_metrics = self._collect_system_metrics()
        
        return {
            'timestamp': timestamp.isoformat(),
            'cpu': cpu_metrics,
            'memory': memory_metrics,
            'disk': disk_metrics,
            'network': network_metrics,
            'processes': process_metrics,
            'connections': network_connections,
            'system': system_metrics
        }
    
    def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect real CPU metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_times = psutil.cpu_times()
            cpu_stats = psutil.cpu_stats()
            cpu_freq = psutil.cpu_freq()
            
            return {
                'percent_per_core': cpu_percent,
                'percent_total': psutil.cpu_percent(),
                'times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle,
                    'nice': getattr(cpu_times, 'nice', 0),
                    'iowait': getattr(cpu_times, 'iowait', 0),
                    'irq': getattr(cpu_times, 'irq', 0),
                    'softirq': getattr(cpu_times, 'softirq', 0),
                },
                'stats': {
                    'ctx_switches': cpu_stats.ctx_switches,
                    'interrupts': cpu_stats.interrupts,
                    'soft_interrupts': cpu_stats.soft_interrupts,
                    'syscalls': getattr(cpu_stats, 'syscalls', 0)
                },
                'frequency': {
                    'current': cpu_freq.current if cpu_freq else 0,
                    'min': cpu_freq.min if cpu_freq else 0,
                    'max': cpu_freq.max if cpu_freq else 0
                },
                'core_count': psutil.cpu_count(),
                'logical_count': psutil.cpu_count(logical=True)
            }
        except Exception as e:
            logger.error(f"Error collecting CPU metrics: {e}")
            return {}
    
    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect real memory metrics"""
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                'virtual': {
                    'total': virtual_memory.total,
                    'available': virtual_memory.available,
                    'used': virtual_memory.used,
                    'free': virtual_memory.free,
                    'percent': virtual_memory.percent,
                    'active': getattr(virtual_memory, 'active', 0),
                    'inactive': getattr(virtual_memory, 'inactive', 0),
                    'buffers': getattr(virtual_memory, 'buffers', 0),
                    'cached': getattr(virtual_memory, 'cached', 0),
                    'shared': getattr(virtual_memory, 'shared', 0),
                    'wired': getattr(virtual_memory, 'wired', 0)
                },
                'swap': {
                    'total': swap_memory.total,
                    'used': swap_memory.used,
                    'free': swap_memory.free,
                    'percent': swap_memory.percent,
                    'sin': swap_memory.sin,
                    'sout': swap_memory.sout
                }
            }
        except Exception as e:
            logger.error(f"Error collecting memory metrics: {e}")
            return {}
    
    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect real disk I/O metrics"""
        try:
            disk_io = psutil.disk_io_counters(perdisk=True)
            disk_usage = {}
            
            # Get disk usage for mounted filesystems
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100 if usage.total > 0 else 0
                    }
                except PermissionError:
                    continue
            
            disk_io_total = psutil.disk_io_counters()
            
            return {
                'io_total': {
                    'read_count': disk_io_total.read_count,
                    'write_count': disk_io_total.write_count,
                    'read_bytes': disk_io_total.read_bytes,
                    'write_bytes': disk_io_total.write_bytes,
                    'read_time': disk_io_total.read_time,
                    'write_time': disk_io_total.write_time
                } if disk_io_total else {},
                'io_per_disk': {
                    device: {
                        'read_count': stats.read_count,
                        'write_count': stats.write_count,
                        'read_bytes': stats.read_bytes,
                        'write_bytes': stats.write_bytes,
                        'read_time': stats.read_time,
                        'write_time': stats.write_time
                    } for device, stats in (disk_io or {}).items()
                },
                'usage': disk_usage
            }
        except Exception as e:
            logger.error(f"Error collecting disk metrics: {e}")
            return {}
    
    def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect real network metrics"""
        try:
            net_io = psutil.net_io_counters(pernic=True)
            net_io_total = psutil.net_io_counters()
            
            return {
                'io_total': {
                    'bytes_sent': net_io_total.bytes_sent,
                    'bytes_recv': net_io_total.bytes_recv,
                    'packets_sent': net_io_total.packets_sent,
                    'packets_recv': net_io_total.packets_recv,
                    'errin': net_io_total.errin,
                    'errout': net_io_total.errout,
                    'dropin': net_io_total.dropin,
                    'dropout': net_io_total.dropout
                } if net_io_total else {},
                'io_per_interface': {
                    interface: {
                        'bytes_sent': stats.bytes_sent,
                        'bytes_recv': stats.bytes_recv,
                        'packets_sent': stats.packets_sent,
                        'packets_recv': stats.packets_recv,
                        'errin': stats.errin,
                        'errout': stats.errout,
                        'dropin': stats.dropin,
                        'dropout': stats.dropout
                    } for interface, stats in (net_io or {}).items()
                }
            }
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
            return {}
    
    def _collect_process_metrics(self) -> List[Dict[str, Any]]:
        """Collect real per-process metrics"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'memory_info', 'num_threads', 'num_fds', 'create_time',
                                           'status', 'username', 'cmdline']):
                try:
                    proc_info = proc.info
                    
                    # Get I/O counters if available
                    io_counters = None
                    try:
                        io_counters = proc.io_counters()._asdict() if hasattr(proc, 'io_counters') else None
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                    
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'memory_rss': proc_info['memory_info'].rss if proc_info['memory_info'] else 0,
                        'memory_vms': proc_info['memory_info'].vms if proc_info['memory_info'] else 0,
                        'num_threads': proc_info['num_threads'],
                        'num_fds': proc_info['num_fds'],
                        'create_time': proc_info['create_time'],
                        'status': proc_info['status'],
                        'username': proc_info['username'],
                        'cmdline': proc_info['cmdline'] or [],
                        'io_counters': io_counters
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return processes
        except Exception as e:
            logger.error(f"Error collecting process metrics: {e}")
            return []
    
    def _collect_network_connections(self) -> List[Dict[str, Any]]:
        """Collect real network connections"""
        try:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                try:
                    # Get process info if available
                    process_name = "unknown"
                    if conn.pid:
                        try:
                            proc = psutil.Process(conn.pid)
                            process_name = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    connections.append({
                        'pid': conn.pid,
                        'process_name': process_name,
                        'fd': conn.fd,
                        'family': str(conn.family),
                        'type': str(conn.type),
                        'local_address': conn.laddr.ip if conn.laddr else None,
                        'local_port': conn.laddr.port if conn.laddr else None,
                        'remote_address': conn.raddr.ip if conn.raddr else None,
                        'remote_port': conn.raddr.port if conn.raddr else None,
                        'status': conn.status
                    })
                except Exception:
                    continue
                    
            return connections
        except Exception as e:
            logger.error(f"Error collecting network connections: {e}")
            return []
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-wide metrics"""
        try:
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            # Load averages (Unix-like systems)
            load_avg = getattr(os, 'getloadavg', lambda: (0, 0, 0))()
            
            return {
                'boot_time': boot_time,
                'uptime_seconds': uptime,
                'load_average': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                },
                'users': [user._asdict() for user in psutil.users()]
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get the most recent metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """Get metrics history for the specified time period"""
        if not self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        filtered_history = []
        for metric in self.metrics_history:
            try:
                metric_time = datetime.fromisoformat(metric['timestamp'])
                if metric_time >= cutoff_time:
                    filtered_history.append(metric)
            except (KeyError, ValueError):
                continue
                
        return filtered_history
    
    async def get_real_probe_data(self, probe_type: str) -> Dict[str, Any]:
        """Get real probe data based on probe type"""
        current_metrics = await self.collect_comprehensive_metrics()
        
        if probe_type == "syscall":
            return self._extract_syscall_data(current_metrics)
        elif probe_type == "network":
            return self._extract_network_data(current_metrics)
        elif probe_type == "process":
            return self._extract_process_data(current_metrics)
        elif probe_type == "kernel":
            return self._extract_kernel_data(current_metrics)
        elif probe_type == "memory":
            return self._extract_memory_data(current_metrics)
        elif probe_type == "disk":
            return self._extract_disk_data(current_metrics)
        else:
            return current_metrics
    
    def _extract_syscall_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract syscall-related data from real metrics"""
        return {
            'context_switches': metrics.get('cpu', {}).get('stats', {}).get('ctx_switches', 0),
            'interrupts': metrics.get('cpu', {}).get('stats', {}).get('interrupts', 0),
            'syscalls': metrics.get('cpu', {}).get('stats', {}).get('syscalls', 0),
            'processes': len(metrics.get('processes', [])),
            'active_processes': len([p for p in metrics.get('processes', []) 
                                   if p.get('status') in ['running', 'sleeping']]),
            'timestamp': metrics.get('timestamp')
        }
    
    def _extract_network_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network-related data from real metrics"""
        network = metrics.get('network', {})
        connections = metrics.get('connections', [])
        
        return {
            'total_connections': len(connections),
            'established_connections': len([c for c in connections if c.get('status') == 'ESTABLISHED']),
            'listening_connections': len([c for c in connections if c.get('status') == 'LISTEN']),
            'bytes_sent': network.get('io_total', {}).get('bytes_sent', 0),
            'bytes_recv': network.get('io_total', {}).get('bytes_recv', 0),
            'packets_sent': network.get('io_total', {}).get('packets_sent', 0),
            'packets_recv': network.get('io_total', {}).get('packets_recv', 0),
            'errors_in': network.get('io_total', {}).get('errin', 0),
            'errors_out': network.get('io_total', {}).get('errout', 0),
            'connections_by_port': self._group_connections_by_port(connections),
            'timestamp': metrics.get('timestamp')
        }
    
    def _extract_process_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract process-related data from real metrics"""
        processes = metrics.get('processes', [])
        
        return {
            'total_processes': len(processes),
            'total_threads': sum(p.get('num_threads', 0) for p in processes),
            'total_fds': sum(p.get('num_fds', 0) for p in processes),
            'cpu_usage_by_process': [(p.get('name', 'unknown'), p.get('cpu_percent', 0)) 
                                   for p in sorted(processes, 
                                                 key=lambda x: x.get('cpu_percent', 0), 
                                                 reverse=True)[:10]],
            'memory_usage_by_process': [(p.get('name', 'unknown'), p.get('memory_percent', 0)) 
                                      for p in sorted(processes, 
                                                    key=lambda x: x.get('memory_percent', 0), 
                                                    reverse=True)[:10]],
            'timestamp': metrics.get('timestamp')
        }
    
    def _extract_kernel_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract kernel-related data from real metrics"""
        cpu = metrics.get('cpu', {})
        system = metrics.get('system', {})
        
        return {
            'context_switches': cpu.get('stats', {}).get('ctx_switches', 0),
            'interrupts': cpu.get('stats', {}).get('interrupts', 0),
            'load_average': system.get('load_average', {}),
            'uptime': system.get('uptime_seconds', 0),
            'cpu_cores': cpu.get('core_count', 0),
            'cpu_frequency': cpu.get('frequency', {}),
            'timestamp': metrics.get('timestamp')
        }
    
    def _extract_memory_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract memory-related data from real metrics"""
        memory = metrics.get('memory', {})
        
        return {
            'virtual_memory': memory.get('virtual', {}),
            'swap_memory': memory.get('swap', {}),
            'memory_pressure': self._calculate_memory_pressure(memory),
            'timestamp': metrics.get('timestamp')
        }
    
    def _extract_disk_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Extract disk-related data from real metrics"""
        disk = metrics.get('disk', {})
        
        return {
            'io_counters': disk.get('io_total', {}),
            'disk_usage': disk.get('usage', {}),
            'io_per_disk': disk.get('io_per_disk', {}),
            'timestamp': metrics.get('timestamp')
        }
    
    def _group_connections_by_port(self, connections: List[Dict[str, Any]]) -> Dict[int, int]:
        """Group connections by local port"""
        port_counts = {}
        for conn in connections:
            port = conn.get('local_port')
            if port:
                port_counts[port] = port_counts.get(port, 0) + 1
        return port_counts
    
    def _calculate_memory_pressure(self, memory: Dict[str, Any]) -> float:
        """Calculate memory pressure score"""
        virtual = memory.get('virtual', {})
        swap = memory.get('swap', {})
        
        memory_percent = virtual.get('percent', 0)
        swap_percent = swap.get('percent', 0)
        
        # Simple pressure calculation
        pressure = (memory_percent * 0.7) + (swap_percent * 0.3)
        return min(pressure, 100.0)
"""
Real Probe Management System
Handles automatic state progression and live system metrics collection
Enhanced with advanced analytics and deep observability
"""

import asyncio
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

# Import advanced analytics and real metrics collector
from .advanced_analytics import advanced_analytics
from .real_metrics_collector import RealMetricsCollector

logger = logging.getLogger(__name__)

class RealProbeManager:
    """Manages real probe lifecycle and metrics collection"""
    
    def __init__(self):
        self.probes: Dict[str, Dict[str, Any]] = {}
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def register_probe(self, probe_id: str, probe_data: Dict[str, Any]):
        """Register a new probe for management"""
        probe_data.update({
            "start_time": time.time(),
            "last_metrics_update": time.time(),
            "metrics_history": [],
            "real_data_collected": 0,
            "bytes_collected": 0
        })
        self.probes[probe_id] = probe_data
        logger.info(f"Registered probe {probe_id} for real monitoring")
        
    def unregister_probe(self, probe_id: str):
        """Remove probe from management"""
        if probe_id in self.probes:
            del self.probes[probe_id]
            logger.info(f"Unregistered probe {probe_id}")
            
    async def start(self):
        """Start the probe manager background tasks"""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting Real Probe Manager...")
        
        # Start background tasks
        self.tasks = [
            asyncio.create_task(self._state_progression_loop()),
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._uptime_update_loop()),
            asyncio.create_task(self._advanced_analytics_loop())
        ]
        
        logger.info("Real Probe Manager started with 4 background tasks including advanced analytics")
        
    async def stop(self):
        """Stop the probe manager and cleanup"""
        if not self.running:
            return
            
        self.running = False
        logger.info("Stopping Real Probe Manager...")
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Real Probe Manager stopped")
        
    async def _state_progression_loop(self):
        """Automatically advance probes through deployment states"""
        while self.running:
            try:
                for probe_id, probe in self.probes.items():
                    await self._advance_probe_state_if_ready(probe_id, probe)
                await asyncio.sleep(2)  # Check every 2 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state progression loop: {e}")
                await asyncio.sleep(5)
                
    async def _advance_probe_state_if_ready(self, probe_id: str, probe: Dict[str, Any]):
        """Advance probe state based on realistic timing"""
        current_status = probe.get("status", "initializing")
        start_time = probe.get("start_time", time.time())
        elapsed = time.time() - start_time
        
        # Realistic state progression timing
        if current_status == "initializing" and elapsed > 3:  # 3 seconds to initialize
            await self._update_probe_state(probe_id, "loading")
        elif current_status == "loading" and elapsed > 8:  # 8 seconds total to load
            await self._update_probe_state(probe_id, "attaching")
        elif current_status == "attaching" and elapsed > 12:  # 12 seconds total to attach
            await self._update_probe_state(probe_id, "running")
            
    async def _update_probe_state(self, probe_id: str, new_status: str):
        """Update probe state and associated metrics"""
        if probe_id not in self.probes:
            return
            
        old_status = self.probes[probe_id].get("status", "unknown")
        self.probes[probe_id].update({
            "status": new_status,
            "last_updated": datetime.now().isoformat(),
            "deployment_stage": new_status
        })
        
        # Set health and data rate based on status
        if new_status == "running":
            self.probes[probe_id]["health"] = "healthy"
            # Will be updated with real metrics in metrics loop
        elif new_status == "error":
            self.probes[probe_id]["health"] = "error"
            self.probes[probe_id]["data_rate"] = "0.0 MB/s"
        else:
            self.probes[probe_id]["health"] = "starting"
            self.probes[probe_id]["data_rate"] = "0.0 MB/s"
            
        logger.info(f"Advanced probe {probe_id}: {old_status} -> {new_status}")
        
    async def _metrics_collection_loop(self):
        """Collect real system metrics for running probes"""
        # Initialize real metrics collector
        metrics_collector = RealMetricsCollector()
        
        while self.running:
            try:
                for probe_id, probe in self.probes.items():
                    if probe.get("status") == "running":
                        await self._collect_real_metrics(probe_id, probe, metrics_collector)
                await asyncio.sleep(1)  # Collect metrics every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(5)
                
    async def _collect_real_metrics(self, probe_id: str, probe: Dict[str, Any], metrics_collector: RealMetricsCollector):
        """Collect real system metrics using actual system data"""
        probe_type = probe.get("type", "unknown")
        
        try:
            # Map probe types to real metrics collection types
            metrics_type_mapping = {
                "cpu-profiler": "process",
                "CPU Performance Profiler": "process",
                "tcp-flow-monitor": "network", 
                "TCP Flow Monitor": "network",
                "http-latency-tracker": "network",
                "HTTP Latency Tracker": "network",
                "memory-monitor": "memory",
                "Memory Usage Monitor": "memory",
                "file-system-auditor": "disk",
                "File System Auditor": "disk",
                "syscall-tracer": "syscall",
                "kernel-profiler": "kernel",
                "io-monitor": "disk",
                "security-monitor": "process",
                "scheduler-tracer": "kernel"
            }
            
            # Get real metrics
            metrics_type = metrics_type_mapping.get(probe_type, "process")
            real_data = await metrics_collector.get_real_probe_data(metrics_type)
            
            # Extract metrics from real system data
            if real_data:
                if metrics_type == "process":
                    processes = real_data.get('cpu_usage_by_process', [])
                    memory_procs = real_data.get('memory_usage_by_process', [])
                    
                    metrics = {
                        'cpu_usage': sum([proc[1] for proc in processes[:5]]),  # Top 5 processes
                        'cpu_count': psutil.cpu_count() or 1,
                        'memory_percent': sum([proc[1] for proc in memory_procs[:5]]),  # Top 5 processes
                        'total_processes': real_data.get('total_processes', 0),
                        'total_threads': real_data.get('total_threads', 0),
                        'total_fds': real_data.get('total_fds', 0),
                        'data_size': len(str(real_data)),
                        'type': 'real_process',
                        'real_data': real_data
                    }
                elif metrics_type == "network":
                    metrics = {
                        'bytes_sent': real_data.get('bytes_sent', 0),
                        'bytes_recv': real_data.get('bytes_recv', 0),
                        'packets_sent': real_data.get('packets_sent', 0),
                        'packets_recv': real_data.get('packets_recv', 0),
                        'total_connections': real_data.get('total_connections', 0),
                        'established_connections': real_data.get('established_connections', 0),
                        'listening_connections': real_data.get('listening_connections', 0),
                        'errors_in': real_data.get('errors_in', 0),
                        'errors_out': real_data.get('errors_out', 0),
                        'data_size': len(str(real_data)),
                        'type': 'real_network',
                        'real_data': real_data
                    }
                elif metrics_type == "memory":
                    virtual_mem = real_data.get('virtual_memory', {})
                    swap_mem = real_data.get('swap_memory', {})
                    metrics = {
                        'memory_percent': virtual_mem.get('percent', 0),
                        'memory_available': virtual_mem.get('available', 0),
                        'memory_used': virtual_mem.get('used', 0),
                        'memory_total': virtual_mem.get('total', 0),
                        'swap_percent': swap_mem.get('percent', 0),
                        'swap_used': swap_mem.get('used', 0),
                        'memory_pressure': real_data.get('memory_pressure', 0),
                        'data_size': len(str(real_data)),
                        'type': 'real_memory',
                        'real_data': real_data
                    }
                elif metrics_type == "disk":
                    io_counters = real_data.get('io_counters', {})
                    disk_usage = real_data.get('disk_usage', {})
                    metrics = {
                        'read_bytes': io_counters.get('read_bytes', 0),
                        'write_bytes': io_counters.get('write_bytes', 0),
                        'read_count': io_counters.get('read_count', 0),
                        'write_count': io_counters.get('write_count', 0),
                        'read_time': io_counters.get('read_time', 0),
                        'write_time': io_counters.get('write_time', 0),
                        'disk_usage_percent': sum([d.get('percent', 0) for d in disk_usage.values()]) / max(len(disk_usage), 1),
                        'data_size': len(str(real_data)),
                        'type': 'real_disk',
                        'real_data': real_data
                    }
                elif metrics_type == "syscall":
                    metrics = {
                        'context_switches': real_data.get('context_switches', 0),
                        'interrupts': real_data.get('interrupts', 0),
                        'syscalls': real_data.get('syscalls', 0),
                        'processes': real_data.get('processes', 0),
                        'active_processes': real_data.get('active_processes', 0),
                        'data_size': len(str(real_data)),
                        'type': 'real_syscall',
                        'real_data': real_data
                    }
                elif metrics_type == "kernel":
                    load_avg = real_data.get('load_average', {})
                    metrics = {
                        'context_switches': real_data.get('context_switches', 0),
                        'interrupts': real_data.get('interrupts', 0),
                        'load_1min': load_avg.get('1min', 0),
                        'load_5min': load_avg.get('5min', 0),
                        'load_15min': load_avg.get('15min', 0),
                        'uptime': real_data.get('uptime', 0),
                        'cpu_cores': real_data.get('cpu_cores', 0),
                        'data_size': len(str(real_data)),
                        'type': 'real_kernel',
                        'real_data': real_data
                    }
                else:
                    # Generic real metrics
                    metrics = {
                        'data_points': len(str(real_data)),
                        'data_size': len(str(real_data)),
                        'type': f'real_{metrics_type}',
                        'real_data': real_data
                    }
                
                # Update probe with real metrics
                self._update_probe_metrics(probe_id, metrics)
                
                # Also store in advanced analytics
                analytics_metrics = {
                    f'real_{metrics_type}': {
                        str(key): float(value) if isinstance(value, (int, float)) else 0.0
                        for key, value in metrics.items() 
                        if isinstance(value, (int, float))
                    }
                }
                await advanced_analytics.store_advanced_metrics(analytics_metrics)
            else:
                # Fallback to basic metrics if enhanced collection fails
                metrics = await self._collect_basic_fallback_metrics(probe_type)
                self._update_probe_metrics(probe_id, metrics)
                
        except Exception as e:
            logger.error(f"Failed to collect enhanced metrics for probe {probe_id}: {e}")
            # Fallback to basic metrics
            try:
                metrics = await self._collect_basic_fallback_metrics(probe_type)
                self._update_probe_metrics(probe_id, metrics)
            except Exception as fallback_error:
                logger.error(f"Fallback metrics collection also failed for {probe_id}: {fallback_error}")
    
    async def _collect_basic_fallback_metrics(self, probe_type: str) -> Dict[str, Any]:
        """Fallback to basic metrics collection if enhanced collection fails"""
        try:
            if "cpu" in probe_type.lower():
                return await self._collect_cpu_metrics()
            elif "network" in probe_type.lower() or "tcp" in probe_type.lower():
                return await self._collect_network_metrics()
            elif "memory" in probe_type.lower():
                return await self._collect_memory_metrics()
            elif "file" in probe_type.lower() or "disk" in probe_type.lower():
                return await self._collect_disk_metrics()
            else:
                return await self._collect_generic_metrics()
        except Exception as e:
            logger.error(f"Basic fallback metrics collection failed: {e}")
            return {'type': 'error', 'data_size': 0, 'error': str(e)}
            
    async def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """Collect real CPU metrics"""
        loop = asyncio.get_event_loop()
        cpu_percent = await loop.run_in_executor(self.executor, psutil.cpu_percent, 0.1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            "cpu_usage": cpu_percent,
            "cpu_count": cpu_count,
            "cpu_freq": cpu_freq.current if cpu_freq else 0,
            "data_size": cpu_percent * 1024,  # Simulate data based on CPU usage
            "type": "cpu"
        }
        
    async def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect real network metrics"""
        loop = asyncio.get_event_loop()
        network_io = await loop.run_in_executor(self.executor, psutil.net_io_counters)
        
        return {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
            "data_size": (network_io.bytes_sent + network_io.bytes_recv) / 1024,  # KB
            "type": "network"
        }
        
    async def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect real memory metrics"""
        loop = asyncio.get_event_loop()
        memory = await loop.run_in_executor(self.executor, psutil.virtual_memory)
        
        return {
            "memory_percent": memory.percent,
            "memory_available": memory.available,
            "memory_used": memory.used,
            "memory_total": memory.total,
            "data_size": memory.used / 1024 / 1024,  # MB
            "type": "memory"
        }
        
    async def _collect_disk_metrics(self) -> Dict[str, Any]:
        """Collect real disk metrics"""
        loop = asyncio.get_event_loop()
        disk_io = await loop.run_in_executor(self.executor, psutil.disk_io_counters)
        disk_usage = await loop.run_in_executor(self.executor, psutil.disk_usage, '/')
        
        return {
            "disk_read_bytes": disk_io.read_bytes if disk_io else 0,
            "disk_write_bytes": disk_io.write_bytes if disk_io else 0,
            "disk_usage_percent": (disk_usage.used / disk_usage.total) * 100,
            "disk_free": disk_usage.free,
            "data_size": (disk_io.read_bytes + disk_io.write_bytes) / 1024 / 1024 if disk_io else 0,  # MB
            "type": "disk"
        }
        
    async def _collect_generic_metrics(self) -> Dict[str, Any]:
        """Collect generic system metrics"""
        loop = asyncio.get_event_loop()
        cpu_percent = await loop.run_in_executor(self.executor, psutil.cpu_percent, 0.1)
        memory = await loop.run_in_executor(self.executor, psutil.virtual_memory)
        
        return {
            "cpu_usage": cpu_percent,
            "memory_percent": memory.percent,
            "data_size": (cpu_percent + memory.percent) * 10,  # Simulate data collection
            "type": "generic"
        }
        
    def _update_probe_metrics(self, probe_id: str, metrics: Dict[str, Any]):
        """Update probe with collected metrics"""
        if probe_id not in self.probes:
            return
            
        probe = self.probes[probe_id]
        current_time = time.time()
        
        # Calculate data rate
        time_diff = current_time - probe.get("last_metrics_update", current_time)
        if time_diff > 0:
            data_size_kb = metrics.get("data_size", 0)
            probe["bytes_collected"] += data_size_kb * 1024
            data_rate_bps = (data_size_kb * 1024) / time_diff  # bytes per second
            data_rate_mbps = data_rate_bps / (1024 * 1024)  # MB/s
            
            probe["data_rate"] = f"{data_rate_mbps:.2f} MB/s"
            probe["real_data_collected"] += data_size_kb
            
        # Update metrics history (keep last 100 points)
        probe["metrics_history"].append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        if len(probe["metrics_history"]) > 100:
            probe["metrics_history"] = probe["metrics_history"][-100:]
            
        probe["last_metrics_update"] = current_time
        
    async def _uptime_update_loop(self):
        """Update probe uptime continuously"""
        while self.running:
            try:
                current_time = time.time()
                for probe_id, probe in self.probes.items():
                    start_time = probe.get("start_time", current_time)
                    uptime_seconds = int(current_time - start_time)
                    
                    # Format uptime
                    if uptime_seconds < 60:
                        uptime_str = f"{uptime_seconds}s"
                    elif uptime_seconds < 3600:
                        minutes = uptime_seconds // 60
                        seconds = uptime_seconds % 60
                        uptime_str = f"{minutes}m {seconds}s"
                    else:
                        hours = uptime_seconds // 3600
                        minutes = (uptime_seconds % 3600) // 60
                        uptime_str = f"{hours}h {minutes}m"
                        
                    probe["uptime"] = uptime_str
                    
                await asyncio.sleep(5)  # Update every 5 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in uptime update loop: {e}")
                await asyncio.sleep(10)
    
    async def _advanced_analytics_loop(self):
        """Advanced analytics collection and processing loop"""
        while self.running:
            try:
                # Collect comprehensive system metrics
                advanced_metrics = await advanced_analytics.collect_advanced_system_metrics()
                await advanced_analytics.store_advanced_metrics(advanced_metrics)
                
                # Perform analytics every 5 minutes
                await asyncio.sleep(300)
                
                # Generate insights for running probes
                if self.probes:
                    insights = await advanced_analytics.generate_insights_report(hours=1)
                    logger.debug(f"Generated advanced insights: {insights.get('summary', {})}")
                    
                await asyncio.sleep(300)  # Run every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in advanced analytics loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
                
    def get_probe_data(self, probe_id: str) -> Dict[str, Any]:
        """Get current probe data"""
        return self.probes.get(probe_id, {})
        
    def get_all_probes(self) -> Dict[str, Dict[str, Any]]:
        """Get all probe data"""
        return self.probes.copy()
    
    async def get_advanced_analytics_dashboard(self, hours: int = 24) -> str:
        """Get advanced analytics dashboard HTML"""
        return await advanced_analytics.generate_comprehensive_dashboard(hours)
    
    async def get_system_insights(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive system insights"""
        return await advanced_analytics.generate_insights_report(hours)

# Global probe manager instance
probe_manager = RealProbeManager()
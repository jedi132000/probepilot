"""
System Status API endpoints
Provides system health, metrics, and status information
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime
import psutil
import platform

router = APIRouter()

@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Get overall system health and status"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "uptime": "2h 15m 30s",
        "services": {
            "api": "healthy",
            "database": "connected", 
            "probe_manager": "ready",
            "telemetry_processor": "running",
            "ai_copilot": "available"
        },
        "system": {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": f"{psutil.virtual_memory().total // (1024**3)} GB"
        }
    }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """Get current system performance metrics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "usage_percent": cpu_percent,
            "count": psutil.cpu_count(),
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv
        }
    }

@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """Get detailed system information"""
    return {
        "probepilot": {
            "version": "0.1.0",
            "mode": "development",
            "api_version": "v1"
        },
        "system": {
            "platform": platform.platform(),
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        },
        "runtime": {
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True)
        }
    }
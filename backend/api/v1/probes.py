"""
Probe Management API endpoints
Handles eBPF probe deployment, monitoring, and lifecycle management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import time
import logging

# Pydantic models for request/response
from pydantic import BaseModel, Field

# Import the real probe manager
from core.probe_manager import probe_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models
class ProbeConfig(BaseModel):
    """Configuration for deploying a new probe"""
    name: str = Field(..., description="Probe name")
    type: str = Field(..., description="Probe type (tcp-flow, cpu-profiler, etc.)")
    target: str = Field(..., description="Target system (hostname or IP)")
    config: Dict[str, Any] = Field(default={}, description="Probe-specific configuration")
    sampling_rate: int = Field(default=1000, description="Sampling rate in Hz")
    filters: List[str] = Field(default=[], description="Data filters")

class ProbeResponse(BaseModel):
    """Response model for probe information"""
    id: str
    name: str
    type: str
    target: str
    status: str
    data_rate: str
    uptime: str
    created_at: str
    config: Dict[str, Any]

class ProbeStatus(BaseModel):
    """Probe status information"""
    id: str
    status: str
    health: str
    last_seen: str
    metrics: Dict[str, Any]

@router.get("/", response_model=List[ProbeResponse])
async def get_active_probes():
    """Get list of all active probes with real-time data"""
    try:
        probes = []
        all_probes = probe_manager.get_all_probes()
        
        for probe_id, probe_data in all_probes.items():
            probes.append(ProbeResponse(
                id=probe_id,
                name=probe_data["name"],
                type=probe_data["type"],
                target=probe_data["target"],
                status=probe_data["status"],
                data_rate=probe_data.get("data_rate", "0.0 MB/s"),
                uptime=probe_data.get("uptime", "0s"),
                created_at=probe_data["created_at"],
                config=probe_data["config"]
            ))
        return probes
    except Exception as e:
        logger.error("Failed to retrieve probes: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active probes"
        )

@router.post("/", response_model=Dict[str, Any])
async def deploy_probe(probe_config: ProbeConfig):
    """Deploy a new eBPF probe with real monitoring"""
    try:
        # Generate unique probe ID
        probe_id = f"probe-{str(uuid.uuid4())[:8]}"
        
        # Initial probe data with "initializing" status
        probe_data = {
            "id": probe_id,
            "name": probe_config.name,
            "type": probe_config.type,
            "target": probe_config.target,
            "status": "initializing",
            "data_rate": "0.0 MB/s",
            "uptime": "0s",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "config": probe_config.config,
            "health": "starting",
            "deployment_stage": "initializing"
        }
        
        # Register with real probe manager for live monitoring
        probe_manager.register_probe(probe_id, probe_data)
        
        logger.info("Deploying real probe %s of type %s to %s", 
                   probe_id, probe_config.type, probe_config.target)
        
        # Return initial response - probe will automatically progress through states
        return {
            "success": True,
            "probe_id": probe_id,
            "message": f"Probe {probe_config.name} deployment initiated with real monitoring",
            "status": "initializing",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to deploy probe: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deploy probe: {str(e)}"
        )

@router.get("/{probe_id}", response_model=ProbeResponse)
async def get_probe(probe_id: str):
    """Get real-time information about a specific probe"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    return ProbeResponse(
        id=probe_id,
        name=probe_data["name"],
        type=probe_data["type"],
        target=probe_data["target"],
        status=probe_data["status"],
        data_rate=probe_data.get("data_rate", "0.0 MB/s"),
        uptime=probe_data.get("uptime", "0s"),
        created_at=probe_data["created_at"],
        config=probe_data["config"]
    )

@router.get("/{probe_id}/status", response_model=ProbeStatus)
async def get_probe_status(probe_id: str):
    """Get detailed real-time status information for a probe"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    # Get latest metrics from history
    metrics_history = probe_data.get("metrics_history", [])
    latest_metrics = metrics_history[-1]["metrics"] if metrics_history else {}
    
    # Build real metrics response
    real_metrics = {
        "data_rate": probe_data.get("data_rate", "0.0 MB/s"),
        "uptime": probe_data.get("uptime", "0s"),
        "total_data_collected": f"{probe_data.get('real_data_collected', 0):.2f} KB",
        "health": probe_data.get("health", "starting")
    }
    
    # Add probe-type specific metrics
    if latest_metrics:
        probe_type = latest_metrics.get("type", "generic")
        if probe_type == "cpu":
            real_metrics.update({
                "cpu_usage": f"{latest_metrics.get('cpu_usage', 0):.1f}%",
                "cpu_count": latest_metrics.get('cpu_count', 0),
                "cpu_frequency": f"{latest_metrics.get('cpu_freq', 0):.0f} MHz"
            })
        elif probe_type == "network":
            real_metrics.update({
                "bytes_sent": f"{latest_metrics.get('bytes_sent', 0)} bytes",
                "bytes_received": f"{latest_metrics.get('bytes_recv', 0)} bytes",
                "packets_sent": latest_metrics.get('packets_sent', 0),
                "packets_received": latest_metrics.get('packets_recv', 0)
            })
        elif probe_type == "memory":
            real_metrics.update({
                "memory_usage": f"{latest_metrics.get('memory_percent', 0):.1f}%",
                "memory_available": f"{latest_metrics.get('memory_available', 0) / 1024 / 1024:.0f} MB",
                "memory_used": f"{latest_metrics.get('memory_used', 0) / 1024 / 1024:.0f} MB"
            })
        elif probe_type == "disk":
            real_metrics.update({
                "disk_usage": f"{latest_metrics.get('disk_usage_percent', 0):.1f}%",
                "disk_read": f"{latest_metrics.get('disk_read_bytes', 0) / 1024 / 1024:.2f} MB",
                "disk_write": f"{latest_metrics.get('disk_write_bytes', 0) / 1024 / 1024:.2f} MB"
            })
    
    return ProbeStatus(
        id=probe_id,
        status=probe_data["status"],
        health=probe_data.get("health", "starting"),
        last_seen=datetime.now().isoformat(),
        metrics=real_metrics
    )

@router.put("/{probe_id}", response_model=Dict[str, Any])
async def update_probe(probe_id: str, probe_config: ProbeConfig):
    """Update probe configuration"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update probe configuration in the manager
        probe_data.update({
            "name": probe_config.name,
            "config": probe_config.config,
            "updated_at": datetime.now().isoformat()
        })
        
        logger.info("Updated configuration for probe %s", probe_id)
        
        return {
            "success": True,
            "probe_id": probe_id,
            "message": "Probe configuration updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to update probe %s: %s", probe_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update probe: {str(e)}"
        )

@router.delete("/{probe_id}", response_model=Dict[str, Any])
async def stop_probe(probe_id: str):
    """Stop and remove a probe"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update status to stopping
        probe_data["status"] = "stopping"
        
        logger.info("Stopping real probe %s", probe_id)
        
        # Remove from probe manager
        probe_manager.unregister_probe(probe_id)
        
        return {
            "success": True,
            "probe_id": probe_id,
            "message": "Probe stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to stop probe %s: %s", probe_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop probe: {str(e)}"
        )

@router.post("/{probe_id}/advance", response_model=Dict[str, Any])
async def advance_probe_state(probe_id: str):
    """Manually advance probe to next deployment state (overrides automatic progression)"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        current_status = probe_data["status"]
        
        # Define state progression
        state_progression = {
            "initializing": "loading",
            "loading": "attaching", 
            "attaching": "running",
            "running": "running",  # Already running
            "error": "initializing",  # Retry from start
            "stopped": "initializing"  # Restart
        }
        
        next_status = state_progression.get(current_status, "error")
        
        # Update probe state in the manager
        await probe_manager._update_probe_state(probe_id, next_status)
        
        logger.info("Manually advanced probe %s from %s to %s", probe_id, current_status, next_status)
        
        return {
            "success": True,
            "probe_id": probe_id,
            "previous_status": current_status,
            "current_status": next_status,
            "message": f"Probe manually advanced from {current_status} to {next_status}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to advance probe %s: %s", probe_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to advance probe state: {str(e)}"
        )

@router.post("/{probe_id}/restart", response_model=Dict[str, Any])
async def restart_probe(probe_id: str):
    """Restart a probe"""
    probe_data = probe_manager.get_probe_data(probe_id)
    if not probe_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update status to restarting
        probe_data["status"] = "restarting"
        
        logger.info("Restarting real probe %s", probe_id)
        
        # Force probe back to initializing to restart the cycle
        await probe_manager._update_probe_state(probe_id, "initializing")
        
        # Reset start time for fresh metrics
        probe_data["start_time"] = time.time()
        probe_data["restarted_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "probe_id": probe_id,
            "message": "Probe restarted successfully - will progress through states again",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to restart probe %s: %s", probe_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart probe: {str(e)}"
        )
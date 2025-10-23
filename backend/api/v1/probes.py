"""
Probe Management API endpoints
Handles eBPF probe deployment, monitoring, and lifecycle management
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging

# Pydantic models for request/response
from pydantic import BaseModel, Field

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

# In-memory storage for demo (replace with actual database)
_active_probes: Dict[str, Dict[str, Any]] = {}

@router.get("/", response_model=List[ProbeResponse])
async def get_active_probes():
    """Get list of all active probes"""
    try:
        probes = []
        for probe_id, probe_data in _active_probes.items():
            probes.append(ProbeResponse(
                id=probe_id,
                name=probe_data["name"],
                type=probe_data["type"],
                target=probe_data["target"],
                status=probe_data["status"],
                data_rate=probe_data["data_rate"],
                uptime=probe_data["uptime"],
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
    """Deploy a new eBPF probe"""
    try:
        # Generate unique probe ID
        probe_id = f"probe-{str(uuid.uuid4())[:8]}"
        
        # Simulate probe deployment
        probe_data = {
            "id": probe_id,
            "name": probe_config.name,
            "type": probe_config.type,
            "target": probe_config.target,
            "status": "deploying",
            "data_rate": "0.0 MB/s",
            "uptime": "0s",
            "created_at": datetime.now().isoformat(),
            "config": probe_config.config
        }
        
        # Store probe information
        _active_probes[probe_id] = probe_data
        
        # Simulate deployment process
        logger.info("Deploying probe %s of type %s to %s", 
                   probe_id, probe_config.type, probe_config.target)
        
        # Update status to running (in real implementation, this would be async)
        _active_probes[probe_id]["status"] = "running"
        _active_probes[probe_id]["data_rate"] = "1.2 MB/s"
        
        return {
            "success": True,
            "probe_id": probe_id,
            "message": f"Probe {probe_config.name} deployed successfully",
            "status": "running",
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
    """Get information about a specific probe"""
    if probe_id not in _active_probes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    probe_data = _active_probes[probe_id]
    return ProbeResponse(
        id=probe_id,
        name=probe_data["name"],
        type=probe_data["type"],
        target=probe_data["target"],
        status=probe_data["status"],
        data_rate=probe_data["data_rate"],
        uptime=probe_data["uptime"],
        created_at=probe_data["created_at"],
        config=probe_data["config"]
    )

@router.get("/{probe_id}/status", response_model=ProbeStatus)
async def get_probe_status(probe_id: str):
    """Get detailed status information for a probe"""
    if probe_id not in _active_probes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    probe_data = _active_probes[probe_id]
    return ProbeStatus(
        id=probe_id,
        status=probe_data["status"],
        health="healthy",
        last_seen=datetime.now().isoformat(),
        metrics={
            "data_rate": probe_data["data_rate"],
            "uptime": probe_data["uptime"],
            "events_processed": 15420,
            "memory_usage": "24.5 MB",
            "cpu_usage": "2.1%"
        }
    )

@router.put("/{probe_id}", response_model=Dict[str, Any])
async def update_probe(probe_id: str, probe_config: ProbeConfig):
    """Update probe configuration"""
    if probe_id not in _active_probes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update probe configuration
        _active_probes[probe_id].update({
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
    if probe_id not in _active_probes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update status to stopping
        _active_probes[probe_id]["status"] = "stopping"
        
        # Simulate stopping process
        logger.info("Stopping probe %s", probe_id)
        
        # Remove from active probes
        del _active_probes[probe_id]
        
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

@router.post("/{probe_id}/restart", response_model=Dict[str, Any])
async def restart_probe(probe_id: str):
    """Restart a probe"""
    if probe_id not in _active_probes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Probe {probe_id} not found"
        )
    
    try:
        # Update status
        _active_probes[probe_id]["status"] = "restarting"
        
        # Simulate restart process
        logger.info("Restarting probe %s", probe_id)
        
        # Update to running
        _active_probes[probe_id]["status"] = "running"
        _active_probes[probe_id]["restarted_at"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "probe_id": probe_id,
            "message": "Probe restarted successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to restart probe %s: %s", probe_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart probe: {str(e)}"
        )
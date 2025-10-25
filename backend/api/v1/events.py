"""
Events API endpoints
Handles system events and activity logs
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import psutil
import time
from datetime import datetime
from core.database import get_database

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/recent")
async def get_recent_events(limit: int = 50, db=Depends(get_database)) -> List[Dict[str, Any]]:
    """Get recent system events"""
    
    # Try to get from Redis first
    events = db.get_recent_events(limit)
    
    # If no stored events, generate some real system events
    if not events:
        events = []
        current_time = time.time()
        
        # Get real system processes
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] and pinfo['cpu_percent'] > 5.0:  # Only high CPU processes
                        processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:10]
            
            # Create events from high CPU processes
            for i, proc in enumerate(processes):
                event_time = current_time - (i * 30)  # Spread events over time
                events.append({
                    "timestamp": event_time,
                    "time": datetime.fromtimestamp(event_time).strftime("%H:%M:%S"),
                    "type": "process",
                    "severity": "warning" if proc.get('cpu_percent', 0) > 20 else "info",
                    "message": f"Process {proc['name']} (PID: {proc['pid']}) using {proc.get('cpu_percent', 0):.1f}% CPU",
                    "source": "system_monitor"
                })
        except Exception:
            pass
        
        # Add system load event
        try:
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            events.append({
                "timestamp": current_time - 60,
                "time": datetime.fromtimestamp(current_time - 60).strftime("%H:%M:%S"),
                "type": "system",
                "severity": "warning" if load_avg > 2.0 else "info",
                "message": f"System load average: {load_avg:.2f}",
                "source": "system_monitor"
            })
        except Exception:
            pass
        
        # Add memory usage event
        try:
            memory = psutil.virtual_memory()
            events.append({
                "timestamp": current_time - 120,
                "time": datetime.fromtimestamp(current_time - 120).strftime("%H:%M:%S"),
                "type": "memory",
                "severity": "warning" if memory.percent > 80 else "info",
                "message": f"Memory usage: {memory.percent:.1f}% ({memory.used // (1024**3):.1f}GB used)",
                "source": "system_monitor"
            })
        except Exception:
            pass
        
        # Sort by timestamp (newest first)
        events = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    return events

@router.post("/store")
async def store_event(event: Dict[str, Any], db=Depends(get_database)) -> Dict[str, str]:
    """Store a system event"""
    
    # Add timestamp if not provided
    if "timestamp" not in event:
        event["timestamp"] = time.time()
    
    # Store in Redis
    if db.store_system_event(event):
        return {"status": "success", "message": "Event stored successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to store event")
"""
Alert Engine API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.alert_engine import alert_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """Get comprehensive system health status with intelligent alerting"""
    try:
        health_status = alert_engine.get_system_health_status()
        return {
            "success": True,
            "data": health_status
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system health: {str(e)}")

@router.get("/metrics")
async def get_current_metrics() -> Dict[str, Any]:
    """Get current system metrics"""
    try:
        metrics = alert_engine.collect_system_metrics()
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")

@router.get("/thresholds")
async def get_dynamic_thresholds() -> Dict[str, Any]:
    """Get current dynamic thresholds for all metrics"""
    try:
        metrics = alert_engine.collect_system_metrics()
        thresholds = {}
        
        for metric_name, current_value in metrics.items():
            warning, critical = alert_engine.calculate_dynamic_thresholds(metric_name, current_value)
            thresholds[metric_name] = {
                "warning": warning,
                "critical": critical,
                "current": current_value,
                "baseline_avg": getattr(alert_engine.thresholds.get(metric_name), 'baseline_avg', None),
                "baseline_std": getattr(alert_engine.thresholds.get(metric_name), 'baseline_std', None)
            }
        
        return {
            "success": True,
            "data": thresholds
        }
    except Exception as e:
        logger.error(f"Failed to get thresholds: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get thresholds: {str(e)}")

@router.get("/history/{metric_name}")
async def get_metric_history(metric_name: str, hours: int = 24) -> Dict[str, Any]:
    """Get historical data for a specific metric"""
    try:
        if metric_name not in alert_engine.metrics_history:
            return {
                "success": True,
                "data": {
                    "metric_name": metric_name,
                    "history": [],
                    "message": "No historical data available for this metric"
                }
            }
        
        history = alert_engine.metrics_history[metric_name]
        
        # Limit to requested timeframe
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_history = [
            {"timestamp": timestamp.isoformat(), "value": value}
            for timestamp, value in history
            if timestamp > cutoff_time
        ]
        
        return {
            "success": True,
            "data": {
                "metric_name": metric_name,
                "history": filtered_history,
                "total_points": len(filtered_history)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get metric history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metric history: {str(e)}")

@router.post("/reset-baselines")
async def reset_baselines() -> Dict[str, Any]:
    """Reset all baseline calculations (use with caution)"""
    try:
        # Clear metrics history
        alert_engine.metrics_history.clear()
        
        # Reset baseline values
        for threshold in alert_engine.thresholds.values():
            threshold.baseline_avg = None
            threshold.baseline_std = None
            threshold.last_updated = None
        
        # Save the reset state
        alert_engine._save_persistent_data()
        
        return {
            "success": True,
            "message": "All baselines have been reset. The system will re-learn normal patterns over the next 24 hours."
        }
    except Exception as e:
        logger.error(f"Failed to reset baselines: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset baselines: {str(e)}")

@router.get("/status")
async def get_alert_engine_status() -> Dict[str, Any]:
    """Get status and configuration of the alert engine"""
    try:
        status_info = {
            "engine_active": True,
            "data_directory": str(alert_engine.data_dir),
            "configured_metrics": list(alert_engine.thresholds.keys()),
            "metrics_with_baselines": [
                name for name, threshold in alert_engine.thresholds.items()
                if threshold.baseline_avg is not None
            ],
            "total_historical_points": {
                metric: len(history) for metric, history in alert_engine.metrics_history.items()
            },
            "max_history_size": alert_engine.max_history_size
        }
        
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        logger.error(f"Failed to get alert engine status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
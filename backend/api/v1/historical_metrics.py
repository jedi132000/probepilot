"""
Historical Metrics API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.historical_metrics import historical_engine, TimeSeriesPoint

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics/historical", tags=["historical-metrics"])

@router.post("/store")
async def store_metric_point(
    metric_name: str,
    value: float,
    timestamp: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Store a single metric data point"""
    try:
        ts = datetime.fromisoformat(timestamp) if timestamp else datetime.now()
        historical_engine.store_metric(metric_name, value, ts, tags)
        
        return {
            "success": True,
            "message": f"Stored metric point for {metric_name}",
            "timestamp": ts.isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to store metric: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store metric: {str(e)}")

@router.post("/store-batch")
async def store_metrics_batch(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Store multiple metric points efficiently"""
    try:
        points = []
        for metric in metrics:
            ts = datetime.fromisoformat(metric.get('timestamp', datetime.now().isoformat()))
            point = TimeSeriesPoint(
                timestamp=ts,
                metric_name=metric['metric_name'],
                value=metric['value'],
                tags=metric.get('tags')
            )
            points.append(point)
        
        historical_engine.store_metrics_batch(points)
        
        return {
            "success": True,
            "message": f"Stored {len(points)} metric points",
            "count": len(points)
        }
    except Exception as e:
        logger.error(f"Failed to store batch metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store batch metrics: {str(e)}")

@router.get("/history/{metric_name}")
async def get_metric_history(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 7 days
    limit: Optional[int] = Query(None, ge=1, le=10000)
) -> Dict[str, Any]:
    """Get historical data for a specific metric"""
    try:
        history = historical_engine.get_metric_history(metric_name, hours, limit)
        
        return {
            "success": True,
            "data": {
                "metric_name": metric_name,
                "points": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "tags": point.tags
                    }
                    for point in history
                ],
                "count": len(history),
                "hours_requested": hours
            }
        }
    except Exception as e:
        logger.error(f"Failed to get history for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@router.get("/baseline/{metric_name}")
async def get_metric_baseline(metric_name: str) -> Dict[str, Any]:
    """Get baseline statistics for a metric"""
    try:
        baseline = historical_engine.get_baseline(metric_name)
        
        if not baseline:
            return {
                "success": True,
                "data": None,
                "message": "No baseline data available for this metric"
            }
        
        return {
            "success": True,
            "data": baseline
        }
    except Exception as e:
        logger.error(f"Failed to get baseline for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get baseline: {str(e)}")

@router.post("/baseline/{metric_name}/calculate")
async def calculate_metric_baseline(
    metric_name: str,
    days: int = Query(7, ge=1, le=30)
) -> Dict[str, Any]:
    """Calculate and store baseline for a metric"""
    try:
        baseline = historical_engine.calculate_baseline(metric_name, days)
        
        if not baseline:
            return {
                "success": False,
                "message": f"Insufficient data to calculate baseline for {metric_name}. Need at least 10 data points."
            }
        
        return {
            "success": True,
            "data": baseline,
            "message": f"Baseline calculated for {metric_name} using {days} days of data"
        }
    except Exception as e:
        logger.error(f"Failed to calculate baseline for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate baseline: {str(e)}")

@router.get("/trend/{metric_name}")
async def get_metric_trend(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """Get trend analysis for a metric"""
    try:
        trend = historical_engine.analyze_trend(metric_name, hours)
        
        if not trend:
            return {
                "success": True,
                "data": None,
                "message": "Insufficient data for trend analysis"
            }
        
        return {
            "success": True,
            "data": {
                "metric_name": trend.metric_name,
                "current_value": trend.current_value,
                "trend_direction": trend.trend_direction,
                "trend_strength": trend.trend_strength,
                "anomaly_score": trend.anomaly_score,
                "baseline_avg": trend.baseline_avg,
                "baseline_std": trend.baseline_std,
                "prediction_24h": trend.prediction_24h
            }
        }
    except Exception as e:
        logger.error(f"Failed to analyze trend for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze trend: {str(e)}")

@router.get("/timeline")
async def get_timeline_chart(
    metrics: str = Query(..., description="Comma-separated list of metric names"),
    hours: int = Query(24, ge=1, le=168)
) -> Dict[str, Any]:
    """Generate timeline chart HTML for multiple metrics"""
    try:
        metric_names = [name.strip() for name in metrics.split(',')]
        
        if len(metric_names) > 10:  # Limit to prevent performance issues
            raise HTTPException(status_code=400, detail="Maximum 10 metrics allowed for timeline chart")
        
        chart_html = historical_engine.generate_timeline_chart(metric_names, hours)
        
        return {
            "success": True,
            "data": {
                "chart_html": chart_html,
                "metrics": metric_names,
                "hours": hours
            }
        }
    except Exception as e:
        logger.error(f"Failed to generate timeline chart: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate timeline: {str(e)}")

@router.get("/heatmap")
async def get_deviation_heatmap(
    metrics: str = Query(..., description="Comma-separated list of metric names"),
    days: int = Query(7, ge=1, le=30)
) -> Dict[str, Any]:
    """Generate deviation heatmap HTML for multiple metrics"""
    try:
        metric_names = [name.strip() for name in metrics.split(',')]
        
        if len(metric_names) > 15:  # Limit to prevent performance issues
            raise HTTPException(status_code=400, detail="Maximum 15 metrics allowed for heatmap")
        
        heatmap_html = historical_engine.generate_deviation_heatmap(metric_names, days)
        
        return {
            "success": True,
            "data": {
                "heatmap_html": heatmap_html,
                "metrics": metric_names,
                "days": days
            }
        }
    except Exception as e:
        logger.error(f"Failed to generate heatmap: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate heatmap: {str(e)}")

@router.get("/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """Get summary of all available metrics and their status"""
    try:
        # Get all unique metric names from the database
        import sqlite3
        conn = sqlite3.connect(historical_engine.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                metric_name,
                COUNT(*) as point_count,
                MIN(timestamp) as first_point,
                MAX(timestamp) as last_point
            FROM metrics
            GROUP BY metric_name
            ORDER BY last_point DESC
        ''')
        
        metrics_info = cursor.fetchall()
        conn.close()
        
        summary = []
        for row in metrics_info:
            metric_name = row[0]
            baseline = historical_engine.get_baseline(metric_name)
            trend = historical_engine.analyze_trend(metric_name, 24)
            
            summary.append({
                "metric_name": metric_name,
                "point_count": row[1],
                "first_point": row[2],
                "last_point": row[3],
                "has_baseline": baseline is not None,
                "baseline_avg": baseline['baseline_avg'] if baseline else None,
                "trend_direction": trend.trend_direction if trend else None,
                "trend_strength": trend.trend_strength if trend else None,
                "anomaly_score": trend.anomaly_score if trend else None
            })
        
        return {
            "success": True,
            "data": {
                "metrics": summary,
                "total_metrics": len(summary)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Query(30, ge=7, le=365)
) -> Dict[str, Any]:
    """Clean up old historical data"""
    try:
        deleted_count = historical_engine.cleanup_old_data(days_to_keep)
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} old records",
            "deleted_count": deleted_count,
            "days_kept": days_to_keep
        }
    except Exception as e:
        logger.error(f"Failed to cleanup data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")
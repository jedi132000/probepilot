"""
Advanced Analytics API endpoints
Provides comprehensive system observability and analytics capabilities
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from core.advanced_analytics import advanced_analytics
from core.probe_manager import probe_manager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard")
async def get_advanced_dashboard(hours: int = Query(24, description="Hours of data to analyze")):
    """Get comprehensive advanced analytics dashboard"""
    try:
        dashboard_html = await advanced_analytics.generate_comprehensive_dashboard(hours)
        return {
            "success": True,
            "dashboard_html": dashboard_html,
            "generated_at": datetime.now().isoformat(),
            "data_period_hours": hours
        }
    except Exception as e:
        logger.error(f"Error generating advanced dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

@router.get("/insights")
async def get_system_insights(hours: int = Query(24, description="Hours of data to analyze")):
    """Get comprehensive system insights and analysis"""
    try:
        insights = await advanced_analytics.generate_insights_report(hours)
        return {
            "success": True,
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.get("/metrics/advanced")
async def get_advanced_metrics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get comprehensive advanced system metrics"""
    try:
        # Collect current advanced metrics
        current_metrics = await advanced_analytics.collect_advanced_system_metrics()
        
        return {
            "success": True,
            "current_metrics": current_metrics,
            "collected_at": datetime.now().isoformat(),
            "categories": list(current_metrics.keys()),
            "total_metrics": sum(len(category_metrics) for category_metrics in current_metrics.values())
        }
    except Exception as e:
        logger.error(f"Error collecting advanced metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect advanced metrics: {str(e)}")

@router.get("/performance/{metric_name}")
async def analyze_metric_performance(
    metric_name: str, 
    hours: int = Query(24, description="Hours of data to analyze")
):
    """Analyze performance patterns for a specific metric"""
    try:
        profile = await advanced_analytics.analyze_performance_patterns(metric_name, hours)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"Insufficient data for metric {metric_name}")
        
        return {
            "success": True,
            "metric_name": metric_name,
            "performance_profile": {
                "baseline_mean": profile.baseline_mean,
                "baseline_std": profile.baseline_std,
                "current_value": profile.current_value,
                "percentile_rank": profile.percentile_rank,
                "trend_direction": profile.trend_direction,
                "trend_strength": profile.trend_strength,
                "anomaly_score": profile.anomaly_score,
                "seasonal_patterns": profile.seasonal_patterns
            },
            "analyzed_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing metric performance for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze metric: {str(e)}")

@router.get("/correlations")
async def get_metric_correlations(
    hours: int = Query(24, description="Hours of data to analyze"),
    metrics: Optional[str] = Query(None, description="Comma-separated list of metrics")
):
    """Get correlation analysis between metrics"""
    try:
        # Use provided metrics or default key metrics
        if metrics:
            metric_names = [m.strip() for m in metrics.split(',')]
        else:
            metric_names = ['usage_percent', 'used_bytes', 'bytes_sent', 'read_bytes', 'write_bytes']
        
        correlations = await advanced_analytics.detect_metric_correlations(metric_names, hours)
        
        return {
            "success": True,
            "correlations": [
                {
                    "metric_a": corr.metric_a,
                    "metric_b": corr.metric_b,
                    "correlation_coefficient": corr.correlation_coefficient,
                    "significance": corr.significance,
                    "relationship_type": corr.relationship_type,
                    "confidence_level": corr.confidence_level
                }
                for corr in correlations
            ],
            "analyzed_metrics": metric_names,
            "total_correlations": len(correlations),
            "analyzed_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing correlations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze correlations: {str(e)}")

@router.get("/predictions/{metric_name}")
async def get_metric_predictions(
    metric_name: str,
    hours_history: int = Query(24, description="Hours of historical data to use")
):
    """Get predictions for a specific metric"""
    try:
        prediction = await advanced_analytics.predict_metric_values(metric_name, hours_history)
        
        if not prediction:
            raise HTTPException(status_code=404, detail=f"Insufficient data for predictions of {metric_name}")
        
        return {
            "success": True,
            "metric_name": metric_name,
            "prediction": {
                "current_value": prediction.current_value,
                "predicted_1h": prediction.predicted_1h,
                "predicted_4h": prediction.predicted_4h,
                "predicted_24h": prediction.predicted_24h,
                "confidence_intervals": prediction.confidence_intervals,
                "prediction_accuracy": prediction.prediction_accuracy,
                "model_type": prediction.model_type
            },
            "predicted_at": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating predictions for {metric_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")

@router.get("/anomalies")
async def detect_anomalies(hours: int = Query(24, description="Hours of data to analyze")):
    """Detect anomaly clusters in system behavior"""
    try:
        anomalies = await advanced_analytics.detect_anomaly_clusters(hours)
        
        return {
            "success": True,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "analysis_period_hours": hours,
            "detected_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to detect anomalies: {str(e)}")

@router.get("/health/comprehensive")
async def get_comprehensive_health():
    """Get comprehensive system health analysis"""
    try:
        # Get advanced metrics
        current_metrics = await advanced_analytics.collect_advanced_system_metrics()
        
        # Get system insights (limited to 1 hour for real-time health)
        insights = await advanced_analytics.generate_insights_report(hours=1)
        
        # Calculate comprehensive health scores
        health_analysis = {
            "overall_health_score": current_metrics.get('performance', {}).get('system_health_score', 50),
            "component_health": {
                "cpu": {
                    "score": max(0, 100 - current_metrics.get('cpu', {}).get('usage_percent', 0)),
                    "status": "healthy" if current_metrics.get('cpu', {}).get('usage_percent', 0) < 70 else "warning" if current_metrics.get('cpu', {}).get('usage_percent', 0) < 90 else "critical",
                    "metrics": current_metrics.get('cpu', {})
                },
                "memory": {
                    "score": max(0, 100 - (current_metrics.get('memory', {}).get('used_bytes', 0) / current_metrics.get('memory', {}).get('total_bytes', 1) * 100)),
                    "status": "healthy" if (current_metrics.get('memory', {}).get('used_bytes', 0) / current_metrics.get('memory', {}).get('total_bytes', 1) * 100) < 70 else "warning" if (current_metrics.get('memory', {}).get('used_bytes', 0) / current_metrics.get('memory', {}).get('total_bytes', 1) * 100) < 90 else "critical",
                    "metrics": current_metrics.get('memory', {})
                },
                "disk": {
                    "score": max(0, 100 - current_metrics.get('disk', {}).get('usage_percent', 0)),
                    "status": "healthy" if current_metrics.get('disk', {}).get('usage_percent', 0) < 80 else "warning" if current_metrics.get('disk', {}).get('usage_percent', 0) < 95 else "critical",
                    "metrics": current_metrics.get('disk', {})
                },
                "network": {
                    "score": max(0, 100 - (current_metrics.get('performance', {}).get('network_saturation', 0) * 100)),
                    "status": "healthy" if current_metrics.get('performance', {}).get('network_saturation', 0) < 0.7 else "warning" if current_metrics.get('performance', {}).get('network_saturation', 0) < 0.9 else "critical",
                    "metrics": current_metrics.get('network', {})
                }
            },
            "anomalies_detected": len(insights.get('anomalies', [])),
            "recommendations": insights.get('recommendations', []),
            "data_quality_score": insights.get('summary', {}).get('data_quality_score', 50),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "health_analysis": health_analysis,
            "insights_summary": insights.get('summary', {}),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating comprehensive health analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate health analysis: {str(e)}")

@router.post("/collect")
async def trigger_metrics_collection():
    """Manually trigger advanced metrics collection"""
    try:
        # Collect and store advanced metrics
        current_metrics = await advanced_analytics.collect_advanced_system_metrics()
        await advanced_analytics.store_advanced_metrics(current_metrics)
        
        return {
            "success": True,
            "message": "Advanced metrics collection completed",
            "metrics_collected": sum(len(category_metrics) for category_metrics in current_metrics.values()),
            "categories": list(current_metrics.keys()),
            "collected_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to collect metrics: {str(e)}")

@router.get("/probe-insights/{probe_id}")
async def get_probe_specific_insights(probe_id: str):
    """Get advanced insights specific to a probe"""
    try:
        # Get probe data
        probe_data = probe_manager.get_probe_data(probe_id)
        if not probe_data:
            raise HTTPException(status_code=404, detail=f"Probe {probe_id} not found")
        
        # Get probe's metrics history
        metrics_history = probe_data.get("metrics_history", [])
        
        if not metrics_history:
            return {
                "success": True,
                "probe_id": probe_id,
                "message": "No metrics history available for analysis",
                "basic_info": {
                    "name": probe_data.get("name"),
                    "type": probe_data.get("type"),
                    "status": probe_data.get("status"),
                    "uptime": probe_data.get("uptime")
                }
            }
        
        # Analyze probe-specific patterns
        latest_metrics = metrics_history[-1]["metrics"] if metrics_history else {}
        probe_type = latest_metrics.get("type", "unknown")
        
        # Generate probe-specific insights
        probe_insights = {
            "probe_id": probe_id,
            "probe_type": probe_type,
            "current_performance": latest_metrics,
            "data_collection_rate": probe_data.get("data_rate", "0.0 MB/s"),
            "total_data_collected": f"{probe_data.get('real_data_collected', 0):.2f} KB",
            "health_status": probe_data.get("health", "unknown"),
            "uptime": probe_data.get("uptime", "0s"),
            "metrics_trend": "stable",  # Could be enhanced with trend analysis
            "recommendations": []
        }
        
        # Add probe-type specific insights
        if probe_type == "cpu":
            cpu_usage = latest_metrics.get("cpu_usage", 0)
            if cpu_usage > 80:
                probe_insights["recommendations"].append("High CPU usage detected - consider investigating top processes")
        elif probe_type == "memory":
            memory_percent = latest_metrics.get("memory_percent", 0)
            if memory_percent > 85:
                probe_insights["recommendations"].append("High memory usage - check for memory leaks or increase available memory")
        elif probe_type == "network":
            bytes_rate = latest_metrics.get("data_size", 0)
            if bytes_rate > 1000:  # 1MB+ 
                probe_insights["recommendations"].append("High network activity detected - monitor for unusual traffic patterns")
        
        return {
            "success": True,
            "probe_insights": probe_insights,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating probe insights for {probe_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate probe insights: {str(e)}")
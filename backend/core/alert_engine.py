"""
Advanced Alert Engine for ProbePilot
Implements dynamic thresholding, baseline learning, and intelligent alerting
"""

import psutil
import time
import json
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics
import logging

logger = logging.getLogger(__name__)

@dataclass
class AlertThreshold:
    """Dynamic alert threshold configuration"""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    baseline_avg: Optional[float] = None
    baseline_std: Optional[float] = None
    adaptive: bool = True
    last_updated: datetime = None

@dataclass
class SystemAlert:
    """System alert with metadata"""
    alert_id: str
    severity: str  # info, warning, critical
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    baseline_deviation: Optional[float] = None
    suggested_actions: List[str] = None

class AlertEngine:
    """Advanced alerting engine with baseline learning and dynamic thresholds"""
    
    def __init__(self, data_dir: str = "/tmp/probepilot_alerts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize thresholds with production-ready defaults
        self.thresholds = {
            'cpu_percent': AlertThreshold('cpu_percent', 70.0, 85.0, adaptive=True),
            'memory_percent': AlertThreshold('memory_percent', 75.0, 90.0, adaptive=True),
            'disk_percent': AlertThreshold('disk_percent', 80.0, 95.0, adaptive=False),
            'network_in_mbps': AlertThreshold('network_in_mbps', 100.0, 500.0, adaptive=True),
            'network_out_mbps': AlertThreshold('network_out_mbps', 100.0, 500.0, adaptive=True),
            'load_average': AlertThreshold('load_average', 2.0, 4.0, adaptive=True),
        }
        
        # Historical data for baseline calculation
        self.metrics_history = {}
        self.max_history_size = 1440  # 24 hours at 1 minute intervals
        
        # Active alerts
        self.active_alerts = {}
        
        # Load existing data
        self._load_persistent_data()
        
    def _load_persistent_data(self):
        """Load historical data and thresholds from disk"""
        try:
            # Load thresholds
            threshold_file = self.data_dir / "thresholds.json"
            if threshold_file.exists():
                with open(threshold_file, 'r') as f:
                    data = json.load(f)
                    for name, thresh_data in data.items():
                        if name in self.thresholds:
                            # Update threshold with saved data
                            self.thresholds[name].baseline_avg = thresh_data.get('baseline_avg')
                            self.thresholds[name].baseline_std = thresh_data.get('baseline_std')
                            self.thresholds[name].last_updated = datetime.fromisoformat(
                                thresh_data['last_updated']
                            ) if thresh_data.get('last_updated') else None
            
            # Load metrics history
            history_file = self.data_dir / "metrics_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                    # Convert timestamps back to datetime objects
                    for metric_name, history in history_data.items():
                        self.metrics_history[metric_name] = [
                            (datetime.fromisoformat(timestamp), value)
                            for timestamp, value in history
                        ]
                        
        except Exception as e:
            logger.warning(f"Failed to load persistent alert data: {e}")
    
    def _save_persistent_data(self):
        """Save historical data and thresholds to disk"""
        try:
            # Save thresholds
            threshold_data = {}
            for name, threshold in self.thresholds.items():
                threshold_data[name] = {
                    'baseline_avg': threshold.baseline_avg,
                    'baseline_std': threshold.baseline_std,
                    'last_updated': threshold.last_updated.isoformat() if threshold.last_updated else None
                }
            
            with open(self.data_dir / "thresholds.json", 'w') as f:
                json.dump(threshold_data, f, indent=2)
            
            # Save metrics history (convert datetime to string)
            history_data = {}
            for metric_name, history in self.metrics_history.items():
                history_data[metric_name] = [
                    (timestamp.isoformat(), value)
                    for timestamp, value in history[-self.max_history_size:]  # Keep only recent data
                ]
            
            with open(self.data_dir / "metrics_history.json", 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save persistent alert data: {e}")
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        try:
            # Get network baseline
            net_before = psutil.net_io_counters()
            time.sleep(0.1)  # Small interval for network rate calculation
            net_after = psutil.net_io_counters()
            
            # Calculate network rates (Mbps)
            net_in_mbps = ((net_after.bytes_recv - net_before.bytes_recv) * 8 * 10) / (1024 * 1024)
            net_out_mbps = ((net_after.bytes_sent - net_before.bytes_sent) * 8 * 10) / (1024 * 1024)
            
            metrics = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'network_in_mbps': max(0, net_in_mbps),
                'network_out_mbps': max(0, net_out_mbps),
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def update_baselines(self, metrics: Dict[str, float]):
        """Update baseline statistics with new metrics"""
        current_time = datetime.now()
        
        for metric_name, value in metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []
            
            # Add new measurement
            self.metrics_history[metric_name].append((current_time, value))
            
            # Keep only recent history
            cutoff_time = current_time - timedelta(hours=24)
            self.metrics_history[metric_name] = [
                (timestamp, val) for timestamp, val in self.metrics_history[metric_name]
                if timestamp > cutoff_time
            ]
            
            # Update baseline if we have enough data
            if len(self.metrics_history[metric_name]) >= 20:  # Minimum 20 data points
                values = [val for _, val in self.metrics_history[metric_name]]
                
                if metric_name in self.thresholds and self.thresholds[metric_name].adaptive:
                    threshold = self.thresholds[metric_name]
                    threshold.baseline_avg = statistics.mean(values)
                    threshold.baseline_std = statistics.stdev(values) if len(values) > 1 else 0
                    threshold.last_updated = current_time
    
    def calculate_dynamic_thresholds(self, metric_name: str, current_value: float) -> Tuple[float, float]:
        """Calculate dynamic warning and critical thresholds based on baseline"""
        if metric_name not in self.thresholds:
            return 80.0, 95.0  # Default thresholds
        
        threshold = self.thresholds[metric_name]
        
        if not threshold.adaptive or threshold.baseline_avg is None:
            return threshold.warning_threshold, threshold.critical_threshold
        
        # Dynamic thresholds based on baseline + standard deviations
        baseline_avg = threshold.baseline_avg
        baseline_std = threshold.baseline_std or 5.0  # Default std if none
        
        # Warning: baseline + 2 std devs, Critical: baseline + 3 std devs
        dynamic_warning = min(baseline_avg + (2 * baseline_std), threshold.critical_threshold - 5)
        dynamic_critical = min(baseline_avg + (3 * baseline_std), 98.0)  # Never exceed 98%
        
        # Ensure minimums for safety
        dynamic_warning = max(dynamic_warning, threshold.warning_threshold * 0.7)
        dynamic_critical = max(dynamic_critical, threshold.critical_threshold * 0.8)
        
        return dynamic_warning, dynamic_critical
    
    def analyze_metrics_and_generate_alerts(self, metrics: Dict[str, float]) -> List[SystemAlert]:
        """Analyze metrics and generate intelligent alerts"""
        alerts = []
        current_time = datetime.now()
        
        for metric_name, current_value in metrics.items():
            if metric_name not in self.thresholds:
                continue
            
            warning_threshold, critical_threshold = self.calculate_dynamic_thresholds(
                metric_name, current_value
            )
            
            # Calculate baseline deviation if available
            baseline_deviation = None
            if (metric_name in self.thresholds and 
                self.thresholds[metric_name].baseline_avg is not None):
                baseline_avg = self.thresholds[metric_name].baseline_avg
                baseline_std = self.thresholds[metric_name].baseline_std or 1.0
                baseline_deviation = (current_value - baseline_avg) / baseline_std
            
            # Generate alerts based on thresholds
            alert_id = f"{metric_name}_{int(time.time())}"
            
            if current_value >= critical_threshold:
                alert = SystemAlert(
                    alert_id=alert_id,
                    severity='critical',
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=critical_threshold,
                    message=self._generate_alert_message(metric_name, current_value, 'critical'),
                    timestamp=current_time,
                    baseline_deviation=baseline_deviation,
                    suggested_actions=self._get_suggested_actions(metric_name, 'critical')
                )
                alerts.append(alert)
                self.active_alerts[alert_id] = alert
                
            elif current_value >= warning_threshold:
                alert = SystemAlert(
                    alert_id=alert_id,
                    severity='warning',
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=warning_threshold,
                    message=self._generate_alert_message(metric_name, current_value, 'warning'),
                    timestamp=current_time,
                    baseline_deviation=baseline_deviation,
                    suggested_actions=self._get_suggested_actions(metric_name, 'warning')
                )
                alerts.append(alert)
                self.active_alerts[alert_id] = alert
            
            # Check for significant baseline deviation even if not threshold alert
            elif (baseline_deviation is not None and abs(baseline_deviation) > 2.5):
                alert = SystemAlert(
                    alert_id=alert_id,
                    severity='info',
                    metric_name=metric_name,
                    current_value=current_value,
                    threshold_value=warning_threshold,
                    message=f"{metric_name.replace('_', ' ').title()} showing unusual pattern: {current_value:.1f}% (baseline deviation: {baseline_deviation:.1f}σ)",
                    timestamp=current_time,
                    baseline_deviation=baseline_deviation,
                    suggested_actions=self._get_suggested_actions(metric_name, 'info')
                )
                alerts.append(alert)
        
        return alerts
    
    def _generate_alert_message(self, metric_name: str, value: float, severity: str) -> str:
        """Generate human-readable alert messages"""
        metric_display = metric_name.replace('_', ' ').title()
        
        if severity == 'critical':
            return f"🚨 CRITICAL: {metric_display} at {value:.1f}% - Immediate attention required"
        elif severity == 'warning':
            return f"⚠️ WARNING: {metric_display} elevated at {value:.1f}% - Monitor closely"
        else:
            return f"ℹ️ INFO: {metric_display} anomaly detected at {value:.1f}%"
    
    def _get_suggested_actions(self, metric_name: str, severity: str) -> List[str]:
        """Get suggested remediation actions"""
        actions = {
            'cpu_percent': {
                'critical': [
                    "Identify high-CPU processes with 'top' or 'htop'",
                    "Consider killing non-essential processes",
                    "Scale horizontally if this is a persistent issue",
                    "Check for CPU-intensive background tasks"
                ],
                'warning': [
                    "Monitor CPU trends over next 5-10 minutes",
                    "Review recent deployments or batch jobs",
                    "Check process CPU usage with 'ps aux --sort=-%cpu'"
                ],
                'info': [
                    "Document current workload for baseline analysis",
                    "Consider CPU profiling for optimization"
                ]
            },
            'memory_percent': {
                'critical': [
                    "Restart memory-intensive applications",
                    "Clear system caches if safe to do so",
                    "Check for memory leaks in applications",
                    "Consider adding more RAM or horizontal scaling"
                ],
                'warning': [
                    "Monitor memory trends closely",
                    "Review application memory usage patterns",
                    "Check for growing processes with 'ps aux --sort=-%mem'"
                ],
                'info': [
                    "Document memory usage patterns",
                    "Consider memory optimization opportunities"
                ]
            },
            'disk_percent': {
                'critical': [
                    "Clean up temporary files and logs immediately",
                    "Move or archive large files",
                    "Clear package caches",
                    "Consider disk expansion"
                ],
                'warning': [
                    "Identify large files and directories with 'du -sh *'",
                    "Review log rotation policies",
                    "Clean up old backups or archives"
                ],
                'info': [
                    "Monitor disk usage trends",
                    "Plan for storage capacity expansion"
                ]
            }
        }
        
        return actions.get(metric_name, {}).get(severity, ["Monitor the situation closely"])
    
    def get_system_health_status(self) -> Dict:
        """Get overall system health status"""
        metrics = self.collect_system_metrics()
        
        if not metrics:
            return {
                'status': 'unknown',
                'message': 'Unable to collect system metrics',
                'alerts': [],
                'metrics': {}
            }
        
        # Store metrics in historical database
        try:
            from .historical_metrics import historical_engine, TimeSeriesPoint
            current_time = datetime.now()
            
            # Store all metrics as time series points
            points = [
                TimeSeriesPoint(timestamp=current_time, metric_name=name, value=value)
                for name, value in metrics.items()
            ]
            historical_engine.store_metrics_batch(points)
            
            # Calculate baselines for metrics that don't have them
            for metric_name in metrics.keys():
                baseline = historical_engine.get_baseline(metric_name)
                if not baseline:
                    # Try to calculate baseline if we have enough data
                    historical_engine.calculate_baseline(metric_name, days=1)  # Use shorter period initially
                    
        except Exception as e:
            logger.warning(f"Failed to store historical metrics: {e}")
        
        # Update baselines
        self.update_baselines(metrics)
        
        # Generate alerts
        alerts = self.analyze_metrics_and_generate_alerts(metrics)
        
        # Determine overall status
        if any(alert.severity == 'critical' for alert in alerts):
            status = 'critical'
            message = f"System requires immediate attention - {len([a for a in alerts if a.severity == 'critical'])} critical alerts"
        elif any(alert.severity == 'warning' for alert in alerts):
            status = 'warning'
            message = f"System needs monitoring - {len([a for a in alerts if a.severity == 'warning'])} warnings"
        elif alerts:
            status = 'info'
            message = f"System running normally with {len(alerts)} informational notices"
        else:
            status = 'healthy'
            message = "All systems operating within normal parameters"
        
        # Save persistent data
        self._save_persistent_data()
        
        return {
            'status': status,
            'message': message,
            'alerts': [asdict(alert) for alert in alerts],
            'metrics': metrics,
            'thresholds': {
                name: {
                    'warning': self.calculate_dynamic_thresholds(name, metrics.get(name, 0))[0],
                    'critical': self.calculate_dynamic_thresholds(name, metrics.get(name, 0))[1],
                    'baseline_avg': thresh.baseline_avg,
                    'baseline_std': thresh.baseline_std
                }
                for name, thresh in self.thresholds.items()
            }
        }

# Global alert engine instance
alert_engine = AlertEngine()
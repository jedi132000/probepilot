"""
Advanced Analytics Engine for ProbePilot
Provides comprehensive system observability with deep analytical capabilities
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from scipy import stats
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import logging
import json
import sqlite3
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

logger = logging.getLogger(__name__)

@dataclass
class SystemEvent:
    """Represents a system event for analysis"""
    timestamp: datetime
    event_type: str
    severity: str  # 'info', 'warning', 'critical'
    source: str
    message: str
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None

@dataclass
class PerformanceProfile:
    """System performance profile"""
    metric_name: str
    baseline_mean: float
    baseline_std: float
    current_value: float
    percentile_rank: float
    trend_direction: str
    trend_strength: float
    anomaly_score: float
    seasonal_patterns: List[float]
    
@dataclass
class CorrelationInsight:
    """Correlation analysis result"""
    metric_a: str
    metric_b: str
    correlation_coefficient: float
    significance: float
    relationship_type: str  # 'positive', 'negative', 'none'
    confidence_level: float

@dataclass
class PredictionResult:
    """Prediction analysis result"""
    metric_name: str
    current_value: float
    predicted_1h: float
    predicted_4h: float
    predicted_24h: float
    confidence_intervals: Dict[str, Tuple[float, float]]
    prediction_accuracy: float
    model_type: str

class AdvancedAnalyticsEngine:
    """Advanced analytics engine for deep system observability"""
    
    def __init__(self, db_path: str = "/tmp/probepilot_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self.scaler = StandardScaler()
        self.analysis_cache = {}
        
    def _init_database(self):
        """Initialize advanced analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # System events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata TEXT,
                correlation_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                profile_data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_name)
            )
        ''')
        
        # Correlation analysis table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS correlation_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_a TEXT NOT NULL,
                metric_b TEXT NOT NULL,
                analysis_result TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_a, metric_b)
            )
        ''')
        
        # Advanced metrics table for deeper observability
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS advanced_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT,
                process_info TEXT,
                syscall_info TEXT,
                kernel_context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON system_events(event_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_advanced_metrics_timestamp ON advanced_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_advanced_metrics_category ON advanced_metrics(metric_category)')
        
        conn.commit()
        conn.close()
    
    async def collect_advanced_system_metrics(self) -> Dict[str, Dict[str, float]]:
        """Collect comprehensive system metrics beyond basic psutil (safe version)"""
        import psutil
        import os
        import time
        
        metrics = {
            'cpu': {},
            'memory': {},
            'network': {},
            'disk': {},
            'process': {},
            'kernel': {},
            'performance': {}
        }
        
        try:
            # Advanced CPU metrics
            cpu_times = psutil.cpu_times()
            cpu_stats = psutil.cpu_stats()
            
            metrics['cpu'].update({
                'usage_percent': psutil.cpu_percent(interval=0.1),
                'user_time': cpu_times.user,
                'system_time': cpu_times.system,
                'idle_time': cpu_times.idle,
                'iowait_time': getattr(cpu_times, 'iowait', 0),
                'irq_time': getattr(cpu_times, 'irq', 0),
                'softirq_time': getattr(cpu_times, 'softirq', 0),
                'ctx_switches': cpu_stats.ctx_switches,
                'interrupts': cpu_stats.interrupts,
                'soft_interrupts': cpu_stats.soft_interrupts,
                'syscalls': cpu_stats.syscalls,
                'load_avg_1m': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0,
                'load_avg_5m': os.getloadavg()[1] if hasattr(os, 'getloadavg') else 0,
                'load_avg_15m': os.getloadavg()[2] if hasattr(os, 'getloadavg') else 0,
            })
            
            # Advanced memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics['memory'].update({
                'total_bytes': memory.total,
                'available_bytes': memory.available,
                'used_bytes': memory.used,
                'free_bytes': memory.free,
                'active_bytes': getattr(memory, 'active', 0),
                'inactive_bytes': getattr(memory, 'inactive', 0),
                'buffers_bytes': getattr(memory, 'buffers', 0),
                'cached_bytes': getattr(memory, 'cached', 0),
                'shared_bytes': getattr(memory, 'shared', 0),
                'slab_bytes': getattr(memory, 'slab', 0),
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent,
                'page_faults': getattr(memory, 'page_faults', 0),
                'major_page_faults': getattr(memory, 'major_page_faults', 0),
            })
            
            # Advanced network metrics
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            metrics['network'].update({
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout,
                'active_connections': net_connections,
                'tcp_retransmits': getattr(net_io, 'tcp_retransmits', 0),
            })
            
            # Advanced disk metrics
            disk_io = psutil.disk_io_counters()
            disk_usage = psutil.disk_usage('/')
            
            metrics['disk'].update({
                'read_count': disk_io.read_count if disk_io else 0,
                'write_count': disk_io.write_count if disk_io else 0,
                'read_bytes': disk_io.read_bytes if disk_io else 0,
                'write_bytes': disk_io.write_bytes if disk_io else 0,
                'read_time': disk_io.read_time if disk_io else 0,
                'write_time': disk_io.write_time if disk_io else 0,
                'busy_time': getattr(disk_io, 'busy_time', 0) if disk_io else 0,
                'usage_percent': (disk_usage.used / disk_usage.total) * 100,
                'free_bytes': disk_usage.free,
                'total_bytes': disk_usage.total,
                'inodes_total': getattr(disk_usage, 'inodes_total', 0),
                'inodes_free': getattr(disk_usage, 'inodes_free', 0),
            })
            
            # Process-level metrics (top processes by resource usage)
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and get top 5
            top_cpu_procs = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]
            top_mem_procs = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]
            
            metrics['process'].update({
                'total_processes': len(processes),
                'running_processes': len([p for p in processes if p.get('status') == 'running']),
                'sleeping_processes': len([p for p in processes if p.get('status') == 'sleeping']),
                'zombie_processes': len([p for p in processes if p.get('status') == 'zombie']),
                'top_cpu_usage': sum(p.get('cpu_percent', 0) for p in top_cpu_procs),
                'top_memory_usage': sum(p.get('memory_percent', 0) for p in top_mem_procs),
            })
            
            # Kernel-level metrics (simulate eBPF-style data)
            metrics['kernel'].update({
                'open_files': len(psutil.Process().open_files()) if hasattr(psutil.Process(), 'open_files') else 0,
                'threads': psutil.Process().num_threads(),
                'uptime_seconds': time.time() - psutil.boot_time(),
            })
            
            # Performance derived metrics
            metrics['performance'].update({
                'memory_pressure': max(0, (memory.percent - 70) / 30),  # 0-1 scale above 70%
                'cpu_pressure': max(0, (metrics['cpu']['usage_percent'] - 80) / 20),  # 0-1 scale above 80%
                'io_pressure': max(0, min(1, (metrics['disk']['read_bytes'] + metrics['disk']['write_bytes']) / (100 * 1024 * 1024))),  # 0-1 scale for 100MB/s max
                'network_saturation': max(0, min(1, (metrics['network']['bytes_sent'] + metrics['network']['bytes_recv']) / (1024 * 1024 * 1024))),  # 0-1 scale for 1GB/s max
                'system_health_score': self._calculate_system_health_score(metrics),
            })
            
        except Exception as e:
            logger.error(f"Error collecting advanced metrics: {e}")
            
        return metrics
    
    def _calculate_system_health_score(self, metrics: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            # Weight different components
            cpu_score = max(0, 100 - metrics.get('cpu', {}).get('usage_percent', 0))
            
            # Calculate memory score properly
            memory_used = metrics.get('memory', {}).get('used_bytes', 0)
            memory_total = metrics.get('memory', {}).get('total_bytes', 1)
            memory_percent = (memory_used / memory_total) * 100 if memory_total > 0 else 0
            memory_score = max(0, 100 - memory_percent)
            
            disk_score = max(0, 100 - metrics.get('disk', {}).get('usage_percent', 0))
            
            # Weighted average
            health_score = (cpu_score * 0.3 + memory_score * 0.4 + disk_score * 0.3)
            return min(100, max(0, health_score))
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 50.0  # Default neutral score
    
    async def store_advanced_metrics(self, metrics: Dict[str, Dict[str, float]], timestamp: Optional[datetime] = None):
        """Store advanced metrics in database"""
        if timestamp is None:
            timestamp = datetime.now()
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for category, category_metrics in metrics.items():
                for metric_name, value in category_metrics.items():
                    cursor.execute('''
                        INSERT INTO advanced_metrics 
                        (timestamp, metric_category, metric_name, value, tags)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        timestamp.isoformat(),
                        category,
                        metric_name,
                        value,
                        json.dumps({'category': category, 'timestamp': timestamp.isoformat()})
                    ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing advanced metrics: {e}")
        finally:
            conn.close()
    
    async def analyze_performance_patterns(self, metric_name: str, hours: int = 24) -> Optional[PerformanceProfile]:
        """Analyze performance patterns for a metric"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            query = '''
                SELECT timestamp, value FROM advanced_metrics
                WHERE metric_name = ? AND datetime(timestamp) >= datetime(?)
                ORDER BY timestamp
            '''
            
            df = pd.read_sql_query(query, conn, params=[metric_name, since_time.isoformat()])
            
            if len(df) < 10:
                return None
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            values = df['value'].values
            
            # Statistical analysis
            baseline_mean = np.mean(values)
            baseline_std = np.std(values)
            current_value = values[-1]
            percentile_rank = stats.percentileofscore(values, current_value)
            
            # Trend analysis
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            trend_direction = 'stable'
            if abs(r_value) > 0.3:  # Significant correlation
                trend_direction = 'increasing' if slope > 0 else 'decreasing'
            
            trend_strength = abs(r_value)
            
            # Anomaly detection using Z-score
            z_score = abs(current_value - baseline_mean) / baseline_std if baseline_std > 0 else 0
            anomaly_score = min(z_score / 3.0, 1.0)  # Normalize to 0-1
            
            # Seasonal pattern detection (hourly patterns)
            df['hour'] = df['timestamp'].dt.hour
            hourly_patterns = df.groupby('hour')['value'].mean().values.tolist()
            
            profile = PerformanceProfile(
                metric_name=metric_name,
                baseline_mean=baseline_mean,
                baseline_std=baseline_std,
                current_value=current_value,
                percentile_rank=percentile_rank,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                anomaly_score=anomaly_score,
                seasonal_patterns=hourly_patterns
            )
            
            # Store profile
            await self._store_performance_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error analyzing performance patterns for {metric_name}: {e}")
            return None
        finally:
            conn.close()
    
    async def _store_performance_profile(self, profile: PerformanceProfile):
        """Store performance profile in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO performance_profiles 
                (metric_name, profile_data)
                VALUES (?, ?)
            ''', (profile.metric_name, json.dumps(asdict(profile))))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error storing performance profile: {e}")
        finally:
            conn.close()
    
    async def detect_metric_correlations(self, metric_names: List[str], hours: int = 24) -> List[CorrelationInsight]:
        """Detect correlations between metrics"""
        conn = sqlite3.connect(self.db_path)
        correlations = []
        
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            # Get data for all metrics
            metric_data = {}
            for metric_name in metric_names:
                query = '''
                    SELECT timestamp, value FROM advanced_metrics
                    WHERE metric_name = ? AND datetime(timestamp) >= datetime(?)
                    ORDER BY timestamp
                '''
                
                df = pd.read_sql_query(query, conn, params=[metric_name, since_time.isoformat()])
                if len(df) > 10:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    metric_data[metric_name] = df
            
            # Calculate correlations between all pairs
            for i, metric_a in enumerate(metric_names):
                for metric_b in metric_names[i+1:]:
                    if metric_a in metric_data and metric_b in metric_data:
                        correlation = await self._calculate_correlation(metric_data[metric_a], metric_data[metric_b])
                        if correlation:
                            correlations.append(correlation)
            
        except Exception as e:
            logger.error(f"Error detecting correlations: {e}")
        finally:
            conn.close()
            
        return correlations
    
    async def _calculate_correlation(self, df_a: pd.DataFrame, df_b: pd.DataFrame) -> Optional[CorrelationInsight]:
        """Calculate correlation between two metric datasets"""
        try:
            # Align timestamps (use common time range)
            common_start = max(df_a['timestamp'].min(), df_b['timestamp'].min())
            common_end = min(df_a['timestamp'].max(), df_b['timestamp'].max())
            
            df_a_filtered = df_a[(df_a['timestamp'] >= common_start) & (df_a['timestamp'] <= common_end)]
            df_b_filtered = df_b[(df_b['timestamp'] >= common_start) & (df_b['timestamp'] <= common_end)]
            
            if len(df_a_filtered) < 10 or len(df_b_filtered) < 10:
                return None
            
            # Resample to common frequency (1-minute intervals)
            df_a_resampled = df_a_filtered.set_index('timestamp').resample('1T').mean().dropna()
            df_b_resampled = df_b_filtered.set_index('timestamp').resample('1T').mean().dropna()
            
            # Find common timestamps
            common_timestamps = df_a_resampled.index.intersection(df_b_resampled.index)
            
            if len(common_timestamps) < 10:
                return None
            
            values_a = df_a_resampled.loc[common_timestamps, 'value']
            values_b = df_b_resampled.loc[common_timestamps, 'value']
            
            # Calculate Pearson correlation
            corr_coeff, p_value = stats.pearsonr(values_a, values_b)
            
            # Determine relationship type and confidence
            if abs(corr_coeff) < 0.3:
                relationship_type = 'none'
            else:
                relationship_type = 'positive' if corr_coeff > 0 else 'negative'
            
            confidence_level = 1 - p_value if not np.isnan(p_value) else 0.5
            
            return CorrelationInsight(
                metric_a=df_a_filtered.iloc[0]['timestamp'] if 'timestamp' in df_a_filtered else 'unknown_a',
                metric_b=df_b_filtered.iloc[0]['timestamp'] if 'timestamp' in df_b_filtered else 'unknown_b',
                correlation_coefficient=corr_coeff,
                significance=p_value if not np.isnan(p_value) else 1.0,
                relationship_type=relationship_type,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return None
    
    async def predict_metric_values(self, metric_name: str, hours_history: int = 24) -> Optional[PredictionResult]:
        """Predict future metric values using time series analysis"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            since_time = datetime.now() - timedelta(hours=hours_history)
            
            query = '''
                SELECT timestamp, value FROM advanced_metrics
                WHERE metric_name = ? AND datetime(timestamp) >= datetime(?)
                ORDER BY timestamp
            '''
            
            df = pd.read_sql_query(query, conn, params=[metric_name, since_time.isoformat()])
            
            if len(df) < 20:  # Need sufficient data for prediction
                return None
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp').resample('5T').mean().dropna()  # 5-minute intervals
            
            values = df['value'].values
            
            # Simple linear prediction (can be enhanced with ARIMA, etc.)
            x = np.arange(len(values))
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
            
            current_value = values[-1]
            
            # Predict future values
            n_points = len(values)
            pred_1h = slope * (n_points + 12) + intercept  # 12 * 5min = 1 hour
            pred_4h = slope * (n_points + 48) + intercept  # 48 * 5min = 4 hours
            pred_24h = slope * (n_points + 288) + intercept  # 288 * 5min = 24 hours
            
            # Calculate confidence intervals (simple approach)
            residuals = values - (slope * x + intercept)
            rmse = np.sqrt(np.mean(residuals**2))
            
            confidence_intervals = {
                '1h': (pred_1h - 1.96 * rmse, pred_1h + 1.96 * rmse),
                '4h': (pred_4h - 1.96 * rmse, pred_4h + 1.96 * rmse),
                '24h': (pred_24h - 1.96 * rmse, pred_24h + 1.96 * rmse)
            }
            
            # Simple accuracy based on R-squared
            prediction_accuracy = max(0, min(1, r_value**2))
            
            return PredictionResult(
                metric_name=metric_name,
                current_value=current_value,
                predicted_1h=pred_1h,
                predicted_4h=pred_4h,
                predicted_24h=pred_24h,
                confidence_intervals=confidence_intervals,
                prediction_accuracy=prediction_accuracy,
                model_type='linear_regression'
            )
            
        except Exception as e:
            logger.error(f"Error predicting values for {metric_name}: {e}")
            return None
        finally:
            conn.close()
    
    async def detect_anomaly_clusters(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Detect clusters of anomalous behavior across metrics"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            # Get all metrics data
            query = '''
                SELECT timestamp, metric_name, value FROM advanced_metrics
                WHERE datetime(timestamp) >= datetime(?)
                ORDER BY timestamp
            '''
            
            df = pd.read_sql_query(query, conn, params=[since_time.isoformat()])
            
            if len(df) < 100:
                return []
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Pivot to get metrics as columns
            pivot_df = df.pivot_table(index='timestamp', columns='metric_name', values='value', aggfunc='mean')
            pivot_df = pivot_df.ffill().bfill().dropna()
            
            if pivot_df.shape[1] < 2:
                return []
            
            # Normalize data
            normalized_data = self.scaler.fit_transform(pivot_df.values)
            
            # Use DBSCAN for anomaly detection
            clustering = DBSCAN(eps=2.0, min_samples=5).fit(normalized_data)
            labels = clustering.labels_
            
            # Identify anomaly clusters (noise points have label -1)
            anomaly_indices = np.where(labels == -1)[0]
            
            anomaly_clusters = []
            for idx in anomaly_indices:
                timestamp = pivot_df.index[idx]
                anomaly_metrics = {}
                
                for col_idx, metric_name in enumerate(pivot_df.columns):
                    anomaly_metrics[metric_name] = {
                        'value': pivot_df.iloc[idx, col_idx],
                        'normalized_value': normalized_data[idx, col_idx]
                    }
                
                anomaly_clusters.append({
                    'timestamp': str(timestamp),
                    'anomaly_score': abs(normalized_data[idx]).max(),
                    'affected_metrics': anomaly_metrics,
                    'cluster_id': 'anomaly'
                })
            
            # Sort by anomaly score
            anomaly_clusters.sort(key=lambda x: x['anomaly_score'], reverse=True)
            
            return anomaly_clusters[:20]  # Return top 20 anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomaly clusters: {e}")
            return []
        finally:
            conn.close()
    
    async def generate_comprehensive_dashboard(self, hours: int = 24) -> str:
        """Generate comprehensive analytics dashboard"""
        try:
            # Collect current metrics
            current_metrics = await self.collect_advanced_system_metrics()
            
            # Create multi-dimensional dashboard
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=[
                    'System Health Overview', 'Performance Trends',
                    'Resource Utilization Heatmap', 'Anomaly Detection',
                    'Correlation Matrix', 'Prediction Timeline',
                    'Process Analysis', 'Kernel Metrics'
                ],
                specs=[
                    [{"type": "indicator"}, {"type": "scatter"}],
                    [{"type": "heatmap"}, {"type": "scatter"}],
                    [{"type": "heatmap"}, {"type": "scatter"}],
                    [{"type": "bar"}, {"type": "scatter"}]
                ],
                vertical_spacing=0.08
            )
            
            # System Health Overview (Gauge)
            health_score = current_metrics.get('performance', {}).get('system_health_score', 50)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=health_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "System Health Score"},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkgreen" if health_score > 70 else "orange" if health_score > 40 else "red"},
                        'steps': [
                            {'range': [0, 40], 'color': "lightgray"},
                            {'range': [40, 70], 'color': "gray"},
                            {'range': [70, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=1
            )
            
            # Performance Trends (example with CPU)
            cpu_usage = current_metrics.get('cpu', {}).get('usage_percent', 0)
            memory_usage = current_metrics.get('memory', {}).get('used_bytes', 0) / current_metrics.get('memory', {}).get('total_bytes', 1) * 100
            
            fig.add_trace(
                go.Scatter(
                    x=['CPU', 'Memory', 'Disk', 'Network'],
                    y=[cpu_usage, memory_usage, 
                       current_metrics.get('disk', {}).get('usage_percent', 0),
                       current_metrics.get('performance', {}).get('network_saturation', 0) * 100],
                    mode='lines+markers',
                    name='Current Usage %',
                    line=dict(color='cyan', width=3)
                ),
                row=1, col=2
            )
            
            # Add more visualizations...
            
            fig.update_layout(
                title="ProbePilot Advanced Analytics Dashboard",
                height=1600,
                showlegend=True,
                template="plotly_dark",
                font=dict(color="white")
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="advanced-analytics-dashboard")
            
        except Exception as e:
            logger.error(f"Error generating comprehensive dashboard: {e}")
            return f"<div>Error generating dashboard: {str(e)}</div>"
    
    async def generate_insights_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive insights report"""
        try:
            insights = {
                'summary': {},
                'performance_analysis': {},
                'correlations': [],
                'predictions': {},
                'anomalies': [],
                'recommendations': []
            }
            
            # Collect current metrics
            current_metrics = await self.collect_advanced_system_metrics()
            await self.store_advanced_metrics(current_metrics)
            
            # Performance analysis for key metrics
            key_metrics = ['usage_percent', 'used_bytes', 'bytes_sent', 'read_bytes']
            
            for metric in key_metrics:
                profile = await self.analyze_performance_patterns(metric, hours)
                if profile:
                    insights['performance_analysis'][metric] = asdict(profile)
            
            # Correlation analysis
            correlations = await self.detect_metric_correlations(key_metrics, hours)
            insights['correlations'] = [asdict(corr) for corr in correlations]
            
            # Predictions
            for metric in key_metrics:
                prediction = await self.predict_metric_values(metric, hours)
                if prediction:
                    insights['predictions'][metric] = asdict(prediction)
            
            # Anomaly detection
            anomalies = await self.detect_anomaly_clusters(hours)
            insights['anomalies'] = anomalies
            
            # Generate recommendations
            insights['recommendations'] = await self._generate_recommendations(current_metrics, insights)
            
            # Summary statistics
            insights['summary'] = {
                'total_metrics_analyzed': len(key_metrics),
                'correlations_found': len(correlations),
                'anomalies_detected': len(anomalies),
                'health_score': current_metrics.get('performance', {}).get('system_health_score', 50),
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality_score': self._calculate_data_quality_score(insights)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights report: {e}")
            return {'error': str(e)}
    
    async def _generate_recommendations(self, current_metrics: Dict, insights: Dict) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        try:
            # Performance-based recommendations
            cpu_usage = current_metrics.get('cpu', {}).get('usage_percent', 0)
            memory_usage = current_metrics.get('memory', {}).get('used_bytes', 0) / current_metrics.get('memory', {}).get('total_bytes', 1) * 100
            
            if cpu_usage > 80:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'title': 'High CPU Usage Detected',
                    'description': f'CPU usage is at {cpu_usage:.1f}%. Consider identifying resource-intensive processes.',
                    'action': 'Monitor top CPU processes and consider optimization or scaling.'
                })
            
            if memory_usage > 85:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'title': 'High Memory Usage',
                    'description': f'Memory usage is at {memory_usage:.1f}%. Risk of memory pressure.',
                    'action': 'Check for memory leaks or consider adding more RAM.'
                })
            
            # Anomaly-based recommendations
            if len(insights.get('anomalies', [])) > 5:
                recommendations.append({
                    'category': 'stability',
                    'priority': 'medium',
                    'title': 'Multiple Anomalies Detected',
                    'description': f'Found {len(insights["anomalies"])} anomalous patterns in the last 24 hours.',
                    'action': 'Investigate root causes and implement monitoring alerts.'
                })
            
            # Correlation-based recommendations
            strong_correlations = [c for c in insights.get('correlations', []) if abs(c.get('correlation_coefficient', 0)) > 0.7]
            if strong_correlations:
                recommendations.append({
                    'category': 'optimization',
                    'priority': 'low',
                    'title': 'Strong Metric Correlations Found',
                    'description': f'Found {len(strong_correlations)} strong correlations between metrics.',
                    'action': 'Leverage correlations for predictive monitoring and resource planning.'
                })
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            
        return recommendations
    
    def _calculate_data_quality_score(self, insights: Dict) -> float:
        """Calculate data quality score based on insights completeness"""
        try:
            score = 0
            max_score = 100
            
            # Performance analysis completeness
            if insights.get('performance_analysis'):
                score += 25
            
            # Correlation analysis
            if insights.get('correlations'):
                score += 20
            
            # Predictions availability
            if insights.get('predictions'):
                score += 25
            
            # Anomaly detection
            if 'anomalies' in insights:
                score += 15
            
            # Recommendations generated
            if insights.get('recommendations'):
                score += 15
            
            return min(100, score)
            
        except Exception:
            return 50.0

# Global advanced analytics engine
advanced_analytics = AdvancedAnalyticsEngine()
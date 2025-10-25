"""
Historical Metrics and Trend Analysis System for ProbePilot
Implements timeline visualizations, deviation charts, and baseline comparison
"""

import json
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricTrend:
    """Metric trend analysis result"""
    metric_name: str
    current_value: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0-1, how strong the trend is
    anomaly_score: float  # 0-1, how anomalous current value is
    baseline_avg: float
    baseline_std: float
    prediction_24h: Optional[float] = None

@dataclass
class TimeSeriesPoint:
    """Single time series data point"""
    timestamp: datetime
    value: float
    metric_name: str
    tags: Optional[Dict[str, str]] = None

class HistoricalMetricsEngine:
    """Advanced historical metrics storage and analysis engine"""
    
    def __init__(self, db_path: str = "/tmp/probepilot_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metric_timestamp 
            ON metrics(metric_name, timestamp)
        ''')
        
        # Create baselines table for storing calculated baselines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT UNIQUE NOT NULL,
                baseline_avg REAL NOT NULL,
                baseline_std REAL NOT NULL,
                baseline_min REAL NOT NULL,
                baseline_max REAL NOT NULL,
                sample_count INTEGER NOT NULL,
                last_updated TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_metric(self, metric_name: str, value: float, timestamp: Optional[datetime] = None, tags: Optional[Dict[str, str]] = None):
        """Store a metric data point"""
        if timestamp is None:
            timestamp = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (timestamp, metric_name, value, tags)
            VALUES (?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            metric_name,
            value,
            json.dumps(tags) if tags else None
        ))
        
        conn.commit()
        conn.close()
    
    def store_metrics_batch(self, metrics: List[TimeSeriesPoint]):
        """Store multiple metric points efficiently"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = [
            (point.timestamp.isoformat(), point.metric_name, point.value, 
             json.dumps(point.tags) if point.tags else None)
            for point in metrics
        ]
        
        cursor.executemany('''
            INSERT INTO metrics (timestamp, metric_name, value, tags)
            VALUES (?, ?, ?, ?)
        ''', data)
        
        conn.commit()
        conn.close()
    
    def get_metric_history(self, metric_name: str, hours: int = 24, limit: Optional[int] = None) -> List[TimeSeriesPoint]:
        """Get historical data for a metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        query = '''
            SELECT timestamp, metric_name, value, tags
            FROM metrics
            WHERE metric_name = ? AND datetime(timestamp) >= datetime(?)
            ORDER BY timestamp DESC
        '''
        
        params = [metric_name, since_time.isoformat()]
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [
            TimeSeriesPoint(
                timestamp=datetime.fromisoformat(row[0]),
                metric_name=row[1],
                value=row[2],
                tags=json.loads(row[3]) if row[3] else None
            )
            for row in results
        ]
    
    def calculate_baseline(self, metric_name: str, days: int = 7) -> Optional[Dict]:
        """Calculate baseline statistics for a metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT value FROM metrics
            WHERE metric_name = ? AND datetime(timestamp) >= datetime(?)
            ORDER BY timestamp
        ''', (metric_name, since_time.isoformat()))
        
        results = cursor.fetchall()
        conn.close()
        
        if len(results) < 10:  # Need minimum data points
            return None
        
        values = [row[0] for row in results]
        
        baseline = {
            'metric_name': metric_name,
            'baseline_avg': np.mean(values),
            'baseline_std': np.std(values),
            'baseline_min': np.min(values),
            'baseline_max': np.max(values),
            'sample_count': len(values),
            'last_updated': datetime.now().isoformat()
        }
        
        # Store baseline in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO baselines 
            (metric_name, baseline_avg, baseline_std, baseline_min, baseline_max, sample_count, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            baseline['metric_name'],
            baseline['baseline_avg'],
            baseline['baseline_std'],
            baseline['baseline_min'],
            baseline['baseline_max'],
            baseline['sample_count'],
            baseline['last_updated']
        ))
        
        conn.commit()
        conn.close()
        
        return baseline
    
    def get_baseline(self, metric_name: str) -> Optional[Dict]:
        """Get stored baseline for a metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT baseline_avg, baseline_std, baseline_min, baseline_max, sample_count, last_updated
            FROM baselines
            WHERE metric_name = ?
        ''', (metric_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'metric_name': metric_name,
            'baseline_avg': result[0],
            'baseline_std': result[1],
            'baseline_min': result[2],
            'baseline_max': result[3],
            'sample_count': result[4],
            'last_updated': result[5]
        }
    
    def analyze_trend(self, metric_name: str, hours: int = 24) -> Optional[MetricTrend]:
        """Analyze trend for a metric"""
        history = self.get_metric_history(metric_name, hours)
        
        if len(history) < 5:  # Need minimum points for trend analysis
            return None
        
        # Sort by timestamp
        history.sort(key=lambda x: x.timestamp)
        
        # Extract values and timestamps
        values = [point.value for point in history]
        timestamps = [point.timestamp.timestamp() for point in history]
        
        # Calculate trend using linear regression
        x = np.array(timestamps)
        y = np.array(values)
        
        # Normalize x for better numerical stability
        x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else np.zeros_like(x)
        
        # Linear regression
        slope, intercept = np.polyfit(x_norm, y, 1)
        
        # Determine trend direction and strength
        trend_direction = 'stable'
        trend_strength = 0
        
        if abs(slope) > np.std(y) * 0.1:  # Significant trend
            trend_direction = 'increasing' if slope > 0 else 'decreasing'
            trend_strength = min(abs(slope) / (np.std(y) + 1e-6), 1.0)
        
        # Get baseline for anomaly detection
        baseline = self.get_baseline(metric_name)
        current_value = values[-1]
        
        anomaly_score = 0
        baseline_avg = current_value
        baseline_std = np.std(values)
        
        if baseline:
            baseline_avg = baseline['baseline_avg']
            baseline_std = baseline['baseline_std']
            
            # Calculate anomaly score (z-score based)
            if baseline_std > 0:
                z_score = abs(current_value - baseline_avg) / baseline_std
                anomaly_score = min(z_score / 3.0, 1.0)  # Normalize to 0-1
        
        # Simple prediction for next 24h (linear extrapolation)
        prediction_24h = None
        if trend_strength > 0.3:  # Only predict if there's a strong trend
            future_time_norm = 1.0 + (24 * 3600) / (x.max() - x.min()) if x.max() != x.min() else 1.0
            prediction_24h = slope * future_time_norm + intercept
        
        return MetricTrend(
            metric_name=metric_name,
            current_value=current_value,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            anomaly_score=anomaly_score,
            baseline_avg=baseline_avg,
            baseline_std=baseline_std,
            prediction_24h=prediction_24h
        )
    
    def generate_timeline_chart(self, metric_names: List[str], hours: int = 24) -> str:
        """Generate interactive timeline chart HTML"""
        fig = make_subplots(
            rows=len(metric_names), cols=1,
            subplot_titles=metric_names,
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        colors = px.colors.qualitative.Set1
        
        for i, metric_name in enumerate(metric_names):
            history = self.get_metric_history(metric_name, hours)
            baseline = self.get_baseline(metric_name)
            
            if not history:
                continue
            
            # Sort by timestamp
            history.sort(key=lambda x: x.timestamp)
            
            timestamps = [point.timestamp for point in history]
            values = [point.value for point in history]
            
            # Add main metric line
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=f'{metric_name}',
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=4),
                    hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
                ),
                row=i+1, col=1
            )
            
            # Add baseline bands if available
            if baseline and len(timestamps) > 0:
                baseline_avg = baseline['baseline_avg']
                baseline_std = baseline['baseline_std']
                
                # Warning band (±2 std)
                fig.add_trace(
                    go.Scatter(
                        x=timestamps + timestamps[::-1],
                        y=[baseline_avg + 2*baseline_std] * len(timestamps) + 
                          [baseline_avg - 2*baseline_std] * len(timestamps),
                        fill='tonexty',
                        fillcolor='rgba(255, 193, 7, 0.2)',
                        line=dict(color='rgba(255, 193, 7, 0)'),
                        name=f'{metric_name} Warning Band',
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=i+1, col=1
                )
                
                # Critical band (±3 std)
                fig.add_trace(
                    go.Scatter(
                        x=timestamps + timestamps[::-1],
                        y=[baseline_avg + 3*baseline_std] * len(timestamps) + 
                          [baseline_avg - 3*baseline_std] * len(timestamps),
                        fill='tonexty',
                        fillcolor='rgba(220, 53, 69, 0.2)',
                        line=dict(color='rgba(220, 53, 69, 0)'),
                        name=f'{metric_name} Critical Band',
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=i+1, col=1
                )
                
                # Baseline average line
                fig.add_hline(
                    y=baseline_avg,
                    line_dash="dash",
                    line_color="gray",
                    annotation_text=f"Baseline: {baseline_avg:.1f}",
                    row=i+1, col=1
                )
        
        fig.update_layout(
            title=f"System Metrics Timeline - Last {hours} Hours",
            height=300 * len(metric_names),
            showlegend=True,
            template="plotly_dark",
            font=dict(color="white")
        )
        
        fig.update_xaxes(title_text="Time")
        
        return fig.to_html(include_plotlyjs='cdn', div_id="timeline-chart")
    
    def generate_deviation_heatmap(self, metric_names: List[str], days: int = 7) -> str:
        """Generate deviation heatmap showing anomaly patterns"""
        # Get hourly aggregated data for the heatmap
        deviation_data = []
        
        for metric_name in metric_names:
            history = self.get_metric_history(metric_name, days * 24)
            baseline = self.get_baseline(metric_name)
            
            if not history or not baseline:
                continue
            
            # Group by hour and calculate deviations
            hourly_deviations = {}
            baseline_avg = baseline['baseline_avg']
            baseline_std = baseline['baseline_std']
            
            for point in history:
                hour_key = point.timestamp.strftime('%Y-%m-%d %H:00')
                if baseline_std > 0:
                    deviation = (point.value - baseline_avg) / baseline_std
                else:
                    deviation = 0
                
                if hour_key not in hourly_deviations:
                    hourly_deviations[hour_key] = []
                hourly_deviations[hour_key].append(deviation)
            
            # Average deviations per hour
            for hour_key, deviations in hourly_deviations.items():
                avg_deviation = np.mean(deviations)
                deviation_data.append({
                    'metric': metric_name,
                    'hour': hour_key,
                    'deviation': avg_deviation
                })
        
        if not deviation_data:
            return "<div>No data available for heatmap</div>"
        
        # Create DataFrame and pivot for heatmap
        df = pd.DataFrame(deviation_data)
        
        # Convert hour to datetime for better sorting
        df['hour'] = pd.to_datetime(df['hour'])
        df = df.sort_values(['metric', 'hour'])
        
        # Create pivot table
        pivot_df = df.pivot(index='metric', columns='hour', values='deviation')
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=[col.strftime('%m/%d %H:%M') for col in pivot_df.columns],
            y=pivot_df.index,
            colorscale='RdYlBu_r',
            zmid=0,
            colorbar=dict(title="Std Deviations"),
            hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Deviation: %{z:.2f}σ<extra></extra>'
        ))
        
        fig.update_layout(
            title="Metric Deviation Heatmap (Standard Deviations from Baseline)",
            xaxis_title="Time",
            yaxis_title="Metrics",
            template="plotly_dark",
            font=dict(color="white"),
            height=200 + len(metric_names) * 40
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id="deviation-heatmap")
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove old metric data to manage storage"""
        cutoff_time = datetime.now() - timedelta(days=days_to_keep)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM metrics
            WHERE datetime(timestamp) < datetime(?)
        ''', (cutoff_time.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_count} old metric records")
        return deleted_count

# Global historical metrics engine
historical_engine = HistoricalMetricsEngine()
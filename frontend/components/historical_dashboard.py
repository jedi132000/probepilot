"""
Historical Metrics Dashboard Component
Provides timeline visualizations, trend analysis, and baseline comparison
"""

import gradio as gr
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class HistoricalMetricsDashboard:
    """Dashboard for historical metrics and trend analysis"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all available metrics"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/metrics/historical/summary", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_timeline_chart(self, metrics: str, hours: int = 24) -> str:
        """Get timeline chart HTML for metrics"""
        try:
            params = {"metrics": metrics, "hours": hours}
            response = requests.get(
                f"{self.backend_url}/api/v1/metrics/historical/timeline",
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("chart_html", "No chart data available")
            return f"<div class='error'>Failed to load timeline: HTTP {response.status_code}</div>"
        except Exception as e:
            return f"<div class='error'>Timeline error: {str(e)}</div>"
    
    def get_deviation_heatmap(self, metrics: str, days: int = 7) -> str:
        """Get deviation heatmap HTML for metrics"""
        try:
            params = {"metrics": metrics, "days": days}
            response = requests.get(
                f"{self.backend_url}/api/v1/metrics/historical/heatmap",
                params=params,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("heatmap_html", "No heatmap data available")
            return f"<div class='error'>Failed to load heatmap: HTTP {response.status_code}</div>"
        except Exception as e:
            return f"<div class='error'>Heatmap error: {str(e)}</div>"
    
    def get_trend_analysis(self, metric_name: str, hours: int = 24) -> str:
        """Get trend analysis for a specific metric"""
        try:
            params = {"hours": hours}
            response = requests.get(
                f"{self.backend_url}/api/v1/metrics/historical/trend/{metric_name}",
                params=params,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                trend_data = data.get("data")
                
                if not trend_data:
                    return "Insufficient data for trend analysis"
                
                # Format trend analysis as HTML
                trend_html = f"""
                <div style="background: rgba(30, 41, 59, 0.8); border-radius: 8px; padding: 20px; border: 1px solid rgba(71, 85, 105, 0.3);">
                    <h3 style="color: #94a3b8; margin-top: 0;">📈 Trend Analysis: {trend_data['metric_name']}</h3>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div>
                            <span style="color: #64748b;">Current Value:</span>
                            <span style="color: #3b82f6; font-weight: bold; font-size: 1.1em;">{trend_data['current_value']:.2f}</span>
                        </div>
                        <div>
                            <span style="color: #64748b;">Trend Direction:</span>
                            <span style="color: {'#22c55e' if trend_data['trend_direction'] == 'stable' else '#fbbf24' if trend_data['trend_direction'] == 'increasing' else '#ef4444'}; font-weight: bold;">{trend_data['trend_direction'].upper()}</span>
                        </div>
                        <div>
                            <span style="color: #64748b;">Trend Strength:</span>
                            <span style="color: #8b5cf6; font-weight: bold;">{trend_data['trend_strength']:.2f}</span>
                        </div>
                        <div>
                            <span style="color: #64748b;">Anomaly Score:</span>
                            <span style="color: {'#ef4444' if trend_data['anomaly_score'] > 0.7 else '#fbbf24' if trend_data['anomaly_score'] > 0.3 else '#22c55e'}; font-weight: bold;">{trend_data['anomaly_score']:.2f}</span>
                        </div>
                    </div>
                    
                    <div style="background: rgba(15, 23, 42, 0.5); border-radius: 6px; padding: 12px; margin-bottom: 15px;">
                        <h4 style="color: #94a3b8; margin: 0 0 8px 0;">Baseline Statistics</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div>
                                <span style="color: #64748b;">Average:</span>
                                <span style="color: #e2e8f0; font-weight: bold;">{trend_data['baseline_avg']:.2f}</span>
                            </div>
                            <div>
                                <span style="color: #64748b;">Std Dev:</span>
                                <span style="color: #e2e8f0; font-weight: bold;">{trend_data['baseline_std']:.2f}</span>
                            </div>
                        </div>
                    </div>
                """
                
                if trend_data.get('prediction_24h'):
                    trend_html += f"""
                    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 6px; padding: 12px;">
                        <h4 style="color: #3b82f6; margin: 0 0 8px 0;">📊 24h Prediction</h4>
                        <span style="color: #93c5fd; font-weight: bold; font-size: 1.1em;">{trend_data['prediction_24h']:.2f}</span>
                        <span style="color: #64748b; margin-left: 8px;">(based on current trend)</span>
                    </div>
                    """
                
                trend_html += "</div>"
                return trend_html
                
            return f"<div class='error'>Failed to load trend: HTTP {response.status_code}</div>"
        except Exception as e:
            return f"<div class='error'>Trend analysis error: {str(e)}</div>"
    
    def get_baseline_info(self, metric_name: str) -> str:
        """Get baseline information for a metric"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/metrics/historical/baseline/{metric_name}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                baseline = data.get("data")
                
                if not baseline:
                    return "No baseline data available for this metric"
                
                # Format baseline info as HTML
                last_updated = datetime.fromisoformat(baseline['last_updated']).strftime('%m/%d %H:%M')
                
                baseline_html = f"""
                <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px;">
                    <h4 style="color: #22c55e; margin-top: 0;">📊 Baseline Statistics</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9em;">
                        <div><span style="color: #64748b;">Average:</span> <span style="color: #e2e8f0; font-weight: bold;">{baseline['baseline_avg']:.2f}</span></div>
                        <div><span style="color: #64748b;">Std Dev:</span> <span style="color: #e2e8f0; font-weight: bold;">{baseline['baseline_std']:.2f}</span></div>
                        <div><span style="color: #64748b;">Min:</span> <span style="color: #e2e8f0; font-weight: bold;">{baseline['baseline_min']:.2f}</span></div>
                        <div><span style="color: #64748b;">Max:</span> <span style="color: #e2e8f0; font-weight: bold;">{baseline['baseline_max']:.2f}</span></div>
                        <div><span style="color: #64748b;">Samples:</span> <span style="color: #e2e8f0; font-weight: bold;">{baseline['sample_count']}</span></div>
                        <div><span style="color: #64748b;">Updated:</span> <span style="color: #e2e8f0; font-weight: bold;">{last_updated}</span></div>
                    </div>
                </div>
                """
                return baseline_html
                
            return f"<div class='error'>Failed to load baseline: HTTP {response.status_code}</div>"
        except Exception as e:
            return f"<div class='error'>Baseline error: {str(e)}</div>"

# Global dashboard instance
dashboard = HistoricalMetricsDashboard()

def create_historical_metrics_interface():
    """Create the historical metrics dashboard interface"""
    
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## 📈 Historical Metrics & Trend Analysis")
            gr.Markdown("Advanced baseline comparison, anomaly detection, and predictive analysis")
        
        with gr.Column(scale=1):
            refresh_btn = gr.Button("🔄 Refresh Data", variant="secondary")
    
    with gr.Tabs():
        # Timeline Analysis Tab
        with gr.TabItem("📊 Timeline Analysis"):
            with gr.Row():
                timeline_metrics = gr.Textbox(
                    label="Metrics to Display",
                    placeholder="cpu_percent,memory_percent,disk_percent",
                    value="cpu_percent,memory_percent,disk_percent",
                    info="Comma-separated list of metrics"
                )
                timeline_hours = gr.Slider(
                    minimum=1, maximum=168, value=24, step=1,
                    label="Hours to Display"
                )
            
            timeline_chart = gr.HTML(label="Timeline Chart")
            
            def update_timeline(metrics, hours):
                return dashboard.get_timeline_chart(metrics, hours)
            
            timeline_metrics.change(
                update_timeline,
                inputs=[timeline_metrics, timeline_hours],
                outputs=[timeline_chart]
            )
            timeline_hours.change(
                update_timeline,
                inputs=[timeline_metrics, timeline_hours],
                outputs=[timeline_chart]
            )
        
        # Deviation Heatmap Tab
        with gr.TabItem("🔥 Anomaly Heatmap"):
            with gr.Row():
                heatmap_metrics = gr.Textbox(
                    label="Metrics for Heatmap",
                    placeholder="cpu_percent,memory_percent,network_in_mbps",
                    value="cpu_percent,memory_percent,network_in_mbps",
                    info="Comma-separated list of metrics"
                )
                heatmap_days = gr.Slider(
                    minimum=1, maximum=30, value=7, step=1,
                    label="Days to Analyze"
                )
            
            deviation_heatmap = gr.HTML(label="Deviation Heatmap")
            
            def update_heatmap(metrics, days):
                return dashboard.get_deviation_heatmap(metrics, days)
            
            heatmap_metrics.change(
                update_heatmap,
                inputs=[heatmap_metrics, heatmap_days],
                outputs=[deviation_heatmap]
            )
            heatmap_days.change(
                update_heatmap,
                inputs=[heatmap_metrics, heatmap_days],
                outputs=[deviation_heatmap]
            )
        
        # Trend Analysis Tab
        with gr.TabItem("📈 Trend Analysis"):
            with gr.Row():
                trend_metric = gr.Dropdown(
                    choices=["cpu_percent", "memory_percent", "disk_percent", "network_in_mbps", "network_out_mbps", "load_average"],
                    value="cpu_percent",
                    label="Select Metric"
                )
                trend_hours = gr.Slider(
                    minimum=1, maximum=168, value=24, step=1,
                    label="Analysis Period (Hours)"
                )
            
            with gr.Row():
                with gr.Column():
                    trend_analysis = gr.HTML(label="Trend Analysis")
                with gr.Column():
                    baseline_info = gr.HTML(label="Baseline Information")
            
            def update_trend_analysis(metric, hours):
                trend = dashboard.get_trend_analysis(metric, hours)
                baseline = dashboard.get_baseline_info(metric)
                return trend, baseline
            
            trend_metric.change(
                update_trend_analysis,
                inputs=[trend_metric, trend_hours],
                outputs=[trend_analysis, baseline_info]
            )
            trend_hours.change(
                update_trend_analysis,
                inputs=[trend_metric, trend_hours],
                outputs=[trend_analysis, baseline_info]
            )
    
    # Load initial data
    def load_initial_data():
        timeline = dashboard.get_timeline_chart("cpu_percent,memory_percent,disk_percent", 24)
        heatmap = dashboard.get_deviation_heatmap("cpu_percent,memory_percent,network_in_mbps", 7)
        trend = dashboard.get_trend_analysis("cpu_percent", 24)
        baseline = dashboard.get_baseline_info("cpu_percent")
        return timeline, heatmap, trend, baseline
    
    # Set up refresh functionality
    refresh_btn.click(
        load_initial_data,
        outputs=[timeline_chart, deviation_heatmap, trend_analysis, baseline_info]
    )
    
    return {
        "timeline_chart": timeline_chart,
        "deviation_heatmap": deviation_heatmap,
        "trend_analysis": trend_analysis,
        "baseline_info": baseline_info
    }

def get_historical_insights_html() -> str:
    """Get quick historical insights for the main dashboard"""
    try:
        summary = dashboard.get_metrics_summary()
        
        if not summary.get("success"):
            return """
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 12px;">
                <h4 style="color: #ef4444; margin: 0;">Historical Data Unavailable</h4>
                <p style="margin: 8px 0 0 0; color: #e2e8f0; font-size: 0.9em;">Historical metrics service is not available</p>
            </div>
            """
        
        metrics_data = summary.get("data", {}).get("metrics", [])
        
        if not metrics_data:
            return """
            <div style="background: rgba(100, 116, 139, 0.1); border: 1px solid #64748b; border-radius: 8px; padding: 12px;">
                <h4 style="color: #64748b; margin: 0;">Building Historical Context</h4>
                <p style="margin: 8px 0 0 0; color: #e2e8f0; font-size: 0.9em;">Collecting baseline data... Check back in a few minutes</p>
            </div>
            """
        
        insights_html = """
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3);">
            <h4 style="color: #94a3b8; margin: 0 0 12px 0; font-size: 0.9em;">📊 HISTORICAL INSIGHTS</h4>
        """
        
        # Show top 3 metrics with anomalies
        anomalous_metrics = [m for m in metrics_data if m.get('anomaly_score', 0) > 0.3]
        anomalous_metrics.sort(key=lambda x: x.get('anomaly_score', 0), reverse=True)
        
        if anomalous_metrics:
            insights_html += "<div style='margin-bottom: 10px;'>"
            for metric in anomalous_metrics[:3]:
                anomaly_score = metric.get('anomaly_score', 0)
                color = "#ef4444" if anomaly_score > 0.7 else "#fbbf24"
                insights_html += f"""
                <div style="font-size: 0.8em; margin-bottom: 4px;">
                    <span style="color: #64748b;">{metric['metric_name']}:</span>
                    <span style="color: {color}; font-weight: bold;">Anomaly {anomaly_score:.2f}</span>
                    <span style="color: #64748b;">({metric.get('trend_direction', 'unknown')})</span>
                </div>
                """
            insights_html += "</div>"
        else:
            insights_html += """
            <div style="font-size: 0.8em; color: #22c55e; margin-bottom: 10px;">
                ✅ All metrics within normal baselines
            </div>
            """
        
        # Show total metrics being tracked
        insights_html += f"""
        <div style="font-size: 0.8em; color: #64748b;">
            Tracking {len(metrics_data)} metrics with historical baselines
        </div>
        </div>
        """
        
        return insights_html
        
    except Exception as e:
        return f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 12px;">
            <h4 style="color: #ef4444; margin: 0;">Historical Insights Error</h4>
            <p style="margin: 8px 0 0 0; color: #e2e8f0; font-size: 0.9em;">Error: {str(e)}</p>
        </div>
        """
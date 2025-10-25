"""
Advanced Analytics Dashboard Component for ProbePilot
Provides comprehensive system observability and deep analytics visualization
"""

import gradio as gr
import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)

class AdvancedAnalyticsDashboard:
    """Advanced analytics dashboard with comprehensive system insights"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        
    def create_dashboard(self):
        """Create advanced analytics dashboard interface"""
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("# 🧠 Advanced Analytics & Deep Observability")
                gr.Markdown("*Comprehensive system analysis with predictive insights, correlation detection, and anomaly identification*")
                
        with gr.Tabs():
            # System Health Tab
            with gr.TabItem("🏥 System Health"):
                health_refresh_btn = gr.Button("🔄 Refresh Health Analysis", variant="primary")
                health_output = gr.HTML()
                
                health_refresh_btn.click(
                    fn=self.get_comprehensive_health,
                    outputs=health_output
                )
                
            # Performance Analytics Tab  
            with gr.TabItem("📊 Performance Analytics"):
                with gr.Row():
                    metric_input = gr.Textbox(
                        label="Metric Name",
                        placeholder="e.g., usage_percent, used_bytes",
                        value="usage_percent"
                    )
                    hours_input = gr.Slider(
                        minimum=1, maximum=168, value=24,
                        label="Analysis Period (Hours)"
                    )
                    
                perf_analyze_btn = gr.Button("📈 Analyze Performance", variant="primary")
                perf_output = gr.HTML()
                
                perf_analyze_btn.click(
                    fn=self.analyze_metric_performance,
                    inputs=[metric_input, hours_input],
                    outputs=perf_output
                )
                
            # Correlation Analysis Tab
            with gr.TabItem("🔗 Correlation Analysis"):
                with gr.Row():
                    metrics_input = gr.Textbox(
                        label="Metrics to Analyze (comma-separated)",
                        placeholder="usage_percent,used_bytes,bytes_sent,read_bytes",
                        value="usage_percent,used_bytes,bytes_sent,read_bytes"
                    )
                    corr_hours_input = gr.Slider(
                        minimum=1, maximum=168, value=24,
                        label="Analysis Period (Hours)"
                    )
                    
                corr_analyze_btn = gr.Button("🔍 Find Correlations", variant="primary")
                corr_output = gr.HTML()
                
                corr_analyze_btn.click(
                    fn=self.analyze_correlations,
                    inputs=[metrics_input, corr_hours_input],
                    outputs=corr_output
                )
                
            # Predictions Tab
            with gr.TabItem("🔮 Predictions"):
                with gr.Row():
                    pred_metric_input = gr.Textbox(
                        label="Metric to Predict",
                        placeholder="e.g., usage_percent",
                        value="usage_percent"
                    )
                    pred_history_input = gr.Slider(
                        minimum=6, maximum=168, value=24,
                        label="Historical Data Period (Hours)"
                    )
                    
                pred_analyze_btn = gr.Button("🎯 Generate Predictions", variant="primary")
                pred_output = gr.HTML()
                
                pred_analyze_btn.click(
                    fn=self.generate_predictions,
                    inputs=[pred_metric_input, pred_history_input],
                    outputs=pred_output
                )
                
            # Anomaly Detection Tab
            with gr.TabItem("🚨 Anomaly Detection"):
                with gr.Row():
                    anomaly_hours_input = gr.Slider(
                        minimum=1, maximum=168, value=24,
                        label="Detection Period (Hours)"
                    )
                    
                anomaly_detect_btn = gr.Button("🕵️ Detect Anomalies", variant="primary")
                anomaly_output = gr.HTML()
                
                anomaly_detect_btn.click(
                    fn=self.detect_anomalies,
                    inputs=[anomaly_hours_input],
                    outputs=anomaly_output
                )
                
            # Comprehensive Insights Tab
            with gr.TabItem("💡 System Insights"):
                with gr.Row():
                    insights_hours_input = gr.Slider(
                        minimum=1, maximum=168, value=24,
                        label="Analysis Period (Hours)"
                    )
                    
                insights_generate_btn = gr.Button("🧠 Generate Insights", variant="primary")
                insights_output = gr.HTML()
                
                insights_generate_btn.click(
                    fn=self.generate_system_insights,
                    inputs=[insights_hours_input],
                    outputs=insights_output
                )
                
            # Advanced Dashboard Tab
            with gr.TabItem("📈 Advanced Dashboard"):
                with gr.Row():
                    dashboard_refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
                    dashboard_auto_btn = gr.Button("🚀 Load Dashboard", variant="secondary")
                
                dashboard_output = gr.HTML(value="<div style='text-align: center; padding: 40px; color: #888;'>Click '🚀 Load Dashboard' to view comprehensive analytics</div>")
                
                dashboard_refresh_btn.click(
                    fn=self.get_advanced_dashboard,
                    outputs=dashboard_output
                )
                
                dashboard_auto_btn.click(
                    fn=self.get_advanced_dashboard,
                    outputs=dashboard_output
                )
        
        # Auto-load initial data
        try:
            health_output.value = self.get_comprehensive_health()
        except Exception as e:
            logger.error(f"Error loading initial health data: {e}")
            health_output.value = "<div class='error'>Error loading initial data</div>"
    
    def get_comprehensive_health(self):
        """Get comprehensive system health analysis"""
        try:
            response = requests.get(f"{self.backend_url}/api/v1/analytics/health/comprehensive", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                health_analysis = data.get("health_analysis", {})
                
                # Create health visualization
                html_content = self._create_health_visualization(health_analysis)
                return html_content
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error getting comprehensive health: {e}")
            return f"<div class='error'>Error retrieving health data: {str(e)}</div>"
    
    def _create_health_visualization(self, health_analysis):
        """Create health visualization HTML"""
        try:
            overall_score = health_analysis.get("overall_health_score", 50)
            components = health_analysis.get("component_health", {})
            anomalies = health_analysis.get("anomalies_detected", 0)
            recommendations = health_analysis.get("recommendations", [])
            
            # Determine overall status
            if overall_score >= 80:
                status_color = "#28a745"
                status_text = "Healthy"
                status_icon = "✅"
            elif overall_score >= 60:
                status_color = "#ffc107"
                status_text = "Warning"
                status_icon = "⚠️"
            else:
                status_color = "#dc3545"
                status_text = "Critical"
                status_icon = "🚨"
            
            html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0; text-align: center;">
                    {status_icon} System Health Analysis
                </h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                        <h3 style="margin: 0; color: {status_color};">Overall Health</h3>
                        <div style="font-size: 2.5em; font-weight: bold; color: {status_color};">{overall_score:.1f}</div>
                        <div style="font-size: 1.2em; color: {status_color};">{status_text}</div>
                    </div>
            """
            
            # Component health scores
            for component, details in components.items():
                score = details.get("score", 0)
                status = details.get("status", "unknown")
                
                color = "#28a745" if status == "healthy" else "#ffc107" if status == "warning" else "#dc3545"
                icon = "✅" if status == "healthy" else "⚠️" if status == "warning" else "🚨"
                
                html += f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                        <h4 style="margin: 0; text-transform: capitalize;">{icon} {component}</h4>
                        <div style="font-size: 1.8em; font-weight: bold; color: {color};">{score:.1f}</div>
                        <div style="color: {color}; text-transform: capitalize;">{status}</div>
                    </div>
                """
            
            html += "</div>"
            
            # Anomalies section
            if anomalies > 0:
                html += f"""
                <div style="background: rgba(220, 53, 69, 0.2); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0; color: #dc3545;">🚨 Anomalies Detected</h3>
                    <p style="margin: 10px 0;">Found {anomalies} anomalous patterns in system behavior.</p>
                    <p style="margin: 0;"><strong>Recommendation:</strong> Investigate these anomalies for potential issues.</p>
                </div>
                """
            
            # Recommendations section
            if recommendations:
                html += """
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0;">💡 Recommendations</h3>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                """
                
                for rec in recommendations[:5]:  # Show top 5 recommendations
                    priority_color = "#dc3545" if rec.get("priority") == "high" else "#ffc107" if rec.get("priority") == "medium" else "#28a745"
                    html += f"""
                        <li style="margin: 10px 0;">
                            <strong style="color: {priority_color};">[{rec.get('priority', 'low').upper()}]</strong>
                            {rec.get('title', 'No title')}: {rec.get('description', 'No description')}
                        </li>
                    """
                
                html += "</ul></div>"
            
            html += f"""
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating health visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def analyze_metric_performance(self, metric_name, hours):
        """Analyze performance patterns for a metric"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/performance/{metric_name}",
                params={"hours": hours},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                profile = data.get("performance_profile", {})
                return self._create_performance_visualization(metric_name, profile)
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error analyzing metric performance: {e}")
            return f"<div class='error'>Error analyzing performance: {str(e)}</div>"
    
    def _create_performance_visualization(self, metric_name, profile):
        """Create performance analysis visualization"""
        try:
            html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #2c5530, #3d7c47); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0;">📊 Performance Analysis: {metric_name}</h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px;">
                        <h4 style="margin: 0;">Current Value</h4>
                        <div style="font-size: 1.5em; font-weight: bold;">{profile.get('current_value', 0):.2f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px;">
                        <h4 style="margin: 0;">Baseline Mean</h4>
                        <div style="font-size: 1.5em; font-weight: bold;">{profile.get('baseline_mean', 0):.2f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px;">
                        <h4 style="margin: 0;">Percentile Rank</h4>
                        <div style="font-size: 1.5em; font-weight: bold;">{profile.get('percentile_rank', 0):.1f}%</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px;">
                        <h4 style="margin: 0;">Trend</h4>
                        <div style="font-size: 1.2em; font-weight: bold; text-transform: capitalize;">
                            {profile.get('trend_direction', 'stable')} 
                            ({profile.get('trend_strength', 0):.2f})
                        </div>
                    </div>
                </div>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0;">Anomaly Score</h4>
                    <div style="display: flex; align-items: center; margin: 10px 0;">
                        <div style="background: #333; height: 20px; width: 200px; border-radius: 10px; overflow: hidden;">
                            <div style="background: {'#dc3545' if profile.get('anomaly_score', 0) > 0.7 else '#ffc107' if profile.get('anomaly_score', 0) > 0.3 else '#28a745'}; height: 100%; width: {profile.get('anomaly_score', 0) * 100}%; transition: width 0.3s;"></div>
                        </div>
                        <span style="margin-left: 10px; font-weight: bold;">{profile.get('anomaly_score', 0):.3f}</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating performance visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def analyze_correlations(self, metrics, hours):
        """Analyze correlations between metrics"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/correlations",
                params={"hours": hours, "metrics": metrics},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                correlations = data.get("correlations", [])
                return self._create_correlation_visualization(correlations)
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return f"<div class='error'>Error analyzing correlations: {str(e)}</div>"
    
    def _create_correlation_visualization(self, correlations):
        """Create correlation analysis visualization"""
        try:
            html = """
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #4a1a4b, #6b2c6e); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0;">🔗 Correlation Analysis</h2>
            """
            
            if not correlations:
                html += """
                <div style="text-align: center; padding: 40px;">
                    <h3>No significant correlations found</h3>
                    <p>Try analyzing over a longer time period or with different metrics.</p>
                </div>
                """
            else:
                html += """
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                        <thead>
                            <tr style="background: rgba(255,255,255,0.1);">
                                <th style="padding: 12px; text-align: left; border: 1px solid rgba(255,255,255,0.2);">Metric A</th>
                                <th style="padding: 12px; text-align: left; border: 1px solid rgba(255,255,255,0.2);">Metric B</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.2);">Correlation</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.2);">Strength</th>
                                <th style="padding: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.2);">Confidence</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for corr in correlations:
                    coeff = corr.get("correlation_coefficient", 0)
                    relationship = corr.get("relationship_type", "none")
                    confidence = corr.get("confidence_level", 0)
                    
                    # Color coding based on strength
                    if abs(coeff) > 0.7:
                        strength_color = "#28a745"
                        strength_text = "Strong"
                    elif abs(coeff) > 0.3:
                        strength_color = "#ffc107"
                        strength_text = "Moderate"
                    else:
                        strength_color = "#6c757d"
                        strength_text = "Weak"
                    
                    html += f"""
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <td style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">{corr.get('metric_a', 'Unknown')}</td>
                            <td style="padding: 10px; border: 1px solid rgba(255,255,255,0.1);">{corr.get('metric_b', 'Unknown')}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid rgba(255,255,255,0.1); font-weight: bold;">{coeff:.3f}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid rgba(255,255,255,0.1); color: {strength_color}; font-weight: bold;">{strength_text}</td>
                            <td style="padding: 10px; text-align: center; border: 1px solid rgba(255,255,255,0.1);">{confidence:.2%}</td>
                        </tr>
                    """
                
                html += """
                        </tbody>
                    </table>
                </div>
                """
            
            html += f"""
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating correlation visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def generate_predictions(self, metric_name, hours_history):
        """Generate predictions for a metric"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/predictions/{metric_name}",
                params={"hours_history": hours_history},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                prediction = data.get("prediction", {})
                return self._create_prediction_visualization(metric_name, prediction)
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return f"<div class='error'>Error generating predictions: {str(e)}</div>"
    
    def _create_prediction_visualization(self, metric_name, prediction):
        """Create prediction visualization"""
        try:
            accuracy = prediction.get("prediction_accuracy", 0) * 100
            
            html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a4b47, #2d6b61); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0;">🔮 Predictions: {metric_name}</h2>
                
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin: 0;">Model Accuracy: {accuracy:.1f}%</h4>
                    <div style="display: flex; align-items: center; margin: 10px 0;">
                        <div style="background: #333; height: 20px; width: 200px; border-radius: 10px; overflow: hidden;">
                            <div style="background: {'#28a745' if accuracy > 70 else '#ffc107' if accuracy > 50 else '#dc3545'}; height: 100%; width: {accuracy}%; transition: width 0.3s;"></div>
                        </div>
                        <span style="margin-left: 10px;">({prediction.get('model_type', 'unknown')})</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">Current</h4>
                        <div style="font-size: 1.5em; font-weight: bold; color: #17a2b8;">{prediction.get('current_value', 0):.2f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">1 Hour</h4>
                        <div style="font-size: 1.5em; font-weight: bold; color: #28a745;">{prediction.get('predicted_1h', 0):.2f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">4 Hours</h4>
                        <div style="font-size: 1.5em; font-weight: bold; color: #ffc107;">{prediction.get('predicted_4h', 0):.2f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">24 Hours</h4>
                        <div style="font-size: 1.5em; font-weight: bold; color: #dc3545;">{prediction.get('predicted_24h', 0):.2f}</div>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Predictions generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating prediction visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def detect_anomalies(self, hours):
        """Detect system anomalies"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/anomalies",
                params={"hours": hours},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                anomalies = data.get("anomalies", [])
                return self._create_anomaly_visualization(anomalies)
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return f"<div class='error'>Error detecting anomalies: {str(e)}</div>"
    
    def _create_anomaly_visualization(self, anomalies):
        """Create anomaly detection visualization"""
        try:
            html = """
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #5a1a1a, #7d2828); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0;">🚨 Anomaly Detection Results</h2>
            """
            
            if not anomalies:
                html += """
                <div style="text-align: center; padding: 40px; background: rgba(40, 167, 69, 0.2); border-radius: 8px;">
                    <h3 style="color: #28a745;">✅ No Anomalies Detected</h3>
                    <p>Your system is operating within normal parameters.</p>
                </div>
                """
            else:
                html += f"""
                <div style="background: rgba(220, 53, 69, 0.2); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0; color: #dc3545;">⚠️ {len(anomalies)} Anomalies Found</h3>
                    <p style="margin: 10px 0;">Unusual patterns detected in system behavior.</p>
                </div>
                
                <div style="max-height: 500px; overflow-y: auto;">
                """
                
                for i, anomaly in enumerate(anomalies[:10]):  # Show top 10
                    timestamp = anomaly.get("timestamp", "Unknown")
                    score = anomaly.get("anomaly_score", 0)
                    affected_metrics = anomaly.get("affected_metrics", {})
                    
                    html += f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <div style="display: flex; justify-content: between; align-items: center;">
                            <h4 style="margin: 0;">Anomaly #{i+1}</h4>
                            <span style="background: #dc3545; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">Score: {score:.3f}</span>
                        </div>
                        <p style="margin: 10px 0; opacity: 0.8;">Detected at: {timestamp}</p>
                        <p style="margin: 5px 0;"><strong>Affected Metrics:</strong> {len(affected_metrics)} metrics show unusual values</p>
                    </div>
                    """
                
                html += "</div>"
            
            html += f"""
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Detection completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating anomaly visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def generate_system_insights(self, hours):
        """Generate comprehensive system insights"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/analytics/insights",
                params={"hours": hours},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                insights = data.get("insights", {})
                return self._create_insights_visualization(insights)
            else:
                return f"<div class='error'>Error: {response.status_code} - {response.text}</div>"
                
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return f"<div class='error'>Error generating insights: {str(e)}</div>"
    
    def _create_insights_visualization(self, insights):
        """Create comprehensive insights visualization"""
        try:
            summary = insights.get("summary", {})
            recommendations = insights.get("recommendations", [])
            
            html = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #2c3e50, #34495e); color: white; padding: 20px; border-radius: 10px;">
                <h2 style="margin-top: 0;">💡 System Insights Report</h2>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">Health Score</h4>
                        <div style="font-size: 1.8em; font-weight: bold; color: #28a745;">{summary.get('health_score', 0):.1f}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">Metrics Analyzed</h4>
                        <div style="font-size: 1.8em; font-weight: bold; color: #17a2b8;">{summary.get('total_metrics_analyzed', 0)}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">Correlations</h4>
                        <div style="font-size: 1.8em; font-weight: bold; color: #ffc107;">{summary.get('correlations_found', 0)}</div>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <h4 style="margin: 0;">Anomalies</h4>
                        <div style="font-size: 1.8em; font-weight: bold; color: #dc3545;">{summary.get('anomalies_detected', 0)}</div>
                    </div>
                </div>
            """
            
            if recommendations:
                html += """
                <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0;">🎯 Key Recommendations</h3>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                """
                
                for rec in recommendations[:5]:
                    priority = rec.get("priority", "low")
                    priority_color = "#dc3545" if priority == "high" else "#ffc107" if priority == "medium" else "#28a745"
                    
                    html += f"""
                        <li style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px;">
                            <strong style="color: {priority_color};">[{priority.upper()}]</strong>
                            <strong>{rec.get('title', 'No title')}</strong>
                            <br><span style="opacity: 0.9;">{rec.get('description', 'No description')}</span>
                            <br><em style="color: #17a2b8;">Action: {rec.get('action', 'No action specified')}</em>
                        </li>
                    """
                
                html += "</ul></div>"
            
            html += f"""
                <div style="text-align: center; margin-top: 20px; opacity: 0.8;">
                    <small>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
                    <br><small>Data Quality Score: {summary.get('data_quality_score', 0):.1f}%</small>
                </div>
            </div>
            """
            
            return html
            
        except Exception as e:
            logger.error(f"Error creating insights visualization: {e}")
            return f"<div class='error'>Error creating visualization: {str(e)}</div>"
    
    def get_advanced_dashboard(self):
        """Get advanced dashboard with comprehensive visualizations"""
        try:
            logger.info(f"Requesting dashboard from {self.backend_url}/api/v1/analytics/dashboard")
            response = requests.get(f"{self.backend_url}/api/v1/analytics/dashboard", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                dashboard_html = data.get("dashboard_html", "")
                
                if not success:
                    return f"<div class='error'>Backend returned success=false</div>"
                
                if not dashboard_html:
                    return f"<div class='error'>No dashboard HTML received from backend</div>"
                
                logger.info(f"Dashboard HTML received, length: {len(dashboard_html)}")
                
                # Wrap in container
                wrapped_html = f"""
                <div style="background: #1a1a1a; padding: 20px; border-radius: 10px; margin: 10px 0;">
                    <h2 style="color: white; text-align: center; margin-bottom: 20px;">🚀 Advanced Analytics Dashboard</h2>
                    <div style="color: #888; font-size: 12px; text-align: center; margin-bottom: 10px;">
                        Generated: {data.get('generated_at', 'unknown')} | Period: {data.get('data_period_hours', 24)} hours
                    </div>
                    {dashboard_html}
                </div>
                """
                
                return wrapped_html
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Dashboard API error: {error_msg}")
                return f"<div class='error'>Backend Error: {error_msg}</div>"
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to backend: {e}")
            return f"<div class='error'>Cannot connect to backend at {self.backend_url}. Is the backend running on port 8000?</div>"
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            return f"<div class='error'>Backend timeout after 30 seconds. Backend may be overloaded.</div>"
        except Exception as e:
            logger.error(f"Unexpected error getting advanced dashboard: {e}")
            return f"<div class='error'>Unexpected error: {str(e)}</div>"

# Create global instance
advanced_analytics_dashboard = AdvancedAnalyticsDashboard()
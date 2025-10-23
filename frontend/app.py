#!/usr/bin/env python3
"""
ProbePilot Mission Control - Gradio Frontend
Your Mission Control for Kernel Observability

This is the main Gradio application providing the aviation-inspired
dashboard for eBPF probe management and telemetry visualization.
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import asyncio
import json
from typing import Dict, List, Optional
import time

# Import custom components
from components.mission_control import create_mission_control_dashboard
from components.probe_manager import create_probe_manager
from components.analytics import create_analytics_panel
from components.copilot import create_ai_copilot
from themes.aviation_theme import get_aviation_theme
from api.backend_client import BackendClient

class ProbePilotApp:
    """Main ProbePilot Application Class"""
    
    def __init__(self):
        self.backend_client = BackendClient()
        self.theme = get_aviation_theme()
        self.app = None
        
    def create_app(self):
        """Create the main Gradio application"""
        
        # Custom CSS for aviation theme
        custom_css = """
        .gradio-container {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            min-height: 100vh;
        }
        
        .mission-control-header {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
            backdrop-filter: blur(10px);
            padding: 20px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .status-panel {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 15px;
        }
        
        .alert-panel {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 8px;
            padding: 15px;
        }
        
        .probe-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
        }
        
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #10b981;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-green { background-color: #10b981; }
        .status-orange { background-color: #f59e0b; }
        .status-red { background-color: #ef4444; }
        """
        
        # Main application using Gradio Blocks
        with gr.Blocks(
            theme=self.theme,
            css=custom_css,
            title="🛩️ ProbePilot Mission Control",
            analytics_enabled=False
        ) as app:
            
            # Application Header
            gr.HTML("""
            <div class="mission-control-header">
                <h1 style="margin: 0; color: #ffffff; font-size: 2.5em;">
                    🛩️ ProbePilot Mission Control
                </h1>
                <p style="margin: 10px 0 0 0; color: #cbd5e1; font-size: 1.2em;">
                    Your Mission Control for Kernel Observability
                </p>
            </div>
            """)
            
            # Main Navigation Tabs
            with gr.Tabs():
                
                # Mission Control Dashboard
                with gr.TabItem("🎯 Mission Control", id="dashboard"):
                    self._create_dashboard_tab()
                
                # Probe Management
                with gr.TabItem("🔧 Probe Manager", id="probes"):
                    self._create_probe_manager_tab()
                
                # Analytics & Deep Dive
                with gr.TabItem("📊 Analytics", id="analytics"):
                    self._create_analytics_tab()
                
                # AI Copilot
                with gr.TabItem("🤖 Copilot", id="copilot"):
                    self._create_copilot_tab()
                
                # System Settings
                with gr.TabItem("⚙️ Settings", id="settings"):
                    self._create_settings_tab()
        
        self.app = app
        return app
    
    def _create_dashboard_tab(self):
        """Create the main mission control dashboard"""
        
        with gr.Row():
            # System Status Panel
            with gr.Column(scale=1):
                gr.HTML('<h3 style="color: #ffffff;">🚀 System Status</h3>')
                
                system_health = gr.HTML(
                    '<div class="status-panel">'
                    '<span class="status-indicator status-green"></span>'
                    '<strong>All Systems Operational</strong>'
                    '</div>'
                )
                
                active_probes = gr.Number(
                    label="Active Probes",
                    value=12,
                    interactive=False,
                    elem_classes=["metric-value"]
                )
                
                data_rate = gr.Number(
                    label="Data Rate (MB/s)",
                    value=2.4,
                    interactive=False,
                    elem_classes=["metric-value"]
                )
                
                alerts = gr.Number(
                    label="Active Alerts",
                    value=0,
                    interactive=False,
                    elem_classes=["metric-value"]
                )
            
            # Live Metrics Visualization
            with gr.Column(scale=3):
                gr.HTML('<h3 style="color: #ffffff;">📈 Live Telemetry</h3>')
                
                # Real-time metrics plot
                metrics_plot = gr.Plot(
                    label="System Metrics",
                    value=self._generate_sample_metrics()
                )
                
                # Update metrics on button click
                refresh_btn = gr.Button("🔄 Refresh Metrics", variant="secondary")
                refresh_btn.click(
                    fn=self._update_metrics,
                    outputs=metrics_plot
                )
        
        # Quick Actions Panel
        with gr.Row():
            gr.HTML('<h3 style="color: #ffffff;">⚡ Quick Actions</h3>')
            
            with gr.Column():
                deploy_probe_btn = gr.Button("🚀 Deploy Probe", variant="primary")
                stop_probe_btn = gr.Button("🛑 Stop Probe", variant="secondary")
                export_data_btn = gr.Button("📥 Export Data", variant="secondary")
                
        # Recent Activity Feed
        with gr.Row():
            gr.HTML('<h3 style="color: #ffffff;">📋 Recent Activity</h3>')
            
            activity_feed = gr.DataFrame(
                value=self._get_sample_activity(),
                headers=["Time", "Event", "Component", "Status"],
                datatype=["str", "str", "str", "str"],
                interactive=False
            )
    
    def _create_probe_manager_tab(self):
        """Create probe management interface"""
        
        with gr.Row():
            # Probe Deployment
            with gr.Column(scale=1):
                gr.HTML('<h3 style="color: #ffffff;">🔧 Deploy New Probe</h3>')
                
                probe_type = gr.Dropdown(
                    choices=[
                        "TCP Flow Monitor",
                        "HTTP Latency Tracker", 
                        "CPU Performance Profiler",
                        "Memory Usage Monitor",
                        "File System Auditor",
                        "Network Security Scanner"
                    ],
                    label="Probe Type",
                    value="TCP Flow Monitor"
                )
                
                target_system = gr.Textbox(
                    label="Target System",
                    placeholder="hostname or IP address",
                    value="localhost"
                )
                
                probe_config = gr.TextArea(
                    label="Configuration (JSON)",
                    placeholder='{"sampling_rate": 1000, "filters": []}',
                    lines=5
                )
                
                deploy_btn = gr.Button("🚀 Deploy Probe", variant="primary")
                
                deployment_status = gr.HTML("")
                
                # Handle probe deployment
                deploy_btn.click(
                    fn=self._deploy_probe,
                    inputs=[probe_type, target_system, probe_config],
                    outputs=deployment_status
                )
            
            # Active Probes List
            with gr.Column(scale=2):
                gr.HTML('<h3 style="color: #ffffff;">📡 Active Probes</h3>')
                
                probes_table = gr.DataFrame(
                    value=self._get_active_probes(),
                    headers=["ID", "Type", "Target", "Status", "Data Rate", "Uptime"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    interactive=False
                )
                
                with gr.Row():
                    refresh_probes_btn = gr.Button("🔄 Refresh", variant="secondary")
                    stop_selected_btn = gr.Button("🛑 Stop Selected", variant="secondary")
                    restart_selected_btn = gr.Button("♻️ Restart Selected", variant="secondary")
    
    def _create_analytics_tab(self):
        """Create analytics and deep-dive interface"""
        
        gr.HTML('<h3 style="color: #ffffff;">📊 Advanced Analytics</h3>')
        
        with gr.Row():
            # Time Range Selector
            with gr.Column(scale=1):
                time_range = gr.Dropdown(
                    choices=["Last 1 Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days"],
                    label="Time Range",
                    value="Last 1 Hour"
                )
                
                metric_type = gr.Dropdown(
                    choices=["CPU Usage", "Memory Usage", "Network I/O", "Disk I/O", "Custom"],
                    label="Metric Type",
                    value="CPU Usage"
                )
                
                aggregation = gr.Dropdown(
                    choices=["Average", "Maximum", "Minimum", "95th Percentile"],
                    label="Aggregation",
                    value="Average"
                )
            
            # Analytics Visualization
            with gr.Column(scale=3):
                analytics_plot = gr.Plot(
                    label="Detailed Analytics",
                    value=self._generate_analytics_chart()
                )
        
        # Data Export Options
        with gr.Row():
            export_format = gr.Radio(
                choices=["CSV", "JSON", "Excel", "PDF Report"],
                label="Export Format",
                value="CSV"
            )
            
            export_btn = gr.Button("📥 Export Analytics", variant="primary")
            
            export_file = gr.File(label="Download", visible=False)
    
    def _create_copilot_tab(self):
        """Create AI Copilot interface"""
        
        gr.HTML('<h3 style="color: #ffffff;">🤖 ProbePilot AI Copilot</h3>')
        
        # AI Chat Interface
        chatbot = gr.ChatInterface(
            fn=self._copilot_response,
            title="Ask me about your infrastructure...",
            description="I can help you analyze metrics, diagnose issues, and optimize your observability setup.",
            examples=[
                "Why is CPU usage high on node-1?",
                "Show me network latency trends",
                "What probes should I deploy for a web application?",
                "Help me troubleshoot connection timeouts"
            ],
            theme="dark"
        )
        
        # Voice Input (if supported)
        with gr.Row():
            voice_input = gr.Audio(
                label="🎤 Voice Input",
                type="numpy"
            )
            
            voice_btn = gr.Button("🗣️ Ask via Voice", variant="secondary")
    
    def _create_settings_tab(self):
        """Create system settings interface"""
        
        gr.HTML('<h3 style="color: #ffffff;">⚙️ System Configuration</h3>')
        
        with gr.Tabs():
            # General Settings
            with gr.TabItem("General"):
                refresh_interval = gr.Slider(
                    minimum=1,
                    maximum=60,
                    value=5,
                    step=1,
                    label="Dashboard Refresh Interval (seconds)"
                )
                
                data_retention = gr.Slider(
                    minimum=1,
                    maximum=365,
                    value=30,
                    step=1,
                    label="Data Retention (days)"
                )
                
                alert_threshold = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=80,
                    step=1,
                    label="Alert Threshold (%)"
                )
            
            # Authentication
            with gr.TabItem("Authentication"):
                auth_method = gr.Dropdown(
                    choices=["Local", "LDAP", "OAuth", "SAML"],
                    label="Authentication Method",
                    value="Local"
                )
                
                session_timeout = gr.Number(
                    label="Session Timeout (minutes)",
                    value=60
                )
            
            # Notifications
            with gr.TabItem("Notifications"):
                email_alerts = gr.Checkbox(
                    label="Enable Email Alerts",
                    value=True
                )
                
                slack_webhook = gr.Textbox(
                    label="Slack Webhook URL",
                    placeholder="https://hooks.slack.com/...",
                    type="password"
                )
                
                alert_channels = gr.CheckboxGroup(
                    choices=["Email", "Slack", "Teams", "PagerDuty"],
                    label="Alert Channels",
                    value=["Email"]
                )
        
        # Save Settings
        save_settings_btn = gr.Button("💾 Save Configuration", variant="primary")
    
    # Helper Methods
    
    def _generate_sample_metrics(self):
        """Generate sample metrics data for demonstration"""
        
        # Create sample time series data
        now = datetime.now()
        times = [now - timedelta(minutes=x) for x in range(30, 0, -1)]
        
        # Sample CPU, Memory, and Network data
        cpu_data = np.random.normal(45, 10, 30)
        memory_data = np.random.normal(60, 15, 30)
        network_data = np.random.normal(20, 5, 30)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=cpu_data,
            mode='lines+markers',
            name='CPU Usage (%)',
            line=dict(color='#10b981')
        ))
        
        fig.add_trace(go.Scatter(
            x=times,
            y=memory_data,
            mode='lines+markers',
            name='Memory Usage (%)',
            line=dict(color='#3b82f6')
        ))
        
        fig.add_trace(go.Scatter(
            x=times,
            y=network_data,
            mode='lines+markers',
            name='Network I/O (MB/s)',
            line=dict(color='#f59e0b')
        ))
        
        fig.update_layout(
            title="Real-time System Metrics",
            xaxis_title="Time",
            yaxis_title="Value",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=True
        )
        
        return fig
    
    def _update_metrics(self):
        """Update metrics with new data"""
        return self._generate_sample_metrics()
    
    def _get_sample_activity(self):
        """Generate sample activity feed"""
        return pd.DataFrame([
            ["10:45:32", "Probe Deployed", "TCP Monitor", "✅ Success"],
            ["10:44:15", "Alert Triggered", "Memory Usage", "⚠️ Warning"],
            ["10:43:01", "Data Export", "Analytics", "✅ Complete"],
            ["10:41:28", "Probe Updated", "HTTP Tracker", "✅ Success"],
            ["10:40:12", "System Restart", "Node-2", "✅ Complete"]
        ])
    
    def _get_active_probes(self):
        """Get list of active probes"""
        return pd.DataFrame([
            ["probe-001", "TCP Flow Monitor", "web-server-1", "🟢 Running", "1.2 MB/s", "2h 15m"],
            ["probe-002", "HTTP Latency", "api-gateway", "🟢 Running", "0.8 MB/s", "1h 42m"],
            ["probe-003", "CPU Profiler", "database-1", "🟡 Warning", "2.1 MB/s", "45m"],
            ["probe-004", "Memory Monitor", "cache-server", "🟢 Running", "0.5 MB/s", "3h 8m"],
            ["probe-005", "File System", "storage-node", "🔴 Error", "0.0 MB/s", "12m"]
        ])
    
    def _deploy_probe(self, probe_type, target_system, probe_config):
        """Handle probe deployment"""
        # Simulate probe deployment
        time.sleep(1)  # Simulate deployment time
        
        success_html = f"""
        <div class="status-panel" style="border-color: #10b981;">
            <span class="status-indicator status-green"></span>
            <strong>Probe Deployed Successfully!</strong><br>
            Type: {probe_type}<br>
            Target: {target_system}<br>
            Status: Initializing...
        </div>
        """
        
        return success_html
    
    def _generate_analytics_chart(self):
        """Generate analytics visualization"""
        # Sample data for analytics
        dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
        values = np.cumsum(np.random.randn(len(dates))) + 100
        
        fig = px.line(
            x=dates,
            y=values,
            title="30-Day Trend Analysis",
            labels={'x': 'Date', 'y': 'Metric Value'}
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        return fig
    
    def _copilot_response(self, message, history):
        """AI Copilot response handler"""
        
        # Simple rule-based responses for demo
        message_lower = message.lower()
        
        if "cpu" in message_lower and "high" in message_lower:
            return "I see you're experiencing high CPU usage. Let me analyze the data... Based on recent metrics, the spike appears to be related to increased process scheduling. I recommend checking for memory leaks or adding CPU profiling probes for deeper analysis."
        
        elif "network" in message_lower and "latency" in message_lower:
            return "Network latency analysis shows varying patterns. I can see average latency is 45ms with some spikes to 200ms. This could indicate network congestion or DNS resolution issues. Would you like me to deploy additional network monitoring probes?"
        
        elif "deploy" in message_lower and "probe" in message_lower:
            return "For deploying probes, I recommend starting with these essentials: 1) TCP Flow Monitor for network visibility, 2) CPU Performance Profiler for system analysis, 3) HTTP Latency Tracker for application monitoring. What type of application are you monitoring?"
        
        elif "troubleshoot" in message_lower:
            return "I'll help you troubleshoot! First, let me check the current system status... I notice some elevated metrics in the memory usage area. Let's start by examining the recent probe data and identify any anomalies. Would you like me to run a diagnostic scan?"
        
        else:
            return f"I understand you're asking about: '{message}'. Let me analyze your current infrastructure data and provide insights. Could you be more specific about which metrics or systems you'd like me to focus on?"
    
    def launch(self, **kwargs):
        """Launch the ProbePilot application"""
        if not self.app:
            self.app = self.create_app()
        
        default_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,
            "debug": True
        }
        
        # Override defaults with provided kwargs
        launch_kwargs = {**default_kwargs, **kwargs}
        
        print("🛩️ Launching ProbePilot Mission Control...")
        print(f"🌐 Access at: http://localhost:{launch_kwargs['server_port']}")
        
        self.app.launch(**launch_kwargs)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="ProbePilot Mission Control")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--share", action="store_true", help="Create public URL")
    
    args = parser.parse_args()
    
    # Create and launch the application
    app = ProbePilotApp()
    app.launch(
        server_name=args.host,
        server_port=args.port,
        debug=args.debug,
        share=args.share
    )

if __name__ == "__main__":
    main()
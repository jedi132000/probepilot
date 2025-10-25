#!/usr/bin/env python3
"""
ProbePilot Mission Control - Gradio Frontend
Your Mission Control for Kernel Observability

This is the main Gradio application providing the aviation-inspired
dashboard for e        # System Status Panel
        with gr.Column(scale=1):
            gr.HTML('<h3 style="color: #ffffff;">⚡ System Status</h3>')
            
            with gr.Column():
                gr.HTML('<div style="color: #10b981;">🟢 Backend: Connected</div>')
                gr.HTML('<div style="color: #10b981;">🟢 Probes: Active</div>')
                gr.HTML('<div style="color: #10b981;">🟢 Metrics: Live</div>')e management and telemetry visualization.
"""

import os
import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import asyncio
import json
import requests
from typing import Dict, List, Optional
import time
import psutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
                    create_ai_copilot()
                
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
        
        # Data Export Panel
        with gr.Row():
            gr.HTML('<h3 style="color: #ffffff;">📥 Data Export</h3>')
            
            with gr.Column():
                export_data_btn = gr.Button("📥 Export All Probe Data", variant="primary")
                export_status = gr.Textbox(
                    label="Export Status",
                    interactive=False,
                    visible=False
                )
                
                # Wire up export button
                export_data_btn.click(
                    self._export_probe_data,
                    outputs=[gr.File(), export_status]
                )
                
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
                    headers=["ID", "Name", "Target", "Status", "Data Rate", "Uptime"],
                    datatype=["str", "str", "str", "str", "str", "str"],
                    interactive=False,
                    value=[]  # Start empty, will populate on refresh
                )
                
                with gr.Row():
                    refresh_probes_btn = gr.Button("🔄 Refresh", variant="secondary")
                
                # Probe management controls
                with gr.Row():
                    probe_id_input = gr.Textbox(
                        label="Probe ID",
                        placeholder="Enter probe ID (e.g., probe-abc123)",
                        scale=3
                    )
                    stop_probe_btn = gr.Button("🛑 Stop Probe", variant="secondary", scale=1)
                    restart_probe_btn = gr.Button("♻️ Restart Probe", variant="secondary", scale=1)
                
                # Status message for probe operations
                probe_operation_status = gr.Textbox(
                    label="Operation Status",
                    interactive=False,
                    visible=True,
                    value=""
                )
                
                # Wire up the refresh button to update the probes table
                refresh_probes_btn.click(
                    fn=self._get_active_probes,
                    outputs=probes_table
                )
                
                # Wire up stop button
                stop_probe_btn.click(
                    self._stop_probe,
                    inputs=[probe_id_input],
                    outputs=[probes_table, probe_operation_status, probe_id_input]
                )
                
                # Wire up restart button
                restart_probe_btn.click(
                    self._restart_probe,
                    inputs=[probe_id_input],
                    outputs=[probes_table, probe_operation_status, probe_id_input]
                )
    
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
        """Get real system activity from backend"""
        from datetime import datetime
        
        try:
            # Get real system metrics for activity detection
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            current_time = datetime.now().strftime("%H:%M:%S")
            activities = []
            
            # Add real system events
            if cpu_percent > 50:
                activities.append([current_time, "High CPU Usage", f"{cpu_percent:.1f}%", "⚠️ Warning"])
            
            if memory.percent > 70:
                activities.append([current_time, "Memory Alert", f"{memory.percent:.1f}%", "⚠️ Warning"])
            
            if disk.percent > 80:
                activities.append([current_time, "Disk Space", f"{disk.percent:.1f}%", "⚠️ Warning"])
            
            # Get recent probe activity from backend
            try:
                response = requests.get(f"http://localhost:8000/api/v1/probes/")
                if response.status_code == 200:
                    probes = response.json()
                    if probes:
                        latest_probe = max(probes, key=lambda p: p.get('created_at', ''))
                        probe_time = datetime.fromisoformat(latest_probe['created_at'].replace('Z', '+00:00')).strftime("%H:%M:%S")
                        activities.append([probe_time, "Probe Active", latest_probe['name'], "🟢 Running"])
            except:
                pass
            
            # Add some default entries if no alerts
            if not activities:
                activities = [
                    [current_time, "System Monitor", "All systems normal", "✅ Healthy"],
                    [(datetime.now() - timedelta(minutes=1)).strftime("%H:%M:%S"), "Metrics Updated", "Live data collection", "✅ Active"],
                    [(datetime.now() - timedelta(minutes=2)).strftime("%H:%M:%S"), "Backend Connected", "API responding", "🟢 Online"]
                ]
            
            return pd.DataFrame(activities[:5], columns=["Time", "Event", "Details", "Status"])
            
        except Exception as e:
            # Fallback to basic system info
            current_time = datetime.now().strftime("%H:%M:%S")
            return pd.DataFrame([
                [current_time, "System Active", "ProbePilot running", "🟢 Online"],
                [(datetime.now() - timedelta(minutes=1)).strftime("%H:%M:%S"), "Monitoring", "Collecting metrics", "✅ Active"]
            ], columns=["Time", "Event", "Details", "Status"])
    
    def _get_active_probes(self):
        """Get list of active probes from backend"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            probes = loop.run_until_complete(self.backend_client.get_active_probes())
            loop.close()
            
            if probes:
                probe_data = []
                for probe in probes:
                    # Format status with emoji
                    status = probe.get('status', 'unknown').lower()
                    if status == 'running':
                        status_display = "🟢 Running"
                    elif status == 'error':
                        status_display = "🔴 Error"
                    elif status == 'stopped':
                        status_display = "⚪ Stopped"
                    elif status == 'loading':
                        status_display = "📥 Loading"
                    elif status == 'attaching':
                        status_display = "🎯 Attaching"
                    elif status == 'initializing':
                        status_display = "� Initializing"
                    else:
                        status_display = f"⚪ {status.title()}"
                    
                    probe_data.append([
                        probe.get('id', 'N/A'),
                        probe.get('name', 'Unknown'),
                        probe.get('target', 'localhost'),
                        status_display,
                        probe.get('data_rate', '0.0 MB/s'),
                        probe.get('uptime', '0s')
                    ])
                
                return pd.DataFrame(probe_data, columns=["ID", "Name", "Target", "Status", "Data Rate", "Uptime"])
            else:
                # No probes found
                return pd.DataFrame([
                    ["No probes", "Deploy a probe", "to get started", "⚪ Inactive", "0.0 MB/s", "0s"]
                ], columns=["ID", "Name", "Target", "Status", "Data Rate", "Uptime"])
                
        except Exception as e:
            # Fallback to error message
            return pd.DataFrame([
                ["Error", f"Backend connection failed: {str(e)}", "localhost", "🔴 Error", "0.0 MB/s", "0s"]
            ], columns=["ID", "Name", "Target", "Status", "Data Rate", "Uptime"])
    
    def _stop_probe(self, probe_id):
        """Stop a specific probe by ID"""
        
        try:
            if not probe_id or not probe_id.strip():
                return self._get_active_probes(), "❌ Please enter a probe ID", ""
            
            probe_id = probe_id.strip()
            
            # Stop the probe
            response = requests.delete(f"http://localhost:8000/api/v1/probes/{probe_id}")
            
            if response.status_code == 200:
                status = f"✅ Successfully stopped probe: {probe_id}"
                # Refresh the probes table
                updated_df = self._get_active_probes()
                return updated_df, status, ""  # Clear the input field
            else:
                error_msg = f"❌ Failed to stop probe {probe_id} (HTTP {response.status_code})"
                if response.text:
                    try:
                        error_detail = response.json().get('detail', response.text)
                        error_msg += f": {error_detail}"
                    except:
                        error_msg += f": {response.text}"
                return self._get_active_probes(), error_msg, probe_id
            
        except Exception as e:
            return self._get_active_probes(), f"❌ Error stopping probe: {str(e)}", probe_id
    
    def _restart_probe(self, probe_id):
        """Restart a specific probe by ID"""
        
        try:
            if not probe_id or not probe_id.strip():
                return self._get_active_probes(), "❌ Please enter a probe ID", ""
            
            probe_id = probe_id.strip()
            
            # Restart the probe
            response = requests.post(f"http://localhost:8000/api/v1/probes/{probe_id}/restart")
            
            if response.status_code == 200:
                status = f"♻️ Successfully restarted probe: {probe_id}"
                # Refresh the probes table
                updated_df = self._get_active_probes()
                return updated_df, status, ""  # Clear the input field
            else:
                error_msg = f"❌ Failed to restart probe {probe_id} (HTTP {response.status_code})"
                if response.text:
                    try:
                        error_detail = response.json().get('detail', response.text)
                        error_msg += f": {error_detail}"
                    except:
                        error_msg += f": {response.text}"
                return self._get_active_probes(), error_msg, probe_id
            
        except Exception as e:
            return self._get_active_probes(), f"❌ Error restarting probe: {str(e)}", probe_id
    
    def _export_probe_data(self):
        """Export all probe data to CSV"""
        try:
            import csv
            import io
            from datetime import datetime
            
            # Get current probe data
            response = requests.get("http://localhost:8000/api/v1/probes/")
            if response.status_code != 200:
                return None, "❌ Failed to fetch probe data from backend"
                
            probes = response.json()
            if not probes:
                return None, "❌ No probe data available for export"
            
            # Create CSV content
            output = io.StringIO()
            fieldnames = ['probe_id', 'name', 'type', 'target', 'status', 'data_rate', 'uptime', 'created_at']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for probe in probes:
                writer.writerow({
                    'probe_id': probe.get('id', ''),
                    'name': probe.get('name', ''),
                    'type': probe.get('type', ''),
                    'target': probe.get('target', ''),
                    'status': probe.get('status', ''),
                    'data_rate': probe.get('data_rate', ''),
                    'uptime': probe.get('uptime', ''),
                    'created_at': probe.get('created_at', '')
                })
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"probepilot_export_{timestamp}.csv"
            
            csv_content = output.getvalue()
            output.close()
            
            # Create temporary file for download
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
            temp_file.write(csv_content)
            temp_file.close()
            
            return temp_file.name, f"✅ Exported {len(probes)} probes to {filename}"
            
        except Exception as e:
            return None, f"❌ Export failed: {str(e)}"
    
    def _deploy_probe(self, probe_type, target_system, probe_config):
        """Handle probe deployment"""
        try:
            # Prepare probe configuration for backend API
            probe_config_data = {
                "name": f"{probe_type} Probe",
                "type": probe_type.lower().replace(" ", "-"),
                "target": target_system,
                "config": probe_config if isinstance(probe_config, dict) else {},
                "sampling_rate": 1000,
                "filters": []
            }
            
            # Deploy probe via backend API using synchronous requests
            
            response = requests.post(
                "http://localhost:8000/api/v1/probes",
                json=probe_config_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text[:200]}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"DEBUG: Parsed result: {result}")
                except Exception as json_error:
                    return f"""
                    <div class="status-panel" style="border-color: #ef4444;">
                        <span class="status-indicator status-red"></span>
                        <strong>JSON Parse Error!</strong><br>
                        Type: {probe_type}<br>
                        Error: {str(json_error)}<br>
                        Response: {response.text[:100]}
                    </div>
                    """
            else:
                return f"""
                <div class="status-panel" style="border-color: #ef4444;">
                    <span class="status-indicator status-red"></span>
                    <strong>HTTP Error!</strong><br>
                    Type: {probe_type}<br>
                    Status: {response.status_code}<br>
                    Response: {response.text[:100]}
                </div>
                """
            
            if result and result.get("success"):
                probe_id = result.get("probe_id", "unknown")
                
                # Get current status from backend
                try:
                    import time
                    time.sleep(1)  # Brief pause to let probe initialize
                    status_response = requests.get(f"http://localhost:8000/api/v1/probes/{probe_id}")
                    if status_response.status_code == 200:
                        current_probe = status_response.json()
                        current_status = current_probe.get('status', 'initializing').title()
                        data_rate = current_probe.get('data_rate', '0.0 MB/s')
                    else:
                        current_status = "Initializing"
                        data_rate = "0.0 MB/s"
                except:
                    current_status = "Initializing"
                    data_rate = "0.0 MB/s"
                
                success_html = f"""
                <div style="color: #28a745; background: #d4edda; padding: 10px; border-radius: 5px; margin: 10px 0;">
                    <strong>🚀 Probe Deployed Successfully!</strong><br>
                    ID: {probe_id}<br>
                    Type: {probe_type}<br>
                    Target: {target_system}<br>
                    Status: {current_status}<br>
                    Data Rate: {data_rate}<br>
                    <small style="color: #666;">🔄 Refresh Active Probes table to see live status</small>
                </div>
                """
                return success_html
            else:
                error_msg = result.get("error", "Unknown error")
                error_html = f"""
                <div class="status-panel" style="border-color: #ef4444;">
                    <span class="status-indicator status-red"></span>
                    <strong>Probe Deployment Failed!</strong><br>
                    Type: {probe_type}<br>
                    Target: {target_system}<br>
                    Error: {error_msg}
                </div>
                """
                return error_html
                
        except Exception as e:
            error_html = f"""
            <div class="status-panel" style="border-color: #ef4444;">
                <span class="status-indicator status-red"></span>
                <strong>Deployment Error!</strong><br>
                Type: {probe_type}<br>
                Target: {target_system}<br>
                Error: {str(e)}
            </div>
            """
            return error_html
    
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
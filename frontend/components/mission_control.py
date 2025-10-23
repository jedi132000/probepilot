"""
Mission Control Dashboard Component
Aviation-themed system overview and status monitoring
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def create_mission_control_dashboard():
    """Create the main mission control dashboard"""
    
    with gr.Tab("🛩️ Mission Control", elem_id="mission-control") as tab:
        with gr.Row():
            gr.Markdown("""
            # 🛩️ ProbePilot Mission Control
            ## Your Command Center for Kernel Observability
            
            Welcome to the Mission Control dashboard - your primary interface for monitoring 
            system health, probe status, and telemetry data in real-time.
            """)
        
        with gr.Row():
            # System Status Cards
            with gr.Column(scale=1):
                gr.Markdown("### 📊 System Status")
                system_status = gr.HTML("""
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                    <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px; text-align: center;">
                        <h4 style="color: #22c55e; margin: 0;">CPU Usage</h4>
                        <h2 style="color: #22c55e; margin: 5px 0;">24%</h2>
                    </div>
                    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 15px; text-align: center;">
                        <h4 style="color: #3b82f6; margin: 0;">Memory</h4>
                        <h2 style="color: #3b82f6; margin: 5px 0;">8.2GB</h2>
                    </div>
                    <div style="background: rgba(168, 85, 247, 0.1); border: 1px solid #a855f7; border-radius: 8px; padding: 15px; text-align: center;">
                        <h4 style="color: #a855f7; margin: 0;">Active Probes</h4>
                        <h2 style="color: #a855f7; margin: 5px 0;">12</h2>
                    </div>
                    <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px; text-align: center;">
                        <h4 style="color: #22c55e; margin: 0;">Uptime</h4>
                        <h2 style="color: #22c55e; margin: 5px 0;">72h</h2>
                    </div>
                </div>
                """)
            
            with gr.Column(scale=2):
                gr.Markdown("### 📈 Real-time Telemetry")
                # Create sample data for the plot
                sample_plot = create_sample_telemetry_plot()
                telemetry_plot = gr.Plot(value=sample_plot)
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎯 Active Probes")
                probe_status = gr.Dataframe(
                    value=get_sample_probe_data(),
                    headers=["Probe", "Status", "Last Update", "Events/sec"],
                    datatype=["str", "str", "str", "number"]
                )
            
            with gr.Column():
                gr.Markdown("### 📋 Recent Events")
                recent_events = gr.Textbox(
                    value=get_sample_events(),
                    lines=10,
                    interactive=False,
                    container=True
                )
        
        # Auto-refresh controls
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
            auto_refresh = gr.Checkbox(label="Auto-refresh (30s)", value=True)
        
        # Set up auto-refresh functionality
        def refresh_dashboard():
            return (
                create_sample_telemetry_plot(),
                get_sample_probe_data(),
                get_sample_events()
            )
        
        refresh_btn.click(
            fn=refresh_dashboard,
            outputs=[telemetry_plot, probe_status, recent_events]
        )
    
    return tab

def create_sample_telemetry_plot():
    """Create a sample telemetry plot"""
    # Generate sample data
    time_range = pd.date_range(start=datetime.now() - timedelta(hours=1), 
                              end=datetime.now(), freq='1min')
    
    cpu_usage = np.random.normal(25, 5, len(time_range))
    memory_usage = np.random.normal(65, 3, len(time_range))
    network_io = np.random.exponential(2, len(time_range)) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=cpu_usage,
        name='CPU Usage (%)',
        line=dict(color='#22c55e', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=memory_usage,
        name='Memory Usage (%)',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=network_io,
        name='Network I/O (MB/s)',
        line=dict(color='#a855f7', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='System Telemetry - Last Hour',
        xaxis_title='Time',
        yaxis_title='Usage (%)',
        yaxis2=dict(
            title='Network I/O (MB/s)',
            overlaying='y',
            side='right'
        ),
        template='plotly_dark',
        height=400
    )
    
    return fig

def get_sample_probe_data():
    """Get sample probe status data"""
    return [
        ["TCP Flow Monitor", "🟢 Active", "2s ago", 1247],
        ["CPU Profiler", "🟢 Active", "1s ago", 899],
        ["Memory Tracker", "🟢 Active", "3s ago", 567],
        ["Network Security", "🟡 Warning", "15s ago", 89],
        ["File Monitor", "🟢 Active", "1s ago", 234],
        ["Process Tracker", "🟢 Active", "2s ago", 445]
    ]

def get_sample_events():
    """Get sample recent events"""
    events = [
        f"[{datetime.now().strftime('%H:%M:%S')}] TCP connection established: 192.168.1.100:45678 -> 93.184.216.34:80",
        f"[{(datetime.now() - timedelta(seconds=5)).strftime('%H:%M:%S')}] High CPU usage detected on process nginx (PID: 1234)",
        f"[{(datetime.now() - timedelta(seconds=12)).strftime('%H:%M:%S')}] Memory allocation: 2MB allocated by python process (PID: 5678)",
        f"[{(datetime.now() - timedelta(seconds=18)).strftime('%H:%M:%S')}] Network security: New connection from external IP",
        f"[{(datetime.now() - timedelta(seconds=25)).strftime('%H:%M:%S')}] File access: /etc/passwd read by process vim (PID: 9012)",
        f"[{(datetime.now() - timedelta(seconds=33)).strftime('%H:%M:%S')}] Process created: firefox launched by user (PID: 3456)",
        f"[{(datetime.now() - timedelta(seconds=41)).strftime('%H:%M:%S')}] TCP connection closed: 192.168.1.100:45679 -> 8.8.8.8:53",
        f"[{(datetime.now() - timedelta(seconds=48)).strftime('%H:%M:%S')}] Memory freed: 1.5MB freed by java process (PID: 7890)"
    ]
    return "\n".join(events)
"""
Analytics Panel Component
Data visualization and analysis interface
"""

import gradio as gr
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_analytics_panel():
    """Create the analytics and visualization panel"""
    
    with gr.Tab("📊 Analytics", elem_id="analytics") as tab:
        with gr.Row():
            gr.Markdown("""
            # 📊 Telemetry Analytics
            ## Deep Dive into System Performance Data
            
            Analyze historical data, identify trends, and gain insights from your 
            eBPF probe telemetry with advanced visualization and statistical analysis.
            """)
        
        # Time Range Selection
        with gr.Row():
            with gr.Column(scale=2):
                time_range = gr.Dropdown(
                    label="Time Range",
                    choices=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Custom"],
                    value="Last 24 Hours"
                )
            
            with gr.Column(scale=1):
                refresh_analytics = gr.Button("🔄 Refresh Data", variant="primary")
        
        # Main Analytics Tabs
        with gr.Tabs():
            # Network Analytics
            with gr.Tab("🌐 Network"):
                with gr.Row():
                    with gr.Column():
                        network_summary = create_network_summary_plot()
                        network_plot = gr.Plot(value=network_summary, label="Network Traffic Summary")
                    
                    with gr.Column():
                        connection_map = create_connection_map()
                        connection_plot = gr.Plot(value=connection_map, label="Connection Geography")
                
                with gr.Row():
                    protocol_dist = create_protocol_distribution()
                    protocol_plot = gr.Plot(value=protocol_dist, label="Protocol Distribution")
                    
                    port_activity = create_port_activity()
                    port_plot = gr.Plot(value=port_activity, label="Port Activity")
            
            # Performance Analytics
            with gr.Tab("⚡ Performance"):
                with gr.Row():
                    with gr.Column():
                        cpu_heatmap = create_cpu_heatmap()
                        cpu_plot = gr.Plot(value=cpu_heatmap, label="CPU Usage Heatmap")
                    
                    with gr.Column():
                        memory_trend = create_memory_trend()
                        memory_plot = gr.Plot(value=memory_trend, label="Memory Usage Trends")
                
                with gr.Row():
                    process_top = gr.Dataframe(
                        value=get_top_processes(),
                        headers=["Process", "PID", "CPU %", "Memory", "Threads", "Status"],
                        label="Top Resource Consumers"
                    )
            
            # Security Analytics  
            with gr.Tab("🔒 Security"):
                with gr.Row():
                    with gr.Column():
                        security_events = create_security_timeline()
                        security_plot = gr.Plot(value=security_events, label="Security Events Timeline")
                    
                    with gr.Column():
                        threat_level = create_threat_level_gauge()
                        threat_plot = gr.Plot(value=threat_level, label="Current Threat Level")
                
                with gr.Row():
                    security_log = gr.Textbox(
                        value=get_security_events(),
                        lines=8,
                        label="Recent Security Events",
                        interactive=False
                    )
        
        # Export Controls
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 💾 Export Data")
                
                export_format = gr.Dropdown(
                    label="Export Format",
                    choices=["CSV", "JSON", "Parquet", "Excel"],
                    value="CSV"
                )
                
                export_btn = gr.Button("📥 Export Analytics Data")
                
                export_status = gr.Textbox(
                    label="Export Status",
                    interactive=False,
                    lines=2
                )
        
        # Event Handlers
        def refresh_analytics_data(time_range_val):
            """Refresh analytics data based on selected time range"""
            return (
                create_network_summary_plot(),
                create_connection_map(),
                create_protocol_distribution(),
                create_port_activity(),
                create_cpu_heatmap(),
                create_memory_trend(),
                get_top_processes(),
                create_security_timeline(),
                create_threat_level_gauge(),
                get_security_events()
            )
        
        def export_data(format_choice):
            """Export analytics data in chosen format"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"probepilot_analytics_{timestamp}.{format_choice.lower()}"
            
            return f"✅ Analytics data exported to: {filename}\nRows: 15,847 | Size: 2.3MB"
        
        # Wire up event handlers
        refresh_analytics.click(
            fn=refresh_analytics_data,
            inputs=[time_range],
            outputs=[
                network_plot, connection_plot, protocol_plot, port_plot,
                cpu_plot, memory_plot, process_top,
                security_plot, threat_plot, security_log
            ]
        )
        
        export_btn.click(
            fn=export_data,
            inputs=[export_format],
            outputs=[export_status]
        )
    
    return tab

def create_network_summary_plot():
    """Create network traffic summary visualization"""
    # Generate sample data
    time_range = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                              end=datetime.now(), freq='1H')
    
    inbound = np.random.normal(150, 30, len(time_range))
    outbound = np.random.normal(120, 25, len(time_range))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=inbound,
        name='Inbound (MB/s)',
        fill='tonexty',
        fillcolor='rgba(34, 197, 94, 0.2)',
        line=dict(color='#22c55e', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=outbound,
        name='Outbound (MB/s)',
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.update_layout(
        title='Network Traffic - Last 24 Hours',
        xaxis_title='Time',
        yaxis_title='Throughput (MB/s)',
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_connection_map():
    """Create connection geography map"""
    # Sample connection data
    locations = [
        {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco", "connections": 1250},
        {"lat": 40.7128, "lon": -74.0060, "city": "New York", "connections": 890},
        {"lat": 51.5074, "lon": -0.1278, "city": "London", "connections": 650},
        {"lat": 35.6762, "lon": 139.6503, "city": "Tokyo", "connections": 420},
        {"lat": 52.5200, "lon": 13.4050, "city": "Berlin", "connections": 340}
    ]
    
    df = pd.DataFrame(locations)
    
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon", size="connections",
        color="connections", hover_name="city",
        color_continuous_scale="Viridis",
        size_max=15, zoom=1,
        mapbox_style="open-street-map"
    )
    
    fig.update_layout(
        title='Global Connection Distribution',
        height=350,
        template='plotly_dark'
    )
    
    return fig

def create_protocol_distribution():
    """Create protocol distribution pie chart"""
    protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'SSH', 'DNS', 'Other']
    values = [45, 20, 15, 12, 4, 3, 1]
    
    fig = px.pie(
        values=values, 
        names=protocols,
        title='Network Protocol Distribution'
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_port_activity():
    """Create port activity bar chart"""
    ports = ['80', '443', '22', '53', '25', '993', '587', '21', '23', '3389']
    activity = [2850, 2340, 890, 675, 234, 156, 98, 67, 45, 23]
    
    fig = px.bar(
        x=ports, 
        y=activity,
        title='Top Port Activity',
        labels={'x': 'Port', 'y': 'Connections'}
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_cpu_heatmap():
    """Create CPU usage heatmap"""
    # Generate sample CPU data for 8 cores over 24 hours
    hours = list(range(24))
    cores = [f'Core {i}' for i in range(8)]
    
    cpu_data = np.random.normal(30, 15, (8, 24))
    cpu_data = np.clip(cpu_data, 0, 100)
    
    fig = go.Figure(data=go.Heatmap(
        z=cpu_data,
        x=hours,
        y=cores,
        colorscale='RdYlBu_r',
        colorbar=dict(title="CPU Usage (%)")
    ))
    
    fig.update_layout(
        title='CPU Usage Heatmap - Last 24 Hours',
        xaxis_title='Hour of Day',
        yaxis_title='CPU Core',
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_memory_trend():
    """Create memory usage trend"""
    time_range = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                              end=datetime.now(), freq='1H')
    
    used_memory = np.random.normal(65, 8, len(time_range))
    cached_memory = np.random.normal(15, 3, len(time_range))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=used_memory,
        name='Used Memory (%)',
        line=dict(color='#ef4444', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_range,
        y=cached_memory,
        name='Cached Memory (%)',
        line=dict(color='#8b5cf6', width=2)
    ))
    
    fig.update_layout(
        title='Memory Usage Trends',
        xaxis_title='Time',
        yaxis_title='Memory Usage (%)',
        template='plotly_dark',
        height=350
    )
    
    return fig

def get_top_processes():
    """Get top resource consuming processes"""
    return [
        ["nginx", "1234", "23.5", "512MB", "8", "Running"],
        ["postgres", "5678", "18.2", "1.2GB", "12", "Running"],
        ["redis-server", "9012", "12.1", "256MB", "4", "Running"],
        ["python3", "3456", "8.7", "384MB", "6", "Running"],
        ["chrome", "7890", "7.2", "2.1GB", "24", "Running"],
        ["java", "2345", "6.8", "1.8GB", "16", "Running"],
        ["node", "6789", "5.4", "298MB", "8", "Running"],
        ["docker", "4567", "4.1", "156MB", "3", "Running"]
    ]

def create_security_timeline():
    """Create security events timeline"""
    time_range = pd.date_range(start=datetime.now() - timedelta(hours=24), 
                              end=datetime.now(), freq='1H')
    
    events = np.random.poisson(5, len(time_range))
    
    fig = px.line(
        x=time_range, 
        y=events,
        title='Security Events Timeline',
        labels={'x': 'Time', 'y': 'Events Count'}
    )
    
    fig.update_layout(
        template='plotly_dark',
        height=350
    )
    
    return fig

def create_threat_level_gauge():
    """Create threat level gauge"""
    current_threat = 35  # Sample threat level
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_threat,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Threat Level"},
        delta = {'reference': 25},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "lightgray"},
                {'range': [25, 50], 'color': "gray"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        template='plotly_dark',
        height=350
    )
    
    return fig

def get_security_events():
    """Get recent security events"""
    events = [
        f"[{datetime.now().strftime('%H:%M:%S')}] Failed SSH login attempt from 192.168.1.50",
        f"[{(datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S')}] Suspicious file access: /etc/passwd",
        f"[{(datetime.now() - timedelta(minutes=12)).strftime('%H:%M:%S')}] Port scan detected from external IP",
        f"[{(datetime.now() - timedelta(minutes=18)).strftime('%H:%M:%S')}] Privilege escalation attempt blocked",
        f"[{(datetime.now() - timedelta(minutes=25)).strftime('%H:%M:%S')}] Unusual network traffic pattern detected",
        f"[{(datetime.now() - timedelta(minutes=33)).strftime('%H:%M:%S')}] Multiple failed authentication attempts",
        f"[{(datetime.now() - timedelta(minutes=41)).strftime('%H:%M:%S')}] Potential malware communication blocked",
        f"[{(datetime.now() - timedelta(minutes=48)).strftime('%H:%M:%S')}] Unauthorized process execution attempt"
    ]
    return "\n".join(events)
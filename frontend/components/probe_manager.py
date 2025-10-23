"""
Probe Manager Component
eBPF probe deployment and management interface
"""

import gradio as gr
import json
from datetime import datetime

def create_probe_manager():
    """Create the probe management interface"""
    
    with gr.Tab("🔬 Probe Manager", elem_id="probe-manager") as tab:
        with gr.Row():
            gr.Markdown("""
            # 🔬 eBPF Probe Manager
            ## Deploy and Manage Observability Probes
            
            Control your eBPF probes from this central management interface. Deploy new probes,
            configure existing ones, and monitor their health and performance.
            """)
        
        with gr.Row():
            # Available Probes
            with gr.Column(scale=1):
                gr.Markdown("### 📦 Available Probes")
                
                available_probes = gr.Dataframe(
                    value=get_available_probes(),
                    headers=["Probe", "Category", "Version", "Status"],
                    datatype=["str", "str", "str", "str"],
                    interactive=False
                )
                
                with gr.Row():
                    deploy_btn = gr.Button("🚀 Deploy Selected", variant="primary")
                    refresh_btn = gr.Button("🔄 Refresh List")
            
            # Probe Configuration
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Probe Configuration")
                
                probe_name = gr.Textbox(
                    label="Probe Name",
                    placeholder="Enter probe identifier..."
                )
                
                probe_category = gr.Dropdown(
                    label="Category",
                    choices=["Network", "Performance", "Memory", "Security", "Custom"],
                    value="Network"
                )
                
                sampling_rate = gr.Slider(
                    label="Sampling Rate (Hz)",
                    minimum=1,
                    maximum=1000,
                    value=100,
                    step=1
                )
                
                filter_expression = gr.Textbox(
                    label="Filter Expression",
                    placeholder="pid > 1000 AND comm != 'systemd'",
                    lines=2
                )
                
                output_format = gr.Dropdown(
                    label="Output Format",
                    choices=["JSON", "CSV", "Protobuf", "Raw"],
                    value="JSON"
                )
        
        with gr.Row():
            # Deployed Probes
            with gr.Column():
                gr.Markdown("### 🎯 Deployed Probes")
                
                deployed_probes = gr.Dataframe(
                    value=get_deployed_probes(),
                    headers=["Probe", "Status", "Uptime", "Events", "CPU %", "Memory"],
                    datatype=["str", "str", "str", "number", "number", "str"]
                )
                
                with gr.Row():
                    stop_btn = gr.Button("⏹️ Stop", variant="secondary")
                    restart_btn = gr.Button("🔄 Restart", variant="secondary")
                    remove_btn = gr.Button("🗑️ Remove", variant="stop")
        
        with gr.Row():
            # Probe Logs
            with gr.Column():
                gr.Markdown("### 📋 Probe Logs")
                
                probe_logs = gr.Textbox(
                    value=get_sample_probe_logs(),
                    lines=12,
                    interactive=False,
                    container=True,
                    show_copy_button=True
                )
                
                with gr.Row():
                    clear_logs_btn = gr.Button("🧹 Clear Logs")
                    export_logs_btn = gr.Button("💾 Export Logs")
        
        # Probe Templates
        with gr.Row():
            gr.Markdown("### 📝 Quick Deploy Templates")
            
            with gr.Column(scale=1):
                tcp_template_btn = gr.Button("🌐 TCP Flow Monitor", variant="primary")
                gr.Markdown("*Monitor TCP connections and data flow*")
            
            with gr.Column(scale=1):
                cpu_template_btn = gr.Button("⚡ CPU Profiler", variant="primary")
                gr.Markdown("*Profile CPU usage and process scheduling*")
            
            with gr.Column(scale=1):
                memory_template_btn = gr.Button("🧠 Memory Tracker", variant="primary")
                gr.Markdown("*Track memory allocations and detect leaks*")
        
        # Event handlers
        def deploy_probe(name, category, rate, filter_expr, output_fmt):
            if not name:
                return "❌ Error: Probe name is required"
            
            config = {
                "name": name,
                "category": category,
                "sampling_rate": rate,
                "filter": filter_expr,
                "output_format": output_fmt,
                "timestamp": datetime.now().isoformat()
            }
            
            return f"✅ Probe '{name}' deployment initiated with config:\n{json.dumps(config, indent=2)}"
        
        def deploy_template(template_name):
            templates = {
                "TCP Flow Monitor": {
                    "name": "tcp-flow-monitor",
                    "category": "Network",
                    "sampling_rate": 100,
                    "filter": "tcp",
                    "output_format": "JSON"
                },
                "CPU Profiler": {
                    "name": "cpu-profiler",
                    "category": "Performance", 
                    "sampling_rate": 99,
                    "filter": "pid > 0",
                    "output_format": "JSON"
                },
                "Memory Tracker": {
                    "name": "memory-tracker",
                    "category": "Memory",
                    "sampling_rate": 50,
                    "filter": "size > 1024",
                    "output_format": "JSON"
                }
            }
            
            if template_name in templates:
                config = templates[template_name]
                return (
                    config["name"],
                    config["category"],
                    config["sampling_rate"],
                    config["filter"],
                    config["output_format"]
                )
            
            return ("", "Network", 100, "", "JSON")
        
        # Wire up the event handlers
        deploy_btn.click(
            fn=deploy_probe,
            inputs=[probe_name, probe_category, sampling_rate, filter_expression, output_format],
            outputs=[probe_logs]
        )
        
        tcp_template_btn.click(
            fn=lambda: deploy_template("TCP Flow Monitor"),
            outputs=[probe_name, probe_category, sampling_rate, filter_expression, output_format]
        )
        
        cpu_template_btn.click(
            fn=lambda: deploy_template("CPU Profiler"),
            outputs=[probe_name, probe_category, sampling_rate, filter_expression, output_format]
        )
        
        memory_template_btn.click(
            fn=lambda: deploy_template("Memory Tracker"),
            outputs=[probe_name, probe_category, sampling_rate, filter_expression, output_format]
        )
    
    return tab

def get_available_probes():
    """Get list of available probes for deployment"""
    return [
        ["TCP Flow Monitor", "Network", "v1.2.0", "Available"],
        ["CPU Profiler", "Performance", "v1.1.0", "Available"],
        ["Memory Tracker", "Memory", "v1.0.0", "Available"],
        ["HTTP Analyzer", "Network", "v0.9.0", "Beta"],
        ["File System Monitor", "Security", "v1.0.0", "Available"],
        ["Process Tracker", "Security", "v0.8.0", "Beta"],
        ["Network Security", "Security", "v1.1.0", "Available"],
        ["Disk I/O Monitor", "Performance", "v0.7.0", "Alpha"]
    ]

def get_deployed_probes():
    """Get list of currently deployed probes"""
    return [
        ["tcp-flow-monitor", "🟢 Running", "2h 15m", 12847, 0.8, "45MB"],
        ["cpu-profiler", "🟢 Running", "1h 43m", 8901, 1.2, "32MB"],
        ["memory-tracker", "🟢 Running", "0h 55m", 5634, 0.5, "28MB"],
        ["network-security", "🟡 Warning", "3h 22m", 1205, 0.3, "18MB"],
        ["file-monitor", "🟢 Running", "0h 12m", 892, 0.4, "22MB"]
    ]

def get_sample_probe_logs():
    """Get sample probe logs"""
    return """[INFO] 2024-01-20 15:30:45 - tcp-flow-monitor: Probe started successfully
[INFO] 2024-01-20 15:30:45 - tcp-flow-monitor: Attached to TCP tracepoints
[DATA] 2024-01-20 15:30:46 - tcp-flow-monitor: New connection 192.168.1.100:45678 -> 93.184.216.34:80
[INFO] 2024-01-20 15:30:50 - cpu-profiler: Probe started successfully
[INFO] 2024-01-20 15:30:50 - cpu-profiler: Attached to scheduler tracepoints
[DATA] 2024-01-20 15:30:51 - cpu-profiler: High CPU usage detected: nginx (PID: 1234) - 85%
[INFO] 2024-01-20 15:31:02 - memory-tracker: Probe started successfully
[INFO] 2024-01-20 15:31:02 - memory-tracker: Attached to memory allocation tracepoints
[DATA] 2024-01-20 15:31:03 - memory-tracker: Large allocation detected: python (PID: 5678) - 512MB
[WARN] 2024-01-20 15:31:15 - network-security: Suspicious connection pattern detected
[DATA] 2024-01-20 15:31:16 - tcp-flow-monitor: Connection closed 192.168.1.100:45679 -> 8.8.8.8:53
[INFO] 2024-01-20 15:31:20 - file-monitor: Probe started successfully
[DATA] 2024-01-20 15:31:25 - file-monitor: Sensitive file access: /etc/shadow (PID: 9012)"""
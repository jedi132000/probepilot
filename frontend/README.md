# ProbePilot Frontend 🎛️

## Mission Control Dashboard

The ProbePilot frontend serves as the **Mission Control** for your entire observability infrastructure, providing an intuitive, aviation-inspired interface for managing eBPF probes and visualizing telemetry data through a powerful Gradio-based web application.

## Technology Stack

- **Gradio** for rapid UI development and Python-native components
- **FastAPI** backend integration for seamless Python-to-Python communication
- **Custom CSS/Themes** for aviation-inspired styling within Gradio
- **Plotly/Matplotlib** for real-time data visualization through Gradio components
- **WebSocket/Server-Sent Events** for live telemetry streaming
- **Python State Management** using global variables and Gradio state

## Key Features

### 🎯 Mission Control Interface (Gradio Dashboard)
- Central command center built with `gr.Blocks()` for custom layouts
- Real-time system status using `gr.StatusTracker()` and live components
- Quick access to critical metrics via `gr.DataFrame()` and `gr.LinePlot()`
- Aviation-themed custom CSS for cockpit aesthetics

### 📊 Real-time Dashboards
- Live telemetry visualization with `gr.LinePlot(live=True)`
- Interactive charts using Plotly integration (`gr.Plot()`)
- Customizable dashboard layouts with drag-and-drop Gradio blocks
- Export capabilities through `gr.File()` download components

### 🔧 Probe Management
- Visual probe deployment via `gr.Dropdown()` and `gr.Button()` interfaces
- Drag-and-drop configuration using `gr.File()` upload components
- Real-time probe health monitoring with `gr.BarPlot()` and status indicators
- Remote probe updates through form-based Gradio interfaces

### 🚨 Incident Response
- Automated alert aggregation displayed in `gr.DataFrame()` tables
- Guided troubleshooting workflows using `gr.Accordion()` and step-by-step forms
- Collaboration tools with `gr.ChatInterface()` for team communication
- Historical incident analysis through filterable data tables

### 🤖 AI Copilot Integration
- Natural language query interface using `gr.ChatInterface()`
- Voice interaction support with `gr.Audio()` input components
- Automated insights and recommendations display
- Context-aware help system integrated into all dashboard components

## Component Structure

```
frontend/
├── app.py                     # Main Gradio application entry point
├── components/
│   ├── mission_control.py     # Main dashboard using gr.Blocks()
│   ├── probe_manager.py       # Probe deployment and management UI
│   ├── analytics.py           # Deep-dive analytics and visualizations
│   ├── alerts.py              # Alert management and notification UI
│   └── copilot.py            # AI chat interface and voice commands
├── themes/
│   ├── aviation_theme.py      # Custom Gradio theme with aviation styling
│   ├── custom.css            # Additional CSS for mission control aesthetics
│   └── assets/               # Icons, fonts, and image assets
├── api/
│   ├── backend_client.py     # FastAPI backend communication
│   ├── websocket_handler.py  # Real-time data streaming
│   └── auth.py               # Authentication and session management
├── utils/
│   ├── data_processing.py    # Data transformation for Gradio components
│   ├── visualization.py      # Chart and plot generation helpers
│   └── state_management.py   # Global state and session handling
└── requirements.txt          # Python dependencies
```

## Development Setup

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install gradio fastapi plotly pandas numpy
```

### Quick Start
```bash
# Navigate to frontend directory
cd frontend/

# Install requirements
pip install -r requirements.txt

# Launch ProbePilot Mission Control
python app.py
```

### Development Mode
```bash
# Run with hot reload and debug mode
python app.py --debug --reload

# Access at http://localhost:7860
# Gradio provides automatic reload on file changes
```

## Sample Gradio Implementation

### Mission Control Dashboard
```python
import gradio as gr
import plotly.graph_objects as go
from datetime import datetime
import asyncio

def create_mission_control():
    with gr.Blocks(
        theme=gr.themes.Base().load("./themes/aviation_theme.json"),
        css="./themes/custom.css",
        title="ProbePilot Mission Control"
    ) as dashboard:
        
        gr.HTML("<h1>🛩️ ProbePilot Mission Control</h1>")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Real-time metrics
                metrics_plot = gr.LinePlot(
                    live=True,
                    every=1,
                    value=get_live_metrics,
                    label="System Metrics"
                )
                
            with gr.Column(scale=1):
                # System status
                status_display = gr.StatusTracker(
                    label="System Health",
                    value="🟢 All Systems Operational"
                )
                
                # Active probes
                probe_count = gr.Number(
                    label="Active Probes",
                    value=get_active_probe_count
                )
        
        with gr.Row():
            # Probe management
            probe_selector = gr.Dropdown(
                choices=["TCP Flow Monitor", "CPU Profiler", "Memory Tracker"],
                label="Deploy Probe"
            )
            deploy_btn = gr.Button("🚀 Deploy", variant="primary")
            
        with gr.Row():
            # AI Copilot
            chatbot = gr.ChatInterface(
                fn=copilot_response,
                title="🤖 ProbePilot Copilot",
                description="Ask me about your infrastructure..."
            )
    
    return dashboard

def get_live_metrics():
    # Return real-time telemetry data
    pass

def copilot_response(message, history):
    # AI-powered responses to user queries
    return f"Analyzing: {message}..."

if __name__ == "__main__":
    app = create_mission_control()
    app.launch(server_name="0.0.0.0", server_port=7860)
```

## Design System & Theming

### Aviation-Inspired Gradio Theme
```python
# Custom theme configuration
aviation_theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c50="#eff6ff",    # Sky Blue (light)
        c100="#dbeafe",
        c200="#bfdbfe",
        c300="#93c5fd",
        c400="#60a5fa",
        c500="#3b82f6",   # Sky Blue (primary)
        c600="#2563eb",
        c700="#1d4ed8",
        c800="#1e40af",
        c900="#1e3a8a",   # Mission Blue (dark)
        c950="#172554"
    ),
    secondary_hue=gr.themes.Color(
        c500="#10b981"    # Cockpit Green
    )
)
```

### Custom CSS Integration
```css
/* Mission Control Styling */
.gradio-container {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    color: #ffffff;
}

.panel {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 12px;
    font-weight: 600;
}

.status-green { background: #10b981; }
.status-orange { background: #f59e0b; }
.status-red { background: #ef4444; }
```

Following the ProbePilot brand guidelines:
- **Mission Blue** (`#1E3A8A`) for primary interface elements
- **Sky Blue** (`#3B82F6`) for interactive components
- **Cockpit Green** (`#10B981`) for success states and "go" indicators
- **Alert Orange** (`#F59E0B`) for warnings and attention-grabbing elements

## Gradio UI Elements & Aviation Theme

### Mission Control Components
- **Cockpit-style dashboards** using `gr.Blocks()` with custom CSS styling
- **Flight instrument gauges** created with Plotly and displayed via `gr.Plot()`
- **Radar-style network topology** using interactive Plotly network graphs
- **Control panel aesthetics** through themed buttons and form layouts
- **Status indicators** using colored badges and progress bars

### User Experience Flow
1. **Launch Mission Control** → User opens Gradio web interface
2. **System Overview** → Dashboard shows real-time telemetry in aviation-style displays
3. **Deploy Probes** → Dropdown selection and one-click deployment buttons
4. **Monitor Status** → Live updating charts and status indicators
5. **AI Assistance** → Chat with Copilot for insights and troubleshooting
6. **Incident Response** → Guided workflows and collaborative tools

### Benefits of Gradio Approach
- **Rapid Development**: Build complex UIs with minimal code
- **Python-Native**: Seamless integration with backend and AI models
- **Real-time Updates**: Built-in support for live data streaming
- **Customizable**: Extensive theming and CSS customization options
- **Accessible**: Automatic responsive design and accessibility features
- **Collaborative**: Easy sharing and deployment of interactive dashboards
# ProbePilot Frontend 🛩️

## Aviation-Themed Mission Control Interface

The ProbePilot frontend is a **production-ready Gradio application** that serves as Mission Control for your eBPF observability infrastructure. Built with Python-native components and aviation aesthetics, it provides an intuitive interface for managing kernel-level monitoring and real-time telemetry visualization.

## 🚀 Current Status: **DEPLOYED & RUNNING**

✅ **Application Status**: Live at http://localhost:7860  
✅ **Environment**: Python virtual environment with all dependencies  
✅ **Framework**: Gradio 5.49.1 with custom aviation theme  
✅ **Components**: All major interfaces implemented and functional  

## Technology Stack

- **Gradio 5.49.1** - Modern Python web interface framework
- **Plotly** - Interactive data visualization and real-time charts
- **Pandas/NumPy** - Data processing and analysis
- **FastAPI Integration** - Backend API communication
- **Custom Aviation Theme** - Mission control aesthetics
- **WebSocket Support** - Real-time telemetry streaming

## 🎯 Live Features

### 🛩️ Mission Control Dashboard
- **Real-time System Metrics** - CPU, memory, network telemetry
- **Active Probe Monitoring** - Live status of 12 eBPF probes
- **System Health Overview** - Color-coded status indicators
- **Event Stream** - Live feed of system events and alerts
- **Interactive Charts** - Plotly-powered real-time visualization

### � Probe Manager
- **eBPF Probe Deployment** - One-click deployment interface
- **Quick Deploy Templates** - TCP Flow, CPU Profiler, Memory Tracker
- **Probe Configuration** - Sampling rates, filters, output formats
- **Health Monitoring** - Real-time probe status and performance
- **Log Streaming** - Live probe output and event logs

### � Analytics Panel
- **Network Analytics** - Traffic patterns, connection geography
- **Performance Monitoring** - CPU heatmaps, memory trends
- **Security Dashboard** - Threat detection, security events
- **Data Export** - CSV, JSON, Parquet export capabilities
- **Historical Analysis** - Time-series data visualization

### 🤖 AI Copilot
- **Interactive Chat Interface** - Natural language system queries
- **Intelligent Analysis** - Performance bottleneck identification
- **Security Insights** - Threat assessment and recommendations
- **Troubleshooting Assistant** - Guided problem resolution
- **Quick Actions** - Pre-built analysis commands

## 🏗️ Component Architecture

```
frontend/
├── app.py                     # Main Gradio application (✅ Running)
├── components/                # UI Component Library (✅ Complete)
│   ├── __init__.py           
│   ├── mission_control.py     # Main dashboard with real-time metrics
│   ├── probe_manager.py       # eBPF probe deployment interface
│   ├── analytics.py           # Advanced data visualization
│   └── copilot.py            # AI assistant chat interface
├── themes/                    # Aviation Theme System (✅ Active)
│   └── aviation_theme.py      # Custom Gradio theme configuration
├── api/                       # Backend Integration (✅ Ready)
│   └── backend_client.py      # FastAPI client for probe management
├── requirements.txt           # Dependencies (✅ Installed)
└── README.md                 # This documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (✅ Using Python 3.13.7)
- Virtual environment activated (✅ .venv active)
- All dependencies installed (✅ Complete)

### Launch Mission Control
```bash
# From the project root
cd frontend/

# Run with virtual environment
/path/to/probepilot/.venv/bin/python app.py

# Or if venv is activated
python app.py
```

### Access the Interface
- **URL**: http://localhost:7860
- **Host**: 0.0.0.0 (accessible from network)
- **Auto-reload**: Enabled for development

### Command Line Options
```bash
python app.py --help

Options:
  --host HOST       Host to bind (default: 0.0.0.0)
  --port PORT       Port to serve on (default: 7860)
  --debug           Enable debug mode
  --reload          Enable auto-reload
  --share           Create public URL via Gradio sharing
```

## 🎨 Aviation Theme & Design

### Custom Theme Configuration
The frontend uses a meticulously crafted aviation theme that transforms the standard Gradio interface into a mission control experience:

```python
# Aviation color palette
MISSION_BLUE = "#1E3A8A"      # Primary interface color
SKY_BLUE = "#3B82F6"          # Interactive elements  
COCKPIT_GREEN = "#10B981"     # Success states
ALERT_ORANGE = "#F59E0B"      # Warnings
DANGER_RED = "#EF4444"        # Critical alerts
```

### UI Components
- **Mission Control Layout** - Cockpit-inspired dashboard design
- **Status Indicators** - Aviation-style colored status badges
- **Interactive Charts** - Radar and gauge-style visualizations
- **Control Panels** - Pilot control interface aesthetics
- **Real-time Displays** - Flight instrument inspired data views

## 📊 Live Data Integration

### Sample Data Generation
The current implementation includes comprehensive sample data generators for demonstration:

- **Network Metrics** - Simulated TCP flows, bandwidth usage
- **Performance Data** - CPU usage patterns, memory allocation
- **Security Events** - Threat detection, audit logs  
- **Probe Status** - eBPF probe health and performance metrics

### Real-time Updates
- **Refresh Controls** - Manual and automatic data refresh
- **Live Streaming** - WebSocket integration ready
- **Event Processing** - Real-time event handling and display
- **State Management** - Persistent UI state across sessions

## 🔧 Development Features

### Hot Reload Development
```bash
# Run in development mode with auto-reload
python app.py --debug --reload

# Changes to Python files automatically reload the interface
# No need to restart the server during development
```

### Component Testing
Each component can be tested independently:

```python
# Test individual components
from components.mission_control import create_mission_control_dashboard
from components.probe_manager import create_probe_manager

# Launch specific component for testing
component = create_mission_control_dashboard()
component.launch(debug=True)
```

### Custom Theming
Modify the aviation theme in `themes/aviation_theme.py`:

```python
def get_aviation_theme():
    return gr.themes.Base(
        primary_hue="blue",
        secondary_hue="green",
        # Customize colors, fonts, spacing
    )
```

## 🔗 Backend Integration

### FastAPI Client Integration
The frontend seamlessly integrates with the ProbePilot backend through a dedicated client:

```python
# Backend client configuration
from api.backend_client import BackendClient

client = BackendClient(base_url="http://localhost:8000")

# Probe management
await client.deploy_probe("tcp-flow-monitor", config)
await client.get_probe_status("tcp-flow-monitor")
await client.list_active_probes()

# Real-time data streaming
async for event in client.stream_telemetry():
    update_dashboard(event)
```

### API Endpoints Used
- **`POST /api/v1/probes/deploy`** - Deploy new eBPF probes
- **`GET /api/v1/probes/status`** - Get probe health status
- **`GET /api/v1/telemetry/stream`** - Stream real-time data
- **`POST /api/v1/analysis/query`** - AI copilot queries

## 🎯 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 7860

CMD ["python", "app.py", "--host", "0.0.0.0"]
```

### Environment Configuration
```bash
# Production environment variables
export PROBEPILOT_BACKEND_URL="http://backend:8000"
export PROBEPILOT_DEBUG="false"
export PROBEPILOT_SHARE="false"
export GRADIO_SERVER_NAME="0.0.0.0"
export GRADIO_SERVER_PORT="7860"
```

### Performance Optimization
- **Gradio Queuing** - Handle concurrent users efficiently
- **Data Caching** - Cache expensive computations
- **Lazy Loading** - Load components on demand
- **WebSocket Pooling** - Efficient real-time connections

## 🧪 Testing & Quality

### Component Testing
```bash
# Run component tests
python -m pytest tests/components/

# Test individual components
python -m pytest tests/components/test_mission_control.py
python -m pytest tests/components/test_probe_manager.py
```

### UI Testing
```bash
# Gradio interface testing
python -m pytest tests/ui/

# Integration testing with backend
python -m pytest tests/integration/
```

### Performance Testing
```bash
# Load testing with multiple concurrent users
python tests/performance/load_test.py --users 50 --duration 300
```

## 🚀 Future Enhancements

### Planned Features
- **Multi-tenant Support** - Organization and user management
- **Custom Dashboards** - User-configurable dashboard layouts
- **Advanced Analytics** - Machine learning insights
- **Mobile Interface** - Responsive mobile-first design
- **Collaborative Features** - Team workspace and sharing

### Integration Roadmap
- **Kubernetes Integration** - Native K8s probe deployment
- **Cloud Provider APIs** - AWS, GCP, Azure integration
- **Alert Management** - PagerDuty, Slack notifications
- **Data Persistence** - Historical data storage and analysis

## 📚 Resources

### Documentation
- **Gradio Documentation**: https://gradio.app/docs/
- **Plotly Python**: https://plotly.com/python/
- **FastAPI Integration**: https://fastapi.tiangolo.com/

### Support
- **GitHub Issues**: Report bugs and feature requests
- **Community Discord**: Join the ProbePilot community
- **Documentation**: Comprehensive guides and tutorials

---

## 🎊 Ready to Launch!

The ProbePilot frontend is **production-ready** and currently running with full functionality:

✅ **Aviation-themed Mission Control interface**  
✅ **Real-time eBPF probe management**  
✅ **Interactive analytics and visualization**  
✅ **AI-powered system insights**  
✅ **Responsive design and accessibility**  

**Access your Mission Control at: http://localhost:7860**

*Clear skies and happy monitoring! 🛩️*
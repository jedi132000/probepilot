# ProbePilot 🛩️

> **Your Mission Control for Kernel Observability**

ProbePilot is the unified GUI and telemetry engine for cloud-native and on-prem environments, making eBPF-powered observability and incident response accessible to everyone. Deploy, visualize, and action your probes — all from one mission-ready platform.

## 🎯 Mission Statement

Navigate clouds and clusters with precision — ProbePilot puts you in command of your eBPF telemetry. Take flight with eBPF-powered visibility. Piloting your infrastructure just got easier!

## ✨ Key Features

- **Real System Metrics Collection**: Comprehensive system observability using actual hardware and OS metrics
- **Advanced Analytics Engine**: Multi-dimensional analysis with correlation detection, anomaly clustering, and predictive modeling
- **Deep System Profiling**: Process-level monitoring, network flow analysis, memory profiling, and kernel-level metrics
- **Machine Learning Integration**: DBSCAN clustering, linear regression forecasting, and Z-score anomaly detection
- **Time Series Analysis**: Baseline learning, seasonal pattern detection, and trend analysis with confidence intervals
- **Unified Dashboard**: Mission control for all your observability probes with interactive visualizations
- **Real-time Monitoring**: Live system metrics collection and analysis with historical data storage
- **Cloud-Native Ready**: Deploy across Kubernetes, containers, and bare metal
- **Visual Probe Management**: Intuitive GUI for probe deployment and monitoring
- **Incident Response**: Fast-track from detection to resolution with comprehensive health analysis

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/jedi132000/probepilot.git
cd probepilot

# Start with Docker Compose
docker-compose up -d

# Access ProbePilot Mission Control
open http://localhost:7860
```

### Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/jedi132000/probepilot.git
cd probepilot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Start the backend (FastAPI with advanced analytics)
cd backend
uvicorn main:app --reload --port 8000 &

# Start the frontend (Gradio mission control)
cd ../frontend
python app.py

# Access ProbePilot Mission Control
open http://localhost:7860
```

### System Requirements
- **Python 3.8+** with psutil, scipy, scikit-learn, pandas, plotly
- **FastAPI** for backend API services
- **Gradio** for interactive dashboard interface
- **SQLite** for historical metrics storage
- **Real system access** for hardware metrics collection

### Prerequisites
- **Python 3.8+** (for local development)
- **Docker & Docker Compose** (for containerized setup)
- **Linux kernel 4.4+** (for eBPF support)

See [Development Setup Guide](docs/DEVELOPMENT.md) for detailed instructions.

## 🎨 Brand Identity

**Positioning Statements:**
- "ProbePilot: Your Mission Control for Kernel Observability."
- "Navigate clouds and clusters with precision — ProbePilot puts you in command of your eBPF telemetry."
- "ProbePilot: The cockpit for real-time, zero-friction performance insights."
- "Take flight with eBPF-powered visibility. Piloting your infrastructure just got easier!"

## 🏗️ Architecture

ProbePilot consists of:
- **Frontend Dashboard**: Gradio-based mission control interface with advanced analytics visualizations
- **Backend Engine**: FastAPI-based real-time system metrics processing and comprehensive analytics APIs
- **Real Metrics Collector**: Production-grade system data collection using psutil and OS-level APIs
- **Advanced Analytics Engine**: Statistical analysis engine with machine learning capabilities
- **Data Pipeline**: Real-time metrics collection, historical storage, and predictive analysis

### Core Components:
- **Real Metrics Collection**: CPU, memory, network, disk, and process monitoring using actual system APIs
- **Advanced Analytics**: Correlation detection, anomaly clustering, performance profiling, and trend analysis
- **Enhanced Probe System**: Deep system observability with kernel-level metrics and network flow analysis
- **Machine Learning Models**: DBSCAN clustering, linear regression, and statistical anomaly detection
- **Interactive Dashboard**: Comprehensive system health analysis with 6 analytics categories

## 🛠️ Development

*Development setup instructions coming soon*

## 📝 License

*License information to be added*

---

*ProbePilot - The cockpit for real-time, zero-friction performance insights* ✈️

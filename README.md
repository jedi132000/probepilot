# ProbePilot 🛩️

> **Your Mission Control for Kernel Observability**

ProbePilot is the unified GUI and telemetry engine for cloud-native and on-prem environments, making eBPF-powered observability and incident response accessible to everyone. Deploy, visualize, and action your probes — all from one mission-ready platform.

## 🎯 Mission Statement

Navigate clouds and clusters with precision — ProbePilot puts you in command of your eBPF telemetry. Take flight with eBPF-powered visibility. Piloting your infrastructure just got easier!

## ✨ Key Features

- **Real-time Kernel Observability**: Zero-friction performance insights powered by eBPF
- **Unified Dashboard**: Mission control for all your observability probes
- **Cloud-Native Ready**: Deploy across Kubernetes, containers, and bare metal
- **Visual Probe Management**: Intuitive GUI for probe deployment and monitoring
- **Incident Response**: Fast-track from detection to resolution

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

# Start the backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload &

# Start the frontend (Gradio)
cd ../frontend
pip install -r requirements.txt
python app.py

# Access ProbePilot Mission Control
open http://localhost:7860
```

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
- **Frontend Dashboard**: React-based mission control interface
- **Backend Engine**: Go-based telemetry processing and API
- **eBPF Probes**: Kernel-level observability agents
- **Data Pipeline**: Real-time metrics and trace processing

## 🛠️ Development

*Development setup instructions coming soon*

## 📝 License

*License information to be added*

---

*ProbePilot - The cockpit for real-time, zero-friction performance insights* ✈️

# ProbePilot Development Setup 🛠️

This guide will get you up and running with ProbePilot development in minutes.

## 🎯 Quick Start

```bash
# Clone the repository
git clone https://github.com/jedi132000/probepilot.git
cd probepilot

# Set up the frontend (Gradio)
cd frontend
pip install -r requirements.txt
python app.py

# In another terminal, set up the backend (FastAPI)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Access ProbePilot at: http://localhost:7860

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (recommended: Python 3.11)
- **Node.js 18+** (for build tools and package management)
- **Linux kernel 4.4+** (for eBPF support)
- **Docker** (optional, for containerized development)
- **Git** (for version control)

### Development Tools
- **Code Editor**: VS Code (recommended) or your preferred editor
- **Terminal**: Bash, Zsh, or Fish shell
- **Package Manager**: pip, conda, or poetry for Python dependencies

## 🐍 Python Environment Setup

### Option 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### Option 2: Conda Environment
```bash
# Create conda environment
conda create -n probepilot python=3.11
conda activate probepilot

# Install pip in conda environment
conda install pip
```

### Option 3: Poetry (Advanced)
```bash
# Install poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
poetry shell
```

## 🎨 Frontend Development (Gradio)

### Setup and Run
```bash
cd frontend/

# Install dependencies
pip install -r requirements.txt

# Run in development mode with hot reload
python app.py --debug --reload

# Or use the npm script
npm run dev:frontend
```

### Development Features
- **Auto-reload**: Changes to Python files automatically refresh the interface
- **Debug mode**: Enhanced error messages and debugging information
- **Custom themes**: Aviation-themed Gradio styling
- **Live components**: Real-time data updates without page refresh

### Frontend Structure
```
frontend/
├── app.py                    # Main Gradio application
├── components/               # UI component modules
│   ├── mission_control.py    # Dashboard components
│   ├── probe_manager.py      # Probe management UI
│   ├── analytics.py          # Analytics and charts
│   └── copilot.py           # AI chat interface
├── themes/
│   ├── aviation_theme.py     # Custom Gradio theme
│   └── custom.css           # Additional styling
├── api/
│   └── backend_client.py     # FastAPI communication
└── requirements.txt          # Python dependencies
```

## ⚡ Backend Development (FastAPI)

### Setup and Run
```bash
cd backend/

# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the npm script
npm run dev:backend
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Backend Structure
```
backend/
├── main.py                   # FastAPI application entry point
├── api/
│   ├── v1/                  # API version 1 endpoints
│   │   ├── probes.py        # Probe management endpoints
│   │   ├── metrics.py       # Telemetry data endpoints
│   │   ├── system.py        # System status endpoints
│   │   └── copilot.py       # AI/ML endpoints
│   └── dependencies.py      # Shared dependencies
├── core/
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connections
│   └── security.py          # Authentication/authorization
├── models/                  # Pydantic data models
├── services/                # Business logic services
├── tests/                   # Unit and integration tests
└── requirements.txt         # Python dependencies
```

## 🔬 eBPF Probe Development

### Prerequisites for eBPF Development
```bash
# Install eBPF development tools (Ubuntu/Debian)
sudo apt update
sudo apt install -y \
    libbpf-dev \
    bpfcc-tools \
    linux-headers-$(uname -r) \
    clang \
    llvm \
    build-essential

# Install Go (for probe agents)
wget https://go.dev/dl/go1.21.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.3.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
```

### Probe Development Structure
```
probes/
├── network/
│   ├── tcp-flow/
│   │   ├── tcp_flow.c       # eBPF kernel program
│   │   ├── tcp_flow.go      # Userspace agent
│   │   └── Makefile         # Build configuration
│   └── http-latency/
├── performance/
│   ├── cpu-profiler/
│   └── memory-tracker/
└── shared/
    ├── common.h             # Shared eBPF headers
    └── helpers.h            # Utility functions
```

## 🐳 Docker Development Environment

### Quick Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in development mode
docker-compose -f docker-compose.dev.yml up

# Run specific services
docker-compose up frontend backend
```

### Docker Files Structure
```
├── docker-compose.yml        # Production configuration
├── docker-compose.dev.yml    # Development configuration
├── Dockerfile.frontend       # Gradio frontend container
├── Dockerfile.backend        # FastAPI backend container
└── Dockerfile.probes         # eBPF probe development container
```

## 🧪 Testing

### Frontend Testing
```bash
cd frontend/
pytest tests/ -v
```

### Backend Testing
```bash
cd backend/
pytest tests/ -v --cov=app
```

### Integration Testing
```bash
# Run full test suite
npm run test

# Run specific test categories
pytest tests/integration/ -v
pytest tests/unit/ -v
```

## 🔧 Development Tools and Scripts

### Useful npm Scripts
```bash
# Development
npm run dev                 # Start both frontend and backend
npm run dev:frontend        # Start only Gradio frontend
npm run dev:backend         # Start only FastAPI backend

# Testing
npm run test               # Run all tests
npm run test:frontend      # Frontend tests only
npm run test:backend       # Backend tests only

# Code Quality
npm run lint               # Lint all code
npm run lint:fix           # Auto-fix linting issues
npm run format             # Format code with Black

# Documentation
npm run docs               # Serve documentation locally
```

### Python Development Tools
```bash
# Code formatting
black .
isort .

# Linting
flake8 .
pylint app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
```

## 📊 Database Setup

### Development Database (SQLite)
```bash
# SQLite database will be created automatically
# Location: backend/probepilot.db
```

### Production Database (PostgreSQL)
```bash
# Using Docker
docker run --name probepilot-postgres \
  -e POSTGRES_PASSWORD=probepilot \
  -e POSTGRES_DB=probepilot \
  -p 5432:5432 \
  -d postgres:15

# Update backend/.env with connection string
DATABASE_URL=postgresql://postgres:probepilot@localhost:5432/probepilot
```

## 🔐 Environment Configuration

### Environment Variables
Create `.env` files in both `frontend/` and `backend/` directories:

#### Frontend (.env)
```bash
# Gradio Configuration
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_ANALYTICS_ENABLED=false

# Backend API
BACKEND_URL=http://localhost:8000
API_VERSION=v1

# Development
DEBUG=true
LOG_LEVEL=debug
```

#### Backend (.env)
```bash
# FastAPI Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
RELOAD=true

# Database
DATABASE_URL=sqlite:///./probepilot.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# eBPF Probes
PROBE_PATH=/usr/local/bin/probes
PROBE_CONFIG_PATH=./config/probes

# Logging
LOG_LEVEL=debug
LOG_FORMAT=json
```

## 🚀 Deployment

### Development Deployment
```bash
# Quick deployment with Docker
docker-compose up -d

# Manual deployment
cd frontend && python app.py &
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### Production Deployment
```bash
# Build production containers
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill process using port 7860 (Gradio)
lsof -ti:7860 | xargs kill -9

# Kill process using port 8000 (FastAPI)
lsof -ti:8000 | xargs kill -9
```

#### eBPF Permissions
```bash
# Add user to necessary groups
sudo usermod -a -G bpf $USER
sudo usermod -a -G tracing $USER

# Set capabilities for eBPF programs
sudo setcap cap_sys_admin,cap_net_admin,cap_bpf+eip /path/to/probe
```

#### Python Package Conflicts
```bash
# Clear pip cache
pip cache purge

# Reinstall packages
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Getting Help

- **Documentation**: Check `/docs` directory for detailed guides
- **Issues**: Report bugs at https://github.com/jedi132000/probepilot/issues
- **Discussions**: Ask questions at https://github.com/jedi132000/probepilot/discussions
- **Discord**: Join our development community (link in README)

## 📚 Next Steps

1. **Explore the codebase**: Start with `frontend/app.py` and `backend/main.py`
2. **Run the examples**: Try deploying sample probes
3. **Read the architecture docs**: Understand the system design
4. **Contribute**: Check CONTRIBUTING.md for guidelines
5. **Join the community**: Participate in discussions and feedback

---

*Happy coding! Welcome to the ProbePilot mission crew! 🛩️*
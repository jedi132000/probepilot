# 🔧 Real Probe Deployment Integration

## ✅ Integration Complete!

The ProbePilot frontend is now connected to the backend API for **real eBPF probe deployment**. No more mock data - actual system monitoring!

## 🚀 How to Use Real Probe Deployment

### 1. **Start the Backend Server**

```bash
# Option 1: Use the startup script
python start_backend.py

# Option 2: Manual startup
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 2. **Start the Frontend**

```bash
# In another terminal
python frontend/app.py
```

Frontend available at: http://localhost:7860

### 3. **Deploy Real Probes**

#### **Quick Templates** (Recommended)
1. Go to **🔬 Probe Manager** tab
2. Click one of the template buttons:
   - **🌐 TCP Flow Monitor** - Network connection tracking
   - **⚡ CPU Profiler** - Performance monitoring  
   - **🧠 Memory Tracker** - Memory allocation tracking

#### **Custom Deployment**
1. Fill in the probe configuration:
   - **Probe Name**: Unique identifier
   - **Category**: Network/Performance/Memory/Security
   - **Sampling Rate**: How often to collect data (Hz)
   - **Filter Expression**: What to monitor (e.g., "tcp", "port 80")
   - **Output Format**: JSON/CSV/Binary

2. Click **🚀 Deploy Selected**

## 📊 What Happens Now

### **Before (Mock Mode)**
- ❌ Fake probe status
- ❌ Static demo data  
- ❌ No real monitoring
- ❌ Config-only responses

### **After (Real Integration)**
- ✅ **Real eBPF probes** deployed to your system
- ✅ **Live telemetry data** collection
- ✅ **Actual system monitoring** at kernel level
- ✅ **Real probe lifecycle** management (start/stop/monitor)

## 🔍 Monitoring Real Probes

### **Deployed Probes Section**
Shows actual running probes with:
- **Probe Name**: Real deployed probe identifier
- **Status**: 🟢 Running / 🟡 Warning / ❌ Error
- **Uptime**: How long probe has been running
- **Events**: Number of events captured
- **CPU Usage**: Probe overhead on system
- **Memory**: Probe memory consumption

### **Real-time Updates**
- Click **🔄 Refresh List** to get latest probe status
- See actual system resource usage
- Monitor probe health and performance

## 🛠️ Troubleshooting

### **Backend Not Running**
If you see "❌ Backend Connection" errors:
```bash
# Start the backend
python start_backend.py
```

### **Permission Issues**
eBPF requires elevated permissions:
```bash
# May need sudo for some probes
sudo python start_backend.py
```

### **Port Conflicts**
If port 8000 is busy:
- Kill other processes using port 8000
- Or modify backend port in `backend/main.py`

## 🎯 Real Probe Capabilities

### **TCP Flow Monitor**
- **What it does**: Tracks network connections, bandwidth, latency
- **Use cases**: Network troubleshooting, traffic analysis
- **Data**: Connection states, packet counts, transfer rates

### **CPU Profiler**
- **What it does**: Monitors CPU usage, process scheduling
- **Use cases**: Performance optimization, bottleneck detection  
- **Data**: CPU utilization, process states, scheduling events

### **Memory Tracker**
- **What it does**: Tracks memory allocations, detects leaks
- **Use cases**: Memory optimization, leak detection
- **Data**: Allocation patterns, memory usage, leak indicators

## 🔗 Backend API Endpoints

The integration uses these real APIs:

- `GET /api/v1/probes` - List active probes
- `POST /api/v1/probes` - Deploy new probe
- `DELETE /api/v1/probes/{id}` - Stop probe
- `GET /api/v1/metrics` - Get telemetry data

## ✨ Next Steps

1. **Deploy a test probe** using the templates
2. **Monitor real data** in the Analytics tab
3. **Use AI Copilot** for intelligent analysis of real probe data
4. **Scale monitoring** by deploying multiple probes

Your ProbePilot is now a **real system observability platform** with actual eBPF monitoring capabilities! 🎉
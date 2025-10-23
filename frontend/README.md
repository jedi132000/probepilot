# ProbePilot Frontend 🎛️

## Mission Control Dashboard

The ProbePilot frontend serves as the **Mission Control** for your entire observability infrastructure, providing an intuitive, aviation-inspired interface for managing eBPF probes and visualizing telemetry data.

## Technology Stack

- **React 18+** with TypeScript for type safety
- **Tailwind CSS** for consistent, aviation-themed styling
- **Recharts/D3.js** for real-time data visualization
- **WebSocket** connections for live telemetry streaming
- **Zustand** for state management

## Key Features

### 🎯 Mission Control Interface
- Central command center for all observability operations
- Real-time system status and health indicators
- Quick access to critical metrics and alerts

### 📊 Real-time Dashboards
- Live visualization of kernel-level metrics
- Interactive charts and graphs
- Customizable dashboard layouts
- Export capabilities for reports

### 🔧 Probe Management
- Visual probe deployment interface
- Drag-and-drop probe configuration
- Real-time probe health monitoring
- Remote probe updates and management

### 🚨 Incident Response
- Automated alert aggregation
- Guided troubleshooting workflows
- Collaboration tools for team response
- Historical incident analysis

## Component Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── dashboard/          # Mission Control components
│   │   ├── probes/            # Probe management UI
│   │   ├── charts/            # Visualization components
│   │   ├── alerts/            # Alert and notification UI
│   │   └── common/            # Shared UI components
│   ├── pages/
│   │   ├── Dashboard.tsx      # Main mission control page
│   │   ├── ProbeManager.tsx   # Probe deployment interface
│   │   ├── Analytics.tsx      # Deep-dive analytics
│   │   └── Settings.tsx       # Configuration management
│   ├── hooks/                 # Custom React hooks
│   ├── services/              # API communication
│   ├── store/                 # State management
│   └── utils/                 # Helper functions
├── public/
│   ├── index.html
│   └── assets/                # Static assets
└── package.json
```

## Development Setup

*Coming Soon - Development environment setup instructions*

## Design System

Following the ProbePilot brand guidelines:
- **Mission Blue** (`#1E3A8A`) for primary actions
- **Sky Blue** (`#3B82F6`) for interactive elements  
- **Cockpit Green** (`#10B981`) for success states
- **Alert Orange** (`#F59E0B`) for warnings and alerts

## Aviation-Inspired UI Elements

- **Cockpit-style gauges** for system metrics
- **Flight path visualizations** for trace flows
- **Radar-style displays** for network topology
- **Control panel aesthetics** for probe management
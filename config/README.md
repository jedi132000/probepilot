# ProbePilot Development Configuration

This directory contains configuration files for different environments and components of ProbePilot.

## Structure

```
config/
├── README.md           # This file
├── development.yml     # Development environment settings
├── production.yml      # Production environment settings  
├── probe-configs/      # eBPF probe configurations
├── kubernetes/         # Kubernetes deployment configs
└── docker/            # Docker configurations
```

## Environment Variables

ProbePilot uses the following environment variables:

- `PROBEPILOT_ENV` - Environment (development, staging, production)
- `PROBEPILOT_PORT` - Server port (default: 8080)
- `PROBEPILOT_LOG_LEVEL` - Logging level (debug, info, warn, error)
- `PROBEPILOT_DB_URL` - Database connection string
- `PROBEPILOT_PROBE_PATH` - Path to eBPF probe binaries

## Getting Started

1. Copy configuration templates:
   ```bash
   cp config/development.yml.example config/development.yml
   ```

2. Update configuration values for your environment

3. Set required environment variables or use a `.env` file

## Configuration Files

Create environment-specific configuration files as needed:

- `development.yml` - Local development settings
- `staging.yml` - Staging environment configuration  
- `production.yml` - Production deployment settings

Each configuration file should include:
- Server settings (port, host, timeouts)
- Database configuration
- eBPF probe settings
- Logging configuration
- Security settings
"""
ProbePilot Configuration Management
Application settings and environment configuration
"""

from typing import Optional
import os

class Settings:
    """Application settings"""
    
    # API Configuration
    api_title: str = "ProbePilot API"
    api_version: str = "0.1.0"
    api_description: str = "Your Mission Control for Kernel Observability"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite:///probepilot.db"
    
    # Security
    secret_key: str = "probepilot-secret-key-change-in-production"
    
    # eBPF Configuration
    ebpf_enabled: bool = True
    max_probes: int = 10
    probe_timeout: int = 300  # seconds
    
    # Logging
    log_level: str = "INFO"
    
    # Frontend CORS
    cors_origins: list = ["http://localhost:7860", "http://127.0.0.1:7860"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings
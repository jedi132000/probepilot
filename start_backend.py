#!/usr/bin/env python3
"""
ProbePilot Backend Startup Script
Quick start script for the FastAPI backend server
"""

import os
import sys
import subprocess
from pathlib import Path

def start_backend():
    """Start the ProbePilot backend server"""
    
    print("🚀 Starting ProbePilot Backend Server...")
    print("=" * 50)
    
    # Get the backend directory
    backend_dir = Path(__file__).parent / "backend"
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        print(f"   Expected: {backend_dir}")
        return False
    
    # Check if main.py exists
    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print("❌ Backend main.py not found!")
        print(f"   Expected: {main_py}")
        return False
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    print(f"📁 Working directory: {backend_dir}")
    print("🌐 Backend will be available at: http://localhost:8000")
    print("📊 API docs at: http://localhost:8000/docs")
    print("🔄 Starting server...")
    print()
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped by user")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
        
    except FileNotFoundError:
        print("❌ uvicorn not found! Install with: pip install uvicorn")
        return False

if __name__ == "__main__":
    print("🤖 ProbePilot Backend Launcher")
    print("Press Ctrl+C to stop the server")
    print()
    
    success = start_backend()
    
    if success:
        print("✅ Backend server stopped successfully")
    else:
        print("❌ Backend server failed to start")
        sys.exit(1)
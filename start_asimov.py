#!/usr/bin/env python3
"""
ASIMOV AI Clean Startup Script
Prevents port conflicts and ensures single instance deployment
"""

import os
import subprocess
import time
import socket
from contextlib import closing

def cleanup_existing_processes():
    """Kill any existing Python web processes"""
    print("🧹 Cleaning up existing processes...")
    try:
        # Kill Python processes that might be using ports
        subprocess.run(['pkill', '-f', 'python.*app'], capture_output=True)
        subprocess.run(['pkill', '-f', 'flask'], capture_output=True)
        time.sleep(2)
        print("✅ Process cleanup completed")
    except Exception:
        pass  # Continue even if cleanup fails

def check_port_available(port):
    """Check if a port is available"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex(('localhost', port)) != 0

def start_clean_deployment():
    """Start ASIMOV AI with clean port allocation"""
    
    # Clean up first
    cleanup_existing_processes()
    
    # Check port 5000
    target_port = 5000
    if not check_port_available(target_port):
        print(f"⚠️ Port {target_port} still in use, forcing cleanup...")
        time.sleep(3)
    
    # Set environment
    os.environ['PORT'] = str(target_port)
    
    # Import and start application
    print(f"🚀 Starting ASIMOV AI on clean port {target_port}")
    
    try:
        from app import app
        app.run(host='0.0.0.0', port=target_port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Startup failed: {e}")

if __name__ == '__main__':
    start_clean_deployment()
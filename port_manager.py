#!/usr/bin/env python3
"""
ASIMOV AI Port Management & Conflict Prevention
Ensures clean application startup and prevents port conflicts
"""

import os
import sys
import socket
import subprocess
import time
import signal
from contextlib import closing

class PortManager:
    """Manages port allocation and prevents conflicts"""
    
    def __init__(self, preferred_port=5000):
        self.preferred_port = preferred_port
        self.active_processes = []
        
    def is_port_in_use(self, port):
        """Check if port is currently in use"""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return sock.connect_ex(('localhost', port)) == 0
            
    def kill_processes_on_port(self, port):
        """Kill any processes using the specified port"""
        try:
            # Find processes using the port
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'], 
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        try:
                            os.kill(int(pid), signal.SIGTERM)
                            print(f"✅ Terminated process {pid} on port {port}")
                            time.sleep(1)
                        except ProcessLookupError:
                            print(f"⚠️ Process {pid} already terminated")
                        except PermissionError:
                            print(f"⚠️ Permission denied killing process {pid}")
                            
        except FileNotFoundError:
            # lsof not available, try alternative method
            try:
                subprocess.run(['pkill', '-f', 'python.*app.py'], check=False)
                subprocess.run(['pkill', '-f', 'flask'], check=False)
                print("✅ Killed Python/Flask processes")
            except Exception as e:
                print(f"⚠️ Could not kill processes: {e}")
                
    def cleanup_all_python_processes(self):
        """Clean up all Python web server processes"""
        print("🧹 Cleaning up existing Python processes...")
        try:
            # Kill common web server processes
            subprocess.run(['pkill', '-f', 'python.*app'], check=False)
            subprocess.run(['pkill', '-f', 'flask'], check=False)
            subprocess.run(['pkill', '-f', 'gunicorn'], check=False)
            time.sleep(2)
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
            
    def get_available_port(self, start_port=5000, max_attempts=10):
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if not self.is_port_in_use(port):
                return port
        raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")
        
    def secure_port_allocation(self):
        """Securely allocate a port for the application"""
        print("🔍 Checking port availability...")
        
        # First, clean up any existing processes
        self.cleanup_all_python_processes()
        
        # Check if preferred port is available
        if self.is_port_in_use(self.preferred_port):
            print(f"⚠️ Port {self.preferred_port} is in use, cleaning up...")
            self.kill_processes_on_port(self.preferred_port)
            time.sleep(2)
            
        # Verify port is now available
        if self.is_port_in_use(self.preferred_port):
            # Find alternative port
            available_port = self.get_available_port(self.preferred_port + 1)
            print(f"⚠️ Using alternative port: {available_port}")
            return available_port
        else:
            print(f"✅ Port {self.preferred_port} is available")
            return self.preferred_port
            
    def start_application_safely(self, app_module='app'):
        """Start the ASIMOV AI application with port management"""
        try:
            # Get secure port
            port = self.secure_port_allocation()
            
            # Set environment variables
            os.environ['PORT'] = str(port)
            os.environ['FLASK_ENV'] = 'production'
            
            # Import and run the application
            print(f"🚀 Starting ASIMOV AI on port {port}")
            
            if app_module == 'app':
                from app import app
                app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
            else:
                # Dynamic import
                module = __import__(app_module)
                app = getattr(module, 'app')
                app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
                
        except Exception as e:
            print(f"❌ Application startup failed: {e}")
            sys.exit(1)

def startup_health_check():
    """Perform health checks before application startup"""
    checks = []
    
    # Check 1: Database connectivity
    try:
        import sqlite3
        conn = sqlite3.connect('audit_controls.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM controls')
        count = cursor.fetchone()[0]
        conn.close()
        checks.append(f"✅ Database: {count} controls loaded")
    except Exception as e:
        checks.append(f"❌ Database: {e}")
        
    # Check 2: Template files
    try:
        template_files = ['templates/index.html', 'templates/question.html']
        for template in template_files:
            if os.path.exists(template):
                checks.append(f"✅ Template: {template}")
            else:
                checks.append(f"❌ Template missing: {template}")
    except Exception as e:
        checks.append(f"❌ Template check failed: {e}")
        
    # Check 3: Dependencies
    try:
        import flask, openai, pandas
        checks.append("✅ Dependencies: All required packages available")
    except ImportError as e:
        checks.append(f"❌ Dependencies: {e}")
        
    return checks

if __name__ == '__main__':
    print("🔧 ASIMOV AI Startup Manager")
    print("=" * 40)
    
    # Run health checks
    health_checks = startup_health_check()
    for check in health_checks:
        print(check)
    
    # Start with port management
    manager = PortManager(5000)
    manager.start_application_safely()
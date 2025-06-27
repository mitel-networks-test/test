#!/usr/bin/env python3
"""
Simple Web Application for Three-Tier Architecture Demo
This application runs on EC2 instances in the application tier
"""

import json
import os
import socket
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import subprocess

class ThreeTierAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_main_page()
        elif parsed_path.path == '/health':
            self.serve_health_check()
        elif parsed_path.path == '/api/info':
            self.serve_instance_info()
        elif parsed_path.path == '/api/database':
            self.serve_database_info()
        elif parsed_path.path.startswith('/static/'):
            self.serve_static_files()
        else:
            self.send_error(404, "Page not found")
    
    def serve_main_page(self):
        """Serve the main application page"""
        try:
            # Get instance metadata
            instance_id = self.get_instance_metadata('instance-id')
            instance_type = self.get_instance_metadata('instance-type')
            local_ipv4 = self.get_instance_metadata('local-ipv4')
            availability_zone = self.get_instance_metadata('placement/availability-zone')
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Three-Tier Application - Application Tier</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        padding: 20px;
                    }}
                    
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    
                    .header {{
                        background: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        border-radius: 20px;
                        padding: 30px;
                        text-align: center;
                        margin-bottom: 30px;
                        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
                        border: 1px solid rgba(255, 255, 255, 0.18);
                    }}
                    
                    .header h1 {{
                        color: white;
                        font-size: 2.5rem;
                        margin-bottom: 10px;
                        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    }}
                    
                    .header p {{
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 1.1rem;
                    }}
                    
                    .info-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }}
                    
                    .info-card {{
                        background: white;
                        border-radius: 15px;
                        padding: 25px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                    }}
                    
                    .info-card h3 {{
                        color: #2c3e50;
                        margin-bottom: 15px;
                        border-bottom: 2px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    
                    .info-item {{
                        display: flex;
                        justify-content: space-between;
                        padding: 8px 0;
                        border-bottom: 1px solid #ecf0f1;
                    }}
                    
                    .info-item:last-child {{
                        border-bottom: none;
                    }}
                    
                    .label {{
                        font-weight: bold;
                        color: #34495e;
                    }}
                    
                    .value {{
                        color: #7f8c8d;
                    }}
                    
                    .api-section {{
                        background: white;
                        border-radius: 15px;
                        padding: 25px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        margin-bottom: 20px;
                    }}
                    
                    .api-button {{
                        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                        color: white;
                        border: none;
                        padding: 12px 25px;
                        border-radius: 25px;
                        cursor: pointer;
                        margin: 5px;
                        font-weight: bold;
                        transition: transform 0.3s ease;
                    }}
                    
                    .api-button:hover {{
                        transform: translateY(-2px);
                    }}
                    
                    .response-area {{
                        background: #f8f9fa;
                        border-radius: 10px;
                        padding: 20px;
                        margin-top: 15px;
                        min-height: 100px;
                        white-space: pre-wrap;
                        font-family: 'Courier New', monospace;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Application Tier - EC2 Instance</h1>
                        <p>You are connected to an EC2 instance in the application tier</p>
                    </div>
                    
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>Instance Information</h3>
                            <div class="info-item">
                                <span class="label">Instance ID:</span>
                                <span class="value">{instance_id}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Instance Type:</span>
                                <span class="value">{instance_type}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Private IP:</span>
                                <span class="value">{local_ipv4}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Availability Zone:</span>
                                <span class="value">{availability_zone}</span>
                            </div>
                        </div>
                        
                        <div class="info-card">
                            <h3>Request Information</h3>
                            <div class="info-item">
                                <span class="label">Client IP:</span>
                                <span class="value">{self.client_address[0]}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">User Agent:</span>
                                <span class="value">{self.headers.get('User-Agent', 'Unknown')[:50]}...</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Timestamp:</span>
                                <span class="value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                            </div>
                            <div class="info-item">
                                <span class="label">Load Balancer:</span>
                                <span class="value">{"Yes" if 'ELB-HealthChecker' in self.headers.get('User-Agent', '') else "Direct"}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="api-section">
                        <h3>API Endpoints</h3>
                        <p>Test the application tier APIs:</p>
                        <button class="api-button" onclick="callAPI('/api/info')">Instance Info</button>
                        <button class="api-button" onclick="callAPI('/api/database')">Database Status</button>
                        <button class="api-button" onclick="callAPI('/health')">Health Check</button>
                        <div id="api-response" class="response-area">Click a button to test API endpoints...</div>
                    </div>
                </div>
                
                <script>
                    async function callAPI(endpoint) {{
                        const responseArea = document.getElementById('api-response');
                        responseArea.textContent = 'Loading...';
                        
                        try {{
                            const response = await fetch(endpoint);
                            const data = await response.text();
                            responseArea.textContent = `Response from ${{endpoint}}:\\n\\n${{data}}`;
                        }} catch (error) {{
                            responseArea.textContent = `Error calling ${{endpoint}}:\\n\\n${{error.message}}`;
                        }}
                    }}
                    
                    // Auto-refresh every 30 seconds
                    setInterval(() => {{
                        const timestamp = document.querySelector('.value:nth-of-type(3)');
                        if (timestamp) {{
                            timestamp.textContent = new Date().toISOString().replace('T', ' ').replace('Z', ' UTC');
                        }}
                    }}, 30000);
                </script>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def serve_health_check(self):
        """Health check endpoint for ALB"""
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "instance_id": self.get_instance_metadata('instance-id'),
            "checks": {
                "disk_space": self.check_disk_space(),
                "memory": self.check_memory(),
                "database_connection": "simulated_ok"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def serve_instance_info(self):
        """API endpoint for instance information"""
        info = {
            "instance_id": self.get_instance_metadata('instance-id'),
            "instance_type": self.get_instance_metadata('instance-type'),
            "private_ip": self.get_instance_metadata('local-ipv4'),
            "public_ip": self.get_instance_metadata('public-ipv4'),
            "availability_zone": self.get_instance_metadata('placement/availability-zone'),
            "region": self.get_instance_metadata('placement/region'),
            "hostname": socket.gethostname(),
            "uptime": self.get_uptime(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(info, indent=2).encode())
    
    def serve_database_info(self):
        """API endpoint for database tier information"""
        # This would normally connect to RDS, but for demo purposes we'll simulate
        db_info = {
            "status": "connected",
            "type": "MySQL RDS",
            "multi_az": True,
            "backup_retention": "7 days",
            "engine_version": "8.0.35",
            "storage_type": "gp2",
            "allocated_storage": "20 GB",
            "connection_count": 5,
            "last_backup": datetime.now().replace(hour=2, minute=0, second=0).isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(db_info, indent=2).encode())
    
    def get_instance_metadata(self, path):
        """Get EC2 instance metadata"""
        try:
            import urllib.request
            url = f"http://169.254.169.254/latest/meta-data/{path}"
            req = urllib.request.Request(url)
            req.add_header('X-aws-ec2-metadata-token-ttl-seconds', '21600')
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.read().decode('utf-8')
        except:
            return f"mock-{path.replace('/', '-')}"
    
    def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            return f"{free // (1024**3)} GB free"
        except:
            return "unknown"
    
    def check_memory(self):
        """Check memory usage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if 'MemAvailable:' in line:
                        mem_kb = int(line.split()[1])
                        return f"{mem_kb // 1024} MB available"
            return "unknown"
        except:
            return "unknown"
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                days = int(uptime_seconds // 86400)
                hours = int((uptime_seconds % 86400) // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{days}d {hours}h {minutes}m"
        except:
            return "unknown"
    
    def log_message(self, format, *args):
        """Override to add timestamp to log messages"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def run_server(port=80):
    """Run the web server"""
    try:
        server = HTTPServer(('0.0.0.0', port), ThreeTierAppHandler)
        print(f"Three-Tier Application Server starting on port {port}")
        print(f"Instance ID: {ThreeTierAppHandler(None, None, None).get_instance_metadata('instance-id')}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down the server...")
        server.shutdown()
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    run_server(port)
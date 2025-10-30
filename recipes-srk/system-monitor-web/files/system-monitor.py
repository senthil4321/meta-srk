#!/usr/bin/env python3
"""
Lightweight System Monitor Web Server
Displays CPU, RAM, and network metrics on a web page
"""

import http.server
import socketserver
import json
import time
import os
from datetime import datetime

PORT = 8080

class SystemMonitorHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/metrics':
            self.serve_metrics()
        elif self.path == '/api/system-info':
            self.serve_system_info()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the main HTML page"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitor - BeagleBone Black</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .system-info {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .system-info h2 {
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .info-item {
            background: #f7f7f7;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .info-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .info-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-title {
            font-size: 1.2em;
            color: #667eea;
            margin-bottom: 15px;
            font-weight: bold;
        }
        .metric-value {
            font-size: 3em;
            font-weight: bold;
            color: #333;
            margin: 15px 0;
        }
        .metric-label {
            color: #999;
            font-size: 0.9em;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.8em;
            font-weight: bold;
        }
        .network-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        .network-table th,
        .network-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .network-table th {
            background: #667eea;
            color: white;
            font-weight: bold;
        }
        .network-table tr:hover {
            background: #f5f5f5;
        }
        .timestamp {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .status-ok { color: #4caf50; font-weight: bold; }
        .status-warning { color: #ff9800; font-weight: bold; }
        .status-error { color: #f44336; font-weight: bold; }
        
        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .metric-value { font-size: 2em; }
            .metrics-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ BeagleBone Black System Monitor</h1>
        
        <div class="system-info">
            <h2>System Information</h2>
            <div class="info-grid" id="system-info">
                <div class="info-item">
                    <div class="info-label">Loading...</div>
                    <div class="info-value">...</div>
                </div>
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">💻 CPU Usage</div>
                <div class="metric-value" id="cpu-value">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-bar" style="width: 0%">0%</div>
                </div>
                <div class="metric-label">Load Average: <span id="load-avg">--</span></div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🧠 Memory Usage</div>
                <div class="metric-value" id="mem-value">--</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="mem-bar" style="width: 0%">0%</div>
                </div>
                <div class="metric-label">
                    Used: <span id="mem-used">--</span> / Total: <span id="mem-total">--</span>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⏱️ System Uptime</div>
                <div class="metric-value" id="uptime-value">--</div>
                <div class="metric-label">
                    Started: <span id="boot-time">--</span>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🔥 Temperature</div>
                <div class="metric-value" id="temp-value">--</div>
                <div class="metric-label" id="temp-details">--</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⚙️ Processes</div>
                <div class="metric-value" id="proc-total">--</div>
                <div class="metric-label">
                    Running: <span id="proc-running" class="status-ok">--</span> | 
                    Sleeping: <span id="proc-sleeping">--</span> | 
                    Zombie: <span id="proc-zombie" class="status-error">--</span>
                </div>
            </div>
        </div>
        
        <div class="metric-card" id="disk-card" style="display: none;">
            <div class="metric-title">💾 Disk Usage</div>
            <div id="disk-stats"></div>
        </div>
        
        <div class="metric-card">
            <div class="metric-title">🌐 Network Interfaces</div>
            <table class="network-table" id="network-table">
                <thead>
                    <tr>
                        <th>Interface</th>
                        <th>RX Bytes</th>
                        <th>RX Packets</th>
                        <th>TX Bytes</th>
                        <th>TX Packets</th>
                        <th>Errors</th>
                    </tr>
                </thead>
                <tbody id="network-tbody">
                    <tr><td colspan="6">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        
        <div class="timestamp">
            Last updated: <span id="timestamp">--</span> | Auto-refresh every 2 seconds
        </div>
    </div>
    
    <script>
        function formatBytes(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
        }
        
        function formatUptime(seconds) {
            const days = Math.floor(seconds / 86400);
            const hours = Math.floor((seconds % 86400) / 3600);
            const mins = Math.floor((seconds % 3600) / 60);
            
            if (days > 0) return `${days}d ${hours}h`;
            if (hours > 0) return `${hours}h ${mins}m`;
            return `${mins} min`;
        }
        
        async function updateSystemInfo() {
            try {
                const response = await fetch('/api/system-info');
                const data = await response.json();
                
                const infoGrid = document.getElementById('system-info');
                infoGrid.innerHTML = `
                    <div class="info-item">
                        <div class="info-label">Hostname</div>
                        <div class="info-value">${data.hostname}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Kernel</div>
                        <div class="info-value">${data.kernel}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Architecture</div>
                        <div class="info-value">${data.architecture}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">CPU Model</div>
                        <div class="info-value">${data.cpu_model}</div>
                    </div>
                `;
            } catch (error) {
                console.error('Error fetching system info:', error);
            }
        }
        
        async function updateMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update CPU
                document.getElementById('cpu-value').textContent = data.cpu.usage.toFixed(1) + '%';
                document.getElementById('cpu-bar').style.width = data.cpu.usage + '%';
                document.getElementById('cpu-bar').textContent = data.cpu.usage.toFixed(1) + '%';
                document.getElementById('load-avg').textContent = 
                    `${data.cpu.load_1m.toFixed(2)}, ${data.cpu.load_5m.toFixed(2)}, ${data.cpu.load_15m.toFixed(2)}`;
                
                // Update Memory
                const memPercent = (data.memory.used / data.memory.total * 100).toFixed(1);
                document.getElementById('mem-value').textContent = memPercent + '%';
                document.getElementById('mem-bar').style.width = memPercent + '%';
                document.getElementById('mem-bar').textContent = memPercent + '%';
                document.getElementById('mem-used').textContent = formatBytes(data.memory.used * 1024);
                document.getElementById('mem-total').textContent = formatBytes(data.memory.total * 1024);
                
                // Update Uptime
                document.getElementById('uptime-value').textContent = formatUptime(data.uptime.uptime);
                document.getElementById('boot-time').textContent = data.uptime.boot_time;
                
                // Update Temperature
                if (data.temperature && data.temperature.status !== 'not available') {
                    const temps = Object.entries(data.temperature);
                    if (temps.length > 0) {
                        const avgTemp = temps.reduce((sum, [_, temp]) => sum + temp, 0) / temps.length;
                        document.getElementById('temp-value').textContent = avgTemp.toFixed(1) + '°C';
                        document.getElementById('temp-details').innerHTML = temps.map(([zone, temp]) => 
                            `${zone}: ${temp.toFixed(1)}°C`
                        ).join('<br>');
                    } else {
                        document.getElementById('temp-value').textContent = 'N/A';
                        document.getElementById('temp-details').textContent = 'No sensors found';
                    }
                } else {
                    document.getElementById('temp-value').textContent = 'N/A';
                    document.getElementById('temp-details').textContent = 'Not available';
                }
                
                // Update Processes
                document.getElementById('proc-total').textContent = data.processes.total;
                document.getElementById('proc-running').textContent = data.processes.running;
                document.getElementById('proc-sleeping').textContent = data.processes.sleeping;
                document.getElementById('proc-zombie').textContent = data.processes.zombie;
                
                // Update Disk
                if (data.disk && Object.keys(data.disk).length > 0) {
                    document.getElementById('disk-card').style.display = 'block';
                    const diskDiv = document.getElementById('disk-stats');
                    diskDiv.innerHTML = '';
                    
                    for (const [mount, stats] of Object.entries(data.disk)) {
                        const diskItem = document.createElement('div');
                        diskItem.style.marginBottom = '15px';
                        diskItem.innerHTML = `
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <strong>${mount}</strong>
                                <span>${stats.percent.toFixed(1)}% used</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${stats.percent}%">
                                    ${formatBytes(stats.used)} / ${formatBytes(stats.total)}
                                </div>
                            </div>
                            <div class="metric-label">${stats.filesystem} (${stats.type})</div>
                        `;
                        diskDiv.appendChild(diskItem);
                    }
                }
                
                // Update Network
                const tbody = document.getElementById('network-tbody');
                tbody.innerHTML = '';
                for (const [iface, stats] of Object.entries(data.network)) {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td><strong>${iface}</strong></td>
                        <td>${formatBytes(stats.rx_bytes)}</td>
                        <td>${stats.rx_packets.toLocaleString()}</td>
                        <td>${formatBytes(stats.tx_bytes)}</td>
                        <td>${stats.tx_packets.toLocaleString()}</td>
                        <td class="${stats.errors > 0 ? 'status-error' : 'status-ok'}">
                            ${stats.errors}
                        </td>
                    `;
                }
                
                // Update timestamp
                document.getElementById('timestamp').textContent = 
                    new Date().toLocaleString();
                
            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }
        
        // Initial load
        updateSystemInfo();
        updateMetrics();
        
        // Auto-refresh every 2 seconds
        setInterval(updateMetrics, 2000);
    </script>
</body>
</html>
"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_metrics(self):
        """Serve current system metrics as JSON"""
        metrics = {
            'cpu': self.get_cpu_stats(),
            'memory': self.get_memory_stats(),
            'network': self.get_network_stats(),
            'uptime': self.get_uptime_stats(),
            'disk': self.get_disk_stats(),
            'processes': self.get_process_stats(),
            'temperature': self.get_temperature()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(metrics).encode())
    
    def serve_system_info(self):
        """Serve static system information"""
        info = {
            'hostname': self.get_hostname(),
            'kernel': self.get_kernel_version(),
            'architecture': self.get_architecture(),
            'cpu_model': self.get_cpu_model()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'max-age=60')
        self.end_headers()
        self.wfile.write(json.dumps(info).encode())
    
    def get_cpu_stats(self):
        """Get CPU usage and load average"""
        try:
            # Read /proc/loadavg
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read().strip().split()
                load_1m = float(loadavg[0])
                load_5m = float(loadavg[1])
                load_15m = float(loadavg[2])
            
            # Calculate CPU usage from /proc/stat
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
                cpu_stats = [int(x) for x in cpu_line.split()[1:]]
                
                # Total CPU time = user + nice + system + idle + iowait + irq + softirq
                total = sum(cpu_stats[:7])
                idle = cpu_stats[3]
                
                # Store for next calculation (simple approach)
                if not hasattr(self, '_last_cpu'):
                    self._last_cpu = (total, idle)
                    cpu_usage = 0.0
                else:
                    last_total, last_idle = self._last_cpu
                    total_delta = total - last_total
                    idle_delta = idle - last_idle
                    
                    if total_delta > 0:
                        cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)
                    else:
                        cpu_usage = 0.0
                    
                    self._last_cpu = (total, idle)
            
            return {
                'usage': cpu_usage,
                'load_1m': load_1m,
                'load_5m': load_5m,
                'load_15m': load_15m
            }
        except Exception as e:
            return {'usage': 0, 'load_1m': 0, 'load_5m': 0, 'load_15m': 0}
    
    def get_memory_stats(self):
        """Get memory usage statistics"""
        try:
            mem_info = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        key = parts[0].rstrip(':')
                        value = int(parts[1])
                        mem_info[key] = value
            
            total = mem_info.get('MemTotal', 0)
            available = mem_info.get('MemAvailable', mem_info.get('MemFree', 0))
            used = total - available
            
            return {
                'total': total,
                'used': used,
                'available': available,
                'free': mem_info.get('MemFree', 0)
            }
        except Exception as e:
            return {'total': 0, 'used': 0, 'available': 0, 'free': 0}
    
    def get_network_stats(self):
        """Get network interface statistics"""
        stats = {}
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()[2:]  # Skip header
                for line in lines:
                    parts = line.split()
                    iface = parts[0].rstrip(':')
                    
                    # Skip loopback
                    if iface == 'lo':
                        continue
                    
                    stats[iface] = {
                        'rx_bytes': int(parts[1]),
                        'rx_packets': int(parts[2]),
                        'rx_errors': int(parts[3]),
                        'tx_bytes': int(parts[9]),
                        'tx_packets': int(parts[10]),
                        'tx_errors': int(parts[11]),
                        'errors': int(parts[3]) + int(parts[11])
                    }
        except Exception as e:
            pass
        
        return stats
    
    def get_uptime_stats(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
            
            boot_timestamp = time.time() - uptime_seconds
            boot_time = datetime.fromtimestamp(boot_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            return {
                'uptime': int(uptime_seconds),
                'boot_time': boot_time
            }
        except Exception as e:
            return {'uptime': 0, 'boot_time': 'Unknown'}
    
    def get_hostname(self):
        """Get system hostname"""
        try:
            with open('/etc/hostname', 'r') as f:
                return f.read().strip()
        except:
            return 'unknown'
    
    def get_kernel_version(self):
        """Get kernel version"""
        try:
            with open('/proc/version', 'r') as f:
                return f.read().split()[2]
        except:
            return 'unknown'
    
    def get_architecture(self):
        """Get system architecture"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line.lower() or 'processor' in line.lower():
                        return line.split(':')[1].strip()
            return 'ARM'
        except:
            return 'unknown'
    
    def get_cpu_model(self):
        """Get CPU model name"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line.lower():
                        return line.split(':')[1].strip()
                    elif 'Hardware' in line:
                        return line.split(':')[1].strip()
            return 'ARM Processor'
        except:
            return 'unknown'
    
    def get_disk_stats(self):
        """Get disk usage statistics"""
        stats = {}
        try:
            with open('/proc/mounts', 'r') as f:
                for line in f:
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    
                    mount_point = parts[1]
                    fs_type = parts[2]
                    
                    # Skip virtual filesystems
                    if fs_type in ['proc', 'sysfs', 'devtmpfs', 'devpts', 'tmpfs', 
                                   'cgroup', 'cgroup2', 'pstore', 'configfs', 'debugfs',
                                   'tracefs', 'securityfs', 'bpf', 'fusectl', 'mqueue']:
                        continue
                    
                    try:
                        st = os.statvfs(mount_point)
                        total = st.f_blocks * st.f_frsize
                        free = st.f_bfree * st.f_frsize
                        available = st.f_bavail * st.f_frsize
                        used = total - free
                        
                        if total > 0:  # Only include if there's actual storage
                            stats[mount_point] = {
                                'total': total,
                                'used': used,
                                'free': free,
                                'available': available,
                                'percent': (used / total * 100) if total > 0 else 0,
                                'filesystem': parts[0],
                                'type': fs_type
                            }
                    except:
                        pass
        except:
            pass
        
        return stats
    
    def get_process_stats(self):
        """Get process statistics"""
        try:
            # Count processes
            proc_count = 0
            running = 0
            sleeping = 0
            zombie = 0
            
            for pid in os.listdir('/proc'):
                if not pid.isdigit():
                    continue
                
                proc_count += 1
                try:
                    with open(f'/proc/{pid}/stat', 'r') as f:
                        stat = f.read().split()
                        state = stat[2] if len(stat) > 2 else '?'
                        
                        if state == 'R':
                            running += 1
                        elif state == 'S':
                            sleeping += 1
                        elif state == 'Z':
                            zombie += 1
                except:
                    pass
            
            return {
                'total': proc_count,
                'running': running,
                'sleeping': sleeping,
                'zombie': zombie
            }
        except:
            return {'total': 0, 'running': 0, 'sleeping': 0, 'zombie': 0}
    
    def get_temperature(self):
        """Get CPU/SoC temperature if available"""
        temps = {}
        try:
            # Try thermal zones
            thermal_dir = '/sys/class/thermal'
            if os.path.exists(thermal_dir):
                for zone in os.listdir(thermal_dir):
                    if zone.startswith('thermal_zone'):
                        try:
                            with open(f'{thermal_dir}/{zone}/temp', 'r') as f:
                                temp = int(f.read().strip()) / 1000.0  # Convert from millidegrees
                            
                            # Get zone type/name
                            try:
                                with open(f'{thermal_dir}/{zone}/type', 'r') as f:
                                    zone_type = f.read().strip()
                            except:
                                zone_type = zone
                            
                            temps[zone_type] = temp
                        except:
                            pass
            
            # Try hwmon
            hwmon_dir = '/sys/class/hwmon'
            if os.path.exists(hwmon_dir):
                for hwmon in os.listdir(hwmon_dir):
                    hwmon_path = os.path.join(hwmon_dir, hwmon)
                    try:
                        # Get hwmon name
                        with open(f'{hwmon_path}/name', 'r') as f:
                            hwmon_name = f.read().strip()
                        
                        # Look for temp inputs
                        for temp_file in os.listdir(hwmon_path):
                            if temp_file.startswith('temp') and temp_file.endswith('_input'):
                                with open(f'{hwmon_path}/{temp_file}', 'r') as f:
                                    temp = int(f.read().strip()) / 1000.0
                                
                                # Try to get label
                                label_file = temp_file.replace('_input', '_label')
                                try:
                                    with open(f'{hwmon_path}/{label_file}', 'r') as f:
                                        label = f.read().strip()
                                except:
                                    label = f'{hwmon_name}_{temp_file}'
                                
                                temps[label] = temp
                    except:
                        pass
        except:
            pass
        
        return temps if temps else {'status': 'not available'}
    
    def log_message(self, format, *args):
        """Override to reduce console spam"""
        pass


def main():
    """Start the web server"""
    print(f"Starting System Monitor Web Server on port {PORT}")
    print(f"Access at: http://<device-ip>:{PORT}")
    
    with socketserver.TCPServer(("", PORT), SystemMonitorHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()


if __name__ == "__main__":
    main()

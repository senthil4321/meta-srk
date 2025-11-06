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
        elif self.path == '/api/leds':
            self.serve_led_status()
        elif self.path == '/api/ipsec':
            self.serve_ipsec_status()
        elif self.path == '/api/rtc':
            self.serve_rtc_status()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path.startswith('/api/led/'):
            self.control_led()
        elif self.path.startswith('/api/rtc/'):
            self.control_rtc()
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
        
        .led-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .led-button {
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .led-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        .led-button:active {
            transform: translateY(0);
        }
        .led-on {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
            color: white;
        }
        .led-off {
            background: linear-gradient(135deg, #ccc 0%, #999 100%);
            color: #333;
        }
        .rtc-button {
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .rtc-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        .rtc-button:active {
            transform: translateY(0);
        }
        .rtc-status-item {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            background: #f7f7f7;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .rtc-status-label {
            font-weight: bold;
            color: #666;
        }
        .rtc-status-value {
            color: #333;
            font-family: monospace;
        }
        .rtc-status-ok {
            color: #4caf50;
            font-weight: bold;
        }
        .rtc-status-warn {
            color: #ff9800;
            font-weight: bold;
        }
        .rtc-status-error {
            color: #f44336;
            font-weight: bold;
        }
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 400px;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            cursor: pointer;
        }
        .notification.success {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
        }
        .notification.warning {
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        }
        .notification.error {
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }
        .notification-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .notification-message {
            font-size: 0.95em;
            opacity: 0.95;
        }
        .notification-close {
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 1.5em;
            font-weight: bold;
            cursor: pointer;
            opacity: 0.7;
        }
        .notification-close:hover {
            opacity: 1;
        }
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
        .led-unavailable {
            background: #f0f0f0;
            color: #999;
            cursor: not-allowed;
        }
        .led-label {
            font-size: 0.9em;
            margin-top: 5px;
            opacity: 0.8;
        }
        
        .ipsec-tunnel {
            background: #f7f7f7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }
        .ipsec-tunnel.active {
            border-left-color: #4caf50;
            background: #f0f8f0;
        }
        .ipsec-tunnel.inactive {
            border-left-color: #f44336;
            background: #fff0f0;
        }
        .ipsec-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .ipsec-name {
            font-weight: bold;
            font-size: 1.1em;
        }
        .ipsec-state {
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .ipsec-state.established {
            background: #4caf50;
            color: white;
        }
        .ipsec-state.connecting {
            background: #ff9800;
            color: white;
        }
        .ipsec-state.down {
            background: #f44336;
            color: white;
        }
        .ipsec-detail {
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 10px;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .ipsec-detail-label {
            font-weight: bold;
            color: #666;
        }
        .ipsec-detail-value {
            color: #333;
        }
        .ipsec-stats {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
        }
        .ipsec-stat {
            text-align: center;
        }
        .ipsec-stat-label {
            font-size: 0.8em;
            color: #666;
        }
        .ipsec-stat-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }
        
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
            <div class="metric-title">💡 LED Control</div>
            <div class="led-controls" id="led-controls">
                <button class="led-button led-off" id="led-0" onclick="toggleLED(0)">
                    <div>LED 0</div>
                    <div class="led-label">USR0</div>
                </button>
                <button class="led-button led-off" id="led-1" onclick="toggleLED(1)">
                    <div>LED 1</div>
                    <div class="led-label">USR1</div>
                </button>
                <button class="led-button led-off" id="led-2" onclick="toggleLED(2)">
                    <div>LED 2</div>
                    <div class="led-label">USR2</div>
                </button>
                <button class="led-button led-off" id="led-3" onclick="toggleLED(3)">
                    <div>LED 3</div>
                    <div class="led-label">USR3</div>
                </button>
            </div>
        </div>
        
        <div class="metric-card" id="ipsec-card">
            <div class="metric-title">🔒 IPsec Tunnel Status</div>
            <div id="ipsec-status">
                <div class="metric-label">Loading...</div>
            </div>
        </div>
        
        <div class="metric-card" id="rtc-card">
            <div class="metric-title">⏰ RTC Power Management</div>
            <div id="rtc-status">
                <div class="metric-label">Loading...</div>
            </div>
            <div class="rtc-controls" style="margin-top: 15px;">
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px;">
                    <button onclick="syncRTC()" class="rtc-button">
                        🔄 Sync RTC
                    </button>
                    <button onclick="testRTC()" class="rtc-button">
                        🧪 Run Tests
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <input type="number" id="alarm-duration" value="60" min="10" max="3600" 
                           placeholder="Duration (seconds)" style="padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                    <button onclick="setAlarm()" class="rtc-button">
                        ⏰ Set Alarm
                    </button>
                </div>
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <select id="suspend-mode" style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; background: white;">
                        <option value="freeze">Freeze (S2Idle - Lightest sleep, fastest resume)</option>
                        <option value="standby">Standby (Medium power savings)</option>
                        <option value="mem" selected>Suspend-to-RAM (Deepest sleep, max power savings)</option>
                    </select>
                    <input type="number" id="suspend-duration" value="30" min="10" max="600" 
                           placeholder="Suspend duration (sec)" style="padding: 10px; border-radius: 5px; border: 1px solid #ddd;">
                    <button onclick="suspendSystem()" class="rtc-button" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        💤 Suspend
                    </button>
                </div>
                <div style="margin-top: 10px;">
                    <button onclick="clearAlarm()" class="rtc-button" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                        🗑️ Clear Alarm
                    </button>
                </div>
            </div>
            <div id="rtc-output" style="margin-top: 15px; padding: 10px; background: #f7f7f7; border-radius: 5px; display: none; max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9em; white-space: pre-wrap;"></div>
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
        
        <div class="system-info">
            <h2>System Information</h2>
            <div class="info-grid" id="system-info">
                <div class="info-item">
                    <div class="info-label">Loading...</div>
                    <div class="info-value">...</div>
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            Last updated: <span id="timestamp">--</span> | Auto-refresh every 2 seconds
        </div>
    </div>
    
    <script>
        let notificationTimeout = null;
        
        function showNotification(title, message, type = 'info', duration = 5000) {
            // Remove any existing notification
            const existingNotif = document.querySelector('.notification');
            if (existingNotif) {
                existingNotif.remove();
            }
            
            // Clear existing timeout
            if (notificationTimeout) {
                clearTimeout(notificationTimeout);
            }
            
            // Create notification element
            const notif = document.createElement('div');
            notif.className = 'notification ' + type;
            notif.innerHTML = `
                <span class="notification-close" onclick="this.parentElement.remove()">&times;</span>
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            `;
            
            // Add to page
            document.body.appendChild(notif);
            
            // Auto-remove after duration
            notificationTimeout = setTimeout(() => {
                notif.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notif.remove(), 300);
            }, duration);
            
            // Remove on click
            notif.addEventListener('click', () => {
                notif.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => notif.remove(), 300);
            });
        }
        
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
        
        async function toggleLED(ledNum) {
            try {
                const response = await fetch(`/api/led/${ledNum}/toggle`, {
                    method: 'POST'
                });
                
                if (response.ok) {
                    const data = await response.json();
                    updateLEDButton(ledNum, data.state);
                } else {
                    console.error('Failed to toggle LED', ledNum);
                }
            } catch (error) {
                console.error('Error toggling LED:', error);
            }
        }
        
        function updateLEDButton(ledNum, state) {
            const button = document.getElementById(`led-${ledNum}`);
            if (!button) return;
            
            button.className = 'led-button';
            if (state === 1) {
                button.classList.add('led-on');
            } else {
                button.classList.add('led-off');
            }
        }
        
        async function updateLEDStatus() {
            try {
                const response = await fetch('/api/leds');
                const data = await response.json();
                
                for (let i = 0; i < 4; i++) {
                    const ledKey = `usr${i}`;
                    const button = document.getElementById(`led-${i}`);
                    
                    if (data[ledKey] && data[ledKey].available) {
                        button.disabled = false;
                        updateLEDButton(i, data[ledKey].brightness);
                    } else {
                        button.disabled = true;
                        button.className = 'led-button led-unavailable';
                    }
                }
            } catch (error) {
                console.error('Error fetching LED status:', error);
            }
        }
        
        async function updateIPsecStatus() {
            try {
                const response = await fetch('/api/ipsec');
                const data = await response.json();
                
                const ipsecDiv = document.getElementById('ipsec-status');
                
                if (!data.available) {
                    ipsecDiv.innerHTML = '<div class="metric-label">IPsec not available or not running</div>';
                    return;
                }
                
                if (data.tunnels && data.tunnels.length > 0) {
                    ipsecDiv.innerHTML = data.tunnels.map(tunnel => `
                        <div class="ipsec-tunnel ${tunnel.state === 'ESTABLISHED' ? 'active' : 'inactive'}">
                            <div class="ipsec-header">
                                <div class="ipsec-name">${tunnel.name}</div>
                                <div class="ipsec-state ${tunnel.state.toLowerCase()}">${tunnel.state}</div>
                            </div>
                            <div class="ipsec-detail">
                                <div class="ipsec-detail-label">Local:</div>
                                <div class="ipsec-detail-value">${tunnel.local_host} [${tunnel.local_id}]</div>
                                <div class="ipsec-detail-label">Remote:</div>
                                <div class="ipsec-detail-value">${tunnel.remote_host} [${tunnel.remote_id}]</div>
                                <div class="ipsec-detail-label">Encryption:</div>
                                <div class="ipsec-detail-value">${tunnel.encryption || 'N/A'}</div>
                                <div class="ipsec-detail-label">Established:</div>
                                <div class="ipsec-detail-value">${tunnel.established || 'N/A'}</div>
                            </div>
                            ${tunnel.child_sas && tunnel.child_sas.length > 0 ? `
                                <div class="ipsec-stats">
                                    <div class="ipsec-stat">
                                        <div class="ipsec-stat-label">Bytes In</div>
                                        <div class="ipsec-stat-value">${formatBytes(tunnel.child_sas[0].bytes_in || 0)}</div>
                                    </div>
                                    <div class="ipsec-stat">
                                        <div class="ipsec-stat-label">Bytes Out</div>
                                        <div class="ipsec-stat-value">${formatBytes(tunnel.child_sas[0].bytes_out || 0)}</div>
                                    </div>
                                    <div class="ipsec-stat">
                                        <div class="ipsec-stat-label">Packets In</div>
                                        <div class="ipsec-stat-value">${(tunnel.child_sas[0].packets_in || 0).toLocaleString()}</div>
                                    </div>
                                    <div class="ipsec-stat">
                                        <div class="ipsec-stat-label">Packets Out</div>
                                        <div class="ipsec-stat-value">${(tunnel.child_sas[0].packets_out || 0).toLocaleString()}</div>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    `).join('');
                } else {
                    ipsecDiv.innerHTML = '<div class="metric-label">No active tunnels</div>';
                }
            } catch (error) {
                console.error('Error fetching IPsec status:', error);
                document.getElementById('ipsec-status').innerHTML = 
                    '<div class="metric-label">Error loading IPsec status</div>';
            }
        }
        
        async function updateRTCStatus() {
            try {
                const response = await fetch('/api/rtc');
                const data = await response.json();
                
                const rtcDiv = document.getElementById('rtc-status');
                
                if (!data.available) {
                    rtcDiv.innerHTML = '<div class="metric-label">RTC not available</div>';
                    return;
                }
                
                // Check for alarm state change (from set to not set = alarm fired)
                if (window.rtcAlarmWasSet && !data.alarm_set) {
                    showNotification('RTC Alarm Triggered!', 'The RTC alarm has fired. System may have resumed from suspend.');
                }
                window.rtcAlarmWasSet = data.alarm_set;
                
                const suspendSupport = [];
                if (data.suspend_support.mem) suspendSupport.push('Suspend-to-RAM');
                if (data.suspend_support.freeze) suspendSupport.push('S2Idle');
                if (data.suspend_support.standby) suspendSupport.push('Standby');
                
                // Update suspend mode dropdown
                updateSuspendModeDropdown(data.suspend_support);
                
                rtcDiv.innerHTML = `
                    <div class="rtc-status-item">
                        <span class="rtc-status-label">System Time:</span>
                        <span class="rtc-status-value">${data.system_time}</span>
                    </div>
                    <div class="rtc-status-item">
                        <span class="rtc-status-label">RTC Time:</span>
                        <span class="rtc-status-value">${data.rtc_time || 'N/A'}</span>
                    </div>
                    <div class="rtc-status-item">
                        <span class="rtc-status-label">Alarm Status:</span>
                        <span class="rtc-status-value ${data.alarm_set ? 'rtc-status-warn' : 'rtc-status-ok'}">
                            ${data.alarm_set ? 'SET (' + data.alarm_time + ')' : 'Not Set'}
                        </span>
                    </div>
                    <div class="rtc-status-item">
                        <span class="rtc-status-label">Suspend Support:</span>
                        <span class="rtc-status-value ${suspendSupport.length > 0 ? 'rtc-status-ok' : 'rtc-status-error'}">
                            ${suspendSupport.length > 0 ? suspendSupport.join(', ') : 'None'}
                        </span>
                    </div>
                    <div class="rtc-status-item">
                        <span class="rtc-status-label">PM Firmware:</span>
                        <span class="rtc-status-value ${data.pm_firmware ? 'rtc-status-ok' : 'rtc-status-warn'}">
                            ${data.pm_firmware ? 'Ready' : 'Not Loaded'}
                        </span>
                    </div>
                `;
            } catch (error) {
                console.error('Error fetching RTC status:', error);
                document.getElementById('rtc-status').innerHTML = 
                    '<div class="metric-label">Error loading RTC status</div>';
            }
        }
        
        function updateSuspendModeDropdown(suspendSupport) {
            const dropdown = document.getElementById('suspend-mode');
            if (!dropdown) return;
            
            // Clear existing options
            dropdown.innerHTML = '';
            
            // Add options based on available modes
            const modeDescriptions = {
                'freeze': 'Freeze (S2Idle - Lightest sleep, fastest resume)',
                'standby': 'Standby (Medium power savings)',
                'mem': 'Suspend-to-RAM (Deepest sleep, max power savings)'
            };
            
            const modeOrder = ['freeze', 'standby', 'mem'];
            let hasOptions = false;
            
            for (const mode of modeOrder) {
                if (suspendSupport[mode]) {
                    const option = document.createElement('option');
                    option.value = mode;
                    option.textContent = modeDescriptions[mode];
                    // Select 'mem' by default if available, otherwise the first option
                    if (mode === 'mem' || !hasOptions) {
                        option.selected = true;
                    }
                    dropdown.appendChild(option);
                    hasOptions = true;
                }
            }
            
            // Disable suspend button if no modes available
            const suspendButton = dropdown.parentElement.querySelector('button[onclick="suspendSystem()"]');
            if (suspendButton) {
                suspendButton.disabled = !hasOptions;
                if (!hasOptions) {
                    dropdown.innerHTML = '<option>No suspend modes available</option>';
                }
            }
        }
        
        async function syncRTC() {
            const outputDiv = document.getElementById('rtc-output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Syncing RTC...';
            
            try {
                const response = await fetch('/api/rtc/sync', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    outputDiv.textContent = '[OK] ' + data.message + '\\n' + (data.output || '');
                    outputDiv.style.color = '#4caf50';
                    setTimeout(() => updateRTCStatus(), 1000);
                } else {
                    outputDiv.textContent = '[ERROR] ' + data.message + '\\n' + (data.error || '');
                    outputDiv.style.color = '#f44336';
                }
            } catch (error) {
                outputDiv.textContent = '[ERROR] Error: ' + error.message;
                outputDiv.style.color = '#f44336';
            }
        }
        
        async function testRTC() {
            const outputDiv = document.getElementById('rtc-output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Running RTC tests...\\nThis may take up to 30 seconds...';
            
            try {
                const response = await fetch('/api/rtc/test', {
                    method: 'POST'
                });
                const data = await response.json();
                
                outputDiv.textContent = data.output || data.error || 'Test completed';
                outputDiv.style.color = data.status === 'success' ? '#333' : '#f44336';
            } catch (error) {
                outputDiv.textContent = '[ERROR] Error: ' + error.message;
                outputDiv.style.color = '#f44336';
            }
        }
        
        async function setAlarm() {
            const duration = document.getElementById('alarm-duration').value;
            const outputDiv = document.getElementById('rtc-output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Setting alarm for ' + duration + ' seconds...';
            
            try {
                const response = await fetch('/api/rtc/alarm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: parseInt(duration) })
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    outputDiv.textContent = '[OK] ' + data.message + '\\n' + (data.output || '');
                    outputDiv.style.color = '#4caf50';
                    setTimeout(() => updateRTCStatus(), 1000);
                } else {
                    outputDiv.textContent = '[ERROR] ' + data.message + '\\n' + (data.error || '');
                    outputDiv.style.color = '#f44336';
                }
            } catch (error) {
                outputDiv.textContent = '[ERROR] Error: ' + error.message;
                outputDiv.style.color = '#f44336';
            }
        }
        
        async function suspendSystem() {
            const duration = document.getElementById('suspend-duration').value;
            const mode = document.getElementById('suspend-mode').value;
            const modeNames = {
                'freeze': 'Freeze (S2Idle)',
                'standby': 'Standby',
                'mem': 'Suspend-to-RAM'
            };
            
            if (!confirm('System will enter ' + modeNames[mode] + ' for ' + duration + ' seconds. Continue?')) {
                return;
            }
            
            const outputDiv = document.getElementById('rtc-output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Suspending system (' + modeNames[mode] + ') for ' + duration + ' seconds...\\nThe page will stop updating until system resumes.';
            outputDiv.style.color = '#ff9800';
            
            try {
                const response = await fetch('/api/rtc/suspend', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ duration: parseInt(duration), mode: mode })
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    outputDiv.textContent = '[SUSPEND] ' + data.message + '\\n\\nWaiting for system to resume...';
                    outputDiv.style.color = '#ff9800';
                } else {
                    outputDiv.textContent = '[ERROR] ' + data.message;
                    outputDiv.style.color = '#f44336';
                }
            } catch (error) {
                outputDiv.textContent = '[ERROR] Error: ' + error.message;
                outputDiv.style.color = '#f44336';
            }
        }
        
        async function clearAlarm() {
            const outputDiv = document.getElementById('rtc-output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Clearing RTC alarm...';
            
            try {
                const response = await fetch('/api/rtc/clear', {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.status === 'success') {
                    outputDiv.textContent = '[OK] ' + data.message;
                    outputDiv.style.color = '#4caf50';
                    setTimeout(() => updateRTCStatus(), 1000);
                } else {
                    outputDiv.textContent = '[ERROR] ' + data.message;
                    outputDiv.style.color = '#f44336';
                }
            } catch (error) {
                outputDiv.textContent = '[ERROR] Error: ' + error.message;
                outputDiv.style.color = '#f44336';
            }
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
                        <div class="info-label">Machine</div>
                        <div class="info-value">${data.machine}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Rootfs Image</div>
                        <div class="info-value">${data.rootfs_image || 'unknown'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Kernel Recipe</div>
                        <div class="info-value">${data.kernel_name || data.kernel}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">OS Release</div>
                        <div class="info-value">${data.os_release || 'Linux'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Architecture</div>
                        <div class="info-value">${data.architecture}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">CPU Model</div>
                        <div class="info-value">${data.cpu_model}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Kernel Build Time</div>
                        <div class="info-value">${data.kernel_build_time || 'unknown'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Rootfs Build Time</div>
                        <div class="info-value">${data.rootfs_build_time || data.build_time || 'unknown'}</div>
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
        updateLEDStatus();
        updateIPsecStatus();
        updateRTCStatus();
        
        // Auto-refresh every 2 seconds
        setInterval(updateMetrics, 2000);
        // Update LED status every 5 seconds
        setInterval(updateLEDStatus, 5000);
        // Update IPsec status every 5 seconds
        setInterval(updateIPsecStatus, 5000);
        // Update RTC status every 5 seconds
        setInterval(updateRTCStatus, 5000);
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
            'kernel_name': self.get_kernel_name(),
            'kernel_build_time': self.get_kernel_build_time(),
            'architecture': self.get_architecture(),
            'cpu_model': self.get_cpu_model(),
            'machine': self.get_machine_name(),
            'build_time': self.get_build_time(),
            'rootfs_build_time': self.get_rootfs_build_time(),
            'os_release': self.get_os_release(),
            'rootfs_image': self.get_rootfs_image()
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
    
    def get_build_info(self):
        """Read build information from /etc/build-info"""
        info = {}
        try:
            if os.path.exists('/etc/build-info'):
                with open('/etc/build-info', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            info[key] = value.strip()
        except:
            pass
        return info
    
    def get_kernel_name(self):
        """Get kernel recipe name from build-info or /proc/version"""
        # Try to get from build-info first
        build_info = self.get_build_info()
        if 'KERNEL_RECIPE' in build_info:
            return build_info['KERNEL_RECIPE']
        
        # Fallback to /proc/version
        try:
            with open('/proc/version', 'r') as f:
                version_str = f.read()
                # Extract kernel name (e.g., "Linux version 6.6.75-yocto-standard")
                parts = version_str.split()
                if len(parts) >= 3:
                    return parts[2]  # Returns something like "6.6.75-yocto-standard"
            return 'unknown'
        except:
            return 'unknown'
    
    def get_machine_name(self):
        """Get machine name from build-info or device tree"""
        # Try to get from build-info first
        build_info = self.get_build_info()
        if 'MACHINE' in build_info:
            return build_info['MACHINE']
        
        # Fallback to device tree model
        try:
            # Try to get from device tree model
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read().strip('\x00').strip()
                if model:
                    return model
        except:
            pass
        
        # Fallback to machine info from /etc/os-release or other sources
        try:
            if os.path.exists('/etc/machine-info'):
                with open('/etc/machine-info', 'r') as f:
                    for line in f:
                        if 'MACHINE=' in line:
                            return line.split('=')[1].strip().strip('"')
        except:
            pass
        
        return 'unknown'
    
    def get_kernel_build_time(self):
        """Get kernel build timestamp from build-info"""
        build_info = self.get_build_info()
        if 'KERNEL_BUILD_TIME' in build_info:
            return build_info['KERNEL_BUILD_TIME']
        
        # Fallback to kernel version string
        try:
            with open('/proc/version', 'r') as f:
                version_str = f.read()
                # Extract build time (usually after #1 and before compiler info)
                import re
                match = re.search(r'#\d+\s+[A-Z]+\s+(.+?)\s+\d{4}', version_str)
                if match:
                    return match.group(0)
                # Try simpler pattern
                match = re.search(r'#\d+\s+(.+)', version_str)
                if match:
                    build_info_str = match.group(1).split('(')[0].strip()
                    return build_info_str
        except:
            pass
        
        return 'unknown'
    
    def get_rootfs_build_time(self):
        """Get rootfs build timestamp from build-info"""
        build_info = self.get_build_info()
        if 'ROOTFS_BUILD_TIME' in build_info:
            return build_info['ROOTFS_BUILD_TIME']
        return 'unknown'
    
    def get_build_time(self):
        """Get generic build timestamp (deprecated, use get_rootfs_build_time)"""
        # For backwards compatibility
        return self.get_rootfs_build_time()
    
    def get_rootfs_image(self):
        """Get rootfs image name from build-info"""
        build_info = self.get_build_info()
        if 'ROOTFS_IMAGE' in build_info:
            return build_info['ROOTFS_IMAGE']
        return 'unknown'
    
    def get_os_release(self):
        """Get OS/Image information from /etc/os-release"""
        try:
            info = {}
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            info[key] = value.strip('"')
            
            # Return formatted string with key information
            name = info.get('NAME', 'Linux')
            version = info.get('VERSION', '')
            pretty_name = info.get('PRETTY_NAME', '')
            
            if pretty_name:
                return pretty_name
            elif version:
                return f"{name} {version}"
            else:
                return name
        except:
            return 'Linux'
    
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
    
    def serve_led_status(self):
        """Serve current LED status"""
        led_status = self.get_led_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(led_status).encode())
    
    def serve_ipsec_status(self):
        """Serve IPsec tunnel status"""
        ipsec_status = self.get_ipsec_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(ipsec_status).encode())
    
    def control_led(self):
        """Control LED via POST request"""
        try:
            # Parse URL: /api/led/<led_num>/<action>
            parts = self.path.split('/')
            if len(parts) < 5:
                self.send_error(400, "Invalid LED control path")
                return
            
            led_num = int(parts[3])
            action = parts[4]  # 'on', 'off', or 'toggle'
            
            if led_num < 0 or led_num > 3:
                self.send_error(400, "LED number must be 0-3")
                return
            
            if action not in ['on', 'off', 'toggle']:
                self.send_error(400, "Action must be 'on', 'off', or 'toggle'")
                return
            
            # Execute LED control
            success = self.set_led_state(led_num, action)
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'success',
                    'led': led_num,
                    'action': action,
                    'state': self.get_led_brightness(led_num)
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(500, "Failed to control LED")
        
        except Exception as e:
            self.send_error(500, f"Error controlling LED: {str(e)}")
    
    def get_led_status(self):
        """Get status of all LEDs"""
        leds = {}
        for i in range(4):
            led_path = f"/sys/class/leds/beaglebone:green:usr{i}"
            if os.path.exists(led_path):
                leds[f'usr{i}'] = {
                    'number': i,
                    'brightness': self.get_led_brightness(i),
                    'trigger': self.get_led_trigger(i),
                    'available': True
                }
            else:
                leds[f'usr{i}'] = {
                    'number': i,
                    'available': False
                }
        return leds
    
    def get_led_brightness(self, led_num):
        """Get LED brightness (0 or 1)"""
        try:
            with open(f"/sys/class/leds/beaglebone:green:usr{led_num}/brightness", 'r') as f:
                return int(f.read().strip())
        except:
            return 0
    
    def get_led_trigger(self, led_num):
        """Get current LED trigger"""
        try:
            with open(f"/sys/class/leds/beaglebone:green:usr{led_num}/trigger", 'r') as f:
                triggers = f.read().strip()
                # Extract current trigger (marked with [])
                import re
                match = re.search(r'\[(\w+)\]', triggers)
                return match.group(1) if match else 'unknown'
        except:
            return 'unknown'
    
    def set_led_state(self, led_num, action):
        """Set LED state (on, off, or toggle)"""
        try:
            led_path = f"/sys/class/leds/beaglebone:green:usr{led_num}"
            
            # First set trigger to 'none' for manual control
            with open(f"{led_path}/trigger", 'w') as f:
                f.write('none')
            
            # Determine new brightness
            if action == 'toggle':
                current = self.get_led_brightness(led_num)
                new_brightness = 0 if current == 1 else 1
            elif action == 'on':
                new_brightness = 1
            else:  # off
                new_brightness = 0
            
            # Set brightness
            with open(f"{led_path}/brightness", 'w') as f:
                f.write(str(new_brightness))
            
            return True
        except Exception as e:
            print(f"Error setting LED {led_num}: {e}")
            return False
    
    def get_ipsec_status(self):
        """Get IPsec tunnel status from swanctl"""
        import subprocess
        import re
        
        result = {
            'available': False,
            'tunnels': []
        }
        
        try:
            # Check if swanctl is available
            if not os.path.exists('/usr/sbin/swanctl'):
                return result
            
            # Run swanctl --list-sas
            proc = subprocess.run(
                ['/usr/sbin/swanctl', '--list-sas'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if proc.returncode != 0:
                return result
            
            result['available'] = True
            
            # Parse swanctl output
            output = proc.stdout
            
            # Pattern to match tunnel info
            # Example: bbb-ipsec: #1, ESTABLISHED, IKEv2, ...
            tunnel_pattern = r'^(\S+):\s+#(\d+),\s+(\w+),\s+IKEv([12])'
            local_pattern = r"^\s+local\s+'?([^']+?)'?\s+@\s+(\S+)\[(\d+)\]"
            remote_pattern = r"^\s+remote\s+'?([^']+?)'?\s+@\s+(\S+)\[(\d+)\]"
            encryption_pattern = r'^\s+(\S+/\S+/\S+/\S+)'
            established_pattern = r'established\s+(.+?)\s+ago'
            child_pattern = r'^\s+(\S+):\s+#(\d+),.*reqid\s+(\d+),\s+(\w+),\s+(\w+),\s+ESP'
            bytes_pattern = r'^\s+in\s+(\w+),\s+(\d+)\s+bytes,\s+(\d+)\s+packets'
            bytes_out_pattern = r'^\s+out\s+(\w+),\s+(\d+)\s+bytes,\s+(\d+)\s+packets'
            
            current_tunnel = None
            current_child = None
            
            for line in output.split('\n'):
                # New tunnel
                tunnel_match = re.match(tunnel_pattern, line)
                if tunnel_match:
                    if current_tunnel:
                        result['tunnels'].append(current_tunnel)
                    
                    current_tunnel = {
                        'name': tunnel_match.group(1),
                        'unique_id': tunnel_match.group(2),
                        'state': tunnel_match.group(3),
                        'ikev': tunnel_match.group(4),
                        'local_id': '',
                        'local_host': '',
                        'local_port': '',
                        'remote_id': '',
                        'remote_host': '',
                        'remote_port': '',
                        'encryption': '',
                        'established': '',
                        'child_sas': []
                    }
                    current_child = None
                    continue
                
                if not current_tunnel:
                    continue
                
                # Local endpoint
                local_match = re.match(local_pattern, line)
                if local_match:
                    current_tunnel['local_id'] = local_match.group(1)
                    current_tunnel['local_host'] = local_match.group(2)
                    current_tunnel['local_port'] = local_match.group(3)
                    continue
                
                # Remote endpoint
                remote_match = re.match(remote_pattern, line)
                if remote_match:
                    current_tunnel['remote_id'] = remote_match.group(1)
                    current_tunnel['remote_host'] = remote_match.group(2)
                    current_tunnel['remote_port'] = remote_match.group(3)
                    continue
                
                # Encryption
                enc_match = re.match(encryption_pattern, line)
                if enc_match:
                    current_tunnel['encryption'] = enc_match.group(1)
                    continue
                
                # Established time
                est_match = re.search(established_pattern, line)
                if est_match:
                    current_tunnel['established'] = est_match.group(1) + ' ago'
                    continue
                
                # Child SA
                child_match = re.match(child_pattern, line)
                if child_match:
                    current_child = {
                        'name': child_match.group(1),
                        'unique_id': child_match.group(2),
                        'reqid': child_match.group(3),
                        'state': child_match.group(4),
                        'mode': child_match.group(5),
                        'bytes_in': 0,
                        'packets_in': 0,
                        'bytes_out': 0,
                        'packets_out': 0
                    }
                    current_tunnel['child_sas'].append(current_child)
                    continue
                
                # Bytes in
                if current_child:
                    bytes_in_match = re.match(bytes_pattern, line)
                    if bytes_in_match:
                        current_child['bytes_in'] = int(bytes_in_match.group(2))
                        current_child['packets_in'] = int(bytes_in_match.group(3))
                        continue
                    
                    # Bytes out
                    bytes_out_match = re.match(bytes_out_pattern, line)
                    if bytes_out_match:
                        current_child['bytes_out'] = int(bytes_out_match.group(2))
                        current_child['packets_out'] = int(bytes_out_match.group(3))
                        continue
            
            # Add last tunnel
            if current_tunnel:
                result['tunnels'].append(current_tunnel)
        
        except subprocess.TimeoutExpired:
            result['error'] = 'Command timeout'
        except FileNotFoundError:
            result['error'] = 'swanctl not found'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def serve_rtc_status(self):
        """Serve RTC status and power management info"""
        rtc_status = self.get_rtc_status()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(json.dumps(rtc_status).encode())
    
    def control_rtc(self):
        """Control RTC operations via POST request"""
        import subprocess
        
        try:
            # Parse URL: /api/rtc/<action>
            parts = self.path.split('/')
            if len(parts) < 4:
                self.send_error(400, "Invalid RTC control path")
                return
            
            action = parts[3]
            
            # Read POST data for parameters
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = {}
            if content_length > 0:
                import json as json_module
                post_body = self.rfile.read(content_length)
                post_data = json_module.loads(post_body.decode('utf-8'))
            
            result = {'status': 'error', 'message': 'Unknown action'}
            
            if action == 'sync':
                # Sync system time to RTC
                proc = subprocess.run(
                    ['/usr/sbin/rtc-sync.sh'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if proc.returncode == 0:
                    result = {
                        'status': 'success',
                        'message': 'RTC synchronized with system time',
                        'output': proc.stdout
                    }
                else:
                    result = {
                        'status': 'error',
                        'message': 'Failed to sync RTC',
                        'error': proc.stderr
                    }
            
            elif action == 'test':
                # Run RTC power management tests
                proc = subprocess.run(
                    ['/usr/sbin/rtc-pm-test'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                result = {
                    'status': 'success' if proc.returncode == 0 else 'error',
                    'message': 'RTC tests completed',
                    'output': proc.stdout,
                    'error': proc.stderr if proc.returncode != 0 else ''
                }
            
            elif action == 'alarm':
                # Set RTC alarm
                duration = post_data.get('duration', 60)
                proc = subprocess.run(
                    ['/usr/sbin/rtc-wakeup', str(duration)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if proc.returncode == 0:
                    result = {
                        'status': 'success',
                        'message': f'RTC alarm set for {duration} seconds',
                        'output': proc.stdout
                    }
                else:
                    result = {
                        'status': 'error',
                        'message': 'Failed to set RTC alarm',
                        'error': proc.stderr
                    }
            
            elif action == 'suspend':
                # Suspend to RAM with RTC wakeup
                duration = post_data.get('duration', 30)
                mode = post_data.get('mode', 'mem')
                
                # Validate mode
                valid_modes = ['freeze', 'standby', 'mem']
                if mode not in valid_modes:
                    result = {
                        'status': 'error',
                        'message': f'Invalid power mode: {mode}. Must be one of: {", ".join(valid_modes)}'
                    }
                else:
                    # Start suspend in background
                    subprocess.Popen(
                        ['/usr/sbin/rtc-suspend', str(duration), mode],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    mode_names = {
                        'freeze': 'Freeze (S2Idle)',
                        'standby': 'Standby',
                        'mem': 'Suspend-to-RAM'
                    }
                    
                    result = {
                        'status': 'success',
                        'message': f'System will enter {mode_names.get(mode, mode)} for {duration} seconds',
                        'duration': duration,
                        'mode': mode
                    }
            
            elif action == 'clear':
                # Clear RTC alarm
                try:
                    with open('/sys/class/rtc/rtc0/wakealarm', 'w') as f:
                        f.write('0')
                    result = {
                        'status': 'success',
                        'message': 'RTC alarm cleared'
                    }
                except Exception as e:
                    result = {
                        'status': 'error',
                        'message': f'Failed to clear alarm: {str(e)}'
                    }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        
        except Exception as e:
            self.send_error(500, f"Error controlling RTC: {str(e)}")
    
    def get_rtc_status(self):
        """Get RTC status and power management capabilities"""
        import subprocess
        
        result = {
            'available': False,
            'device': '/dev/rtc0',
            'system_time': '',
            'rtc_time': '',
            'alarm_set': False,
            'alarm_time': '',
            'suspend_support': {
                'mem': False,
                'freeze': False,
                'standby': False
            },
            'pm_firmware': False
        }
        
        try:
            # Check if RTC device exists
            if not os.path.exists('/dev/rtc0'):
                return result
            
            result['available'] = True
            
            # Get system time
            result['system_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get RTC time
            try:
                proc = subprocess.run(
                    ['hwclock', '-r'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proc.returncode == 0:
                    result['rtc_time'] = proc.stdout.strip()
            except:
                pass
            
            # Check for alarm
            try:
                with open('/sys/class/rtc/rtc0/wakealarm', 'r') as f:
                    alarm = f.read().strip()
                    if alarm and alarm != '0':
                        result['alarm_set'] = True
                        result['alarm_time'] = alarm
            except:
                pass
            
            # Check suspend support
            try:
                with open('/sys/power/state', 'r') as f:
                    states = f.read().strip().split()
                    result['suspend_support']['mem'] = 'mem' in states
                    result['suspend_support']['freeze'] = 'freeze' in states
                    result['suspend_support']['standby'] = 'standby' in states
            except:
                pass
            
            # Check PM firmware status
            pm_status_path = '/sys/kernel/debug/pm33xx/status'
            if os.path.exists(pm_status_path):
                try:
                    with open(pm_status_path, 'r') as f:
                        status = f.read()
                        result['pm_firmware'] = 'ready' in status.lower()
                except:
                    pass
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
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

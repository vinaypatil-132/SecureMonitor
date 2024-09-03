from flask import Flask, render_template, jsonify
import psutil
import socket
import subprocess
import platform
import time
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    try:
        # Network data
        network = psutil.net_io_counters()
        network_data = {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv
        }

        # Performance data
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        performance_data = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage
        }

        # Security and Authentication
        authentication = get_authentication_logs()

        # Incoming Connections
        incoming_connections = get_incoming_connections()

        # Current Network Details
        current_network = get_current_network_details()

        # Data Usage
        data_usage = {
            'total_bytes_sent': network.bytes_sent,
            'total_bytes_recv': network.bytes_recv
        }

        # Processes
        processes = get_processes()

        # System Uptime
        system_uptime = get_system_uptime()

        # Temperature Sensors
        temperature_sensors = get_temperature_sensors()

        # Disk Partitions
        disk_partitions = get_disk_partitions()

        # Battery Status
        battery_status = get_battery_status()

        # System Information
        system_info = get_system_info()

        # Combine all data
        all_data = {
            'network': network_data,
            'performance': performance_data,
            'authentication': authentication,
            'incoming_connections': incoming_connections,
            'current_network': current_network,
            'data_usage': data_usage,
            'processes': processes,
            'system_uptime': system_uptime,
            'temperature_sensors': temperature_sensors,
            'disk_partitions': disk_partitions,
            'battery_status': battery_status,
            'system_info': system_info
        }
        
        return jsonify(all_data)
    except Exception as e:
        return jsonify({'error': str(e)})

def get_authentication_logs():
    try:
        logs = subprocess.check_output(['journalctl', '-u', 'gdm'], text=True)
        return logs.splitlines()[-10:]
    except subprocess.CalledProcessError as e:
        return str(e)

def get_incoming_connections():
    try:
        connections = subprocess.check_output(['ss', '-tuln'], text=True)
        return connections.splitlines()[1:]
    except subprocess.CalledProcessError as e:
        return str(e)

def get_current_network_details():
    try:
        interfaces = psutil.net_if_addrs()
        details = {}
        for interface, addrs in interfaces.items():
            details[interface] = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    details[interface].append({
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
        return details
    except Exception as e:
        return str(e)

def get_processes():
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            # Filter for important processes (high CPU or memory usage)
            if proc.info['cpu_percent'] > 10 or proc.info['memory_info'].rss / (1024 * 1024) > 100:  # Example thresholds
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_info': proc.info['memory_info'].rss / (1024 * 1024)  # Convert to MB
                })
        return processes
    except Exception as e:
        return str(e)

def get_system_uptime():
    try:
        uptime_seconds = int(time.time() - psutil.boot_time())
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"
    except Exception as e:
        return str(e)

def get_temperature_sensors():
    try:
        temps = {}
        if hasattr(psutil, 'sensors_temperatures'):
            temperatures = psutil.sensors_temperatures()
            for name, entries in temperatures.items():
                temps[name] = [{'label': entry.label, 'temperature': entry.current} for entry in entries]
        return temps
    except Exception as e:
        return str(e)

def get_disk_partitions():
    try:
        partitions = psutil.disk_partitions()
        disk_info = []
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'fstype': partition.fstype,
                'total': usage.total / (1024 * 1024 * 1024),  # Convert to GB
                'used': usage.used / (1024 * 1024 * 1024),
                'free': usage.free / (1024 * 1024 * 1024)
            })
        return disk_info
    except Exception as e:
        return str(e)

def get_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                'percent': 'N/A',
                'plugged_in': 'N/A',
                'time_left': 'N/A'
            }
        percent = battery.percent
        plugged_in = battery.power_plugged
        if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            time_left = 'Unknown'
        else:
            hours, remainder = divmod(battery.secsleft, 3600)
            minutes, _ = divmod(remainder, 60)
            time_left = f"{hours}h {minutes}m"
        return {
            'percent': percent,
            'plugged_in': plugged_in,
            'time_left': time_left
        }
    except Exception as e:
        return {'error': str(e)}

def get_system_info():
    try:
        uname = platform.uname()
        user = os.getlogin()
        system_info = {
            'Operating System': uname.system,
            'Hostname': uname.node,
            'Architecture': uname.machine,
            'User': user,
            'Kernel Version': uname.version
        }
        return system_info
    except Exception as e:
        return {'error': str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

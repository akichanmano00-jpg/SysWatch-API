
import psutil
import platform
import socket
from datetime import datetime


def collect_system_metrics():
    """Collecte les métriques système de la machine."""

    # Informations générales
    hostname = socket.gethostname()
    timestamp = datetime.now().isoformat()
    system = platform.system()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_times = psutil.cpu_times_percent(interval=None)
    load_average = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

    # RAM
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disques
    disk_partitions = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            disk_partitions.append({
                "mountpoint": partition.mountpoint,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "usage_pct": usage.percent
            })
        except (PermissionError, OSError):
            continue

    # I/O disque
    disk_io = psutil.disk_io_counters()

    return {
        "timestamp": timestamp,
        "hostname": hostname,
        "system": system,
        "cpu_pct": cpu_percent,
        "cpu_per_core": cpu_per_core,
        "cpu_user": cpu_times.user,
        "cpu_system": cpu_times.system,
        "cpu_iowait": getattr(cpu_times, "iowait", 0),
        "load_1m": load_average[0],
        "load_5m": load_average[1],
        "load_15m": load_average[2],
        "ram_total_mb": round(memory.total / (1024 ** 2), 2),
        "ram_used_mb": round(memory.used / (1024 ** 2), 2),
        "ram_available_mb": round(memory.available / (1024 ** 2), 2),
        "ram_pct": memory.percent,
        "swap_pct": swap.percent,
        "swap_used_mb": round(swap.used / (1024 ** 2), 2),
        "disk_partitions": disk_partitions,
        "disk_read_mb": round(disk_io.read_bytes / (1024 ** 2), 2) if disk_io else 0,
        "disk_write_mb": round(disk_io.write_bytes / (1024 ** 2), 2) if disk_io else 0
    }

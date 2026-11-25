
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "database" / "syswatch.db"


def get_connection():
    """Ouvre une connexion à la base SQLite."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Crée les cinq tables nécessaires au projet."""

    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS host_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            hostname TEXT,
            cpu_pct REAL,
            load_1m REAL,
            ram_used_mb REAL,
            ram_pct REAL,
            swap_pct REAL,
            disk_read_mb_s REAL,
            disk_write_mb_s REAL
        );

        CREATE TABLE IF NOT EXISTS disk_partitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mountpoint TEXT,
            total_gb REAL,
            used_gb REAL,
            usage_pct REAL
        );

        CREATE TABLE IF NOT EXISTS process_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pid INTEGER,
            name TEXT,
            status TEXT,
            cpu_pct REAL,
            rss_mb REAL,
            num_threads INTEGER,
            open_files INTEGER
        );

        CREATE TABLE IF NOT EXISTS service_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            service_name TEXT,
            url TEXT,
            status_code INTEGER,
            response_time_ms REAL,
            is_healthy INTEGER,
            ssl_days_left INTEGER,
            error_msg TEXT
        );

        CREATE TABLE IF NOT EXISTS system_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            category TEXT,
            severity TEXT,
            resource_name TEXT,
            metric_value REAL,
            threshold_value REAL,
            description TEXT
        );
        """)


def insert_host_metrics(data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO host_metrics (
                timestamp, hostname, cpu_pct, load_1m,
                ram_used_mb, ram_pct, swap_pct,
                disk_read_mb_s, disk_write_mb_s
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["timestamp"], data["hostname"], data["cpu_pct"],
            data["load_1m"], data["ram_used_mb"], data["ram_pct"],
            data["swap_pct"], data["disk_read_mb_s"],
            data["disk_write_mb_s"]
        ))


def insert_disk_partitions(timestamp, partitions):
    with get_connection() as conn:
        for disk in partitions:
            conn.execute("""
                INSERT INTO disk_partitions (
                    timestamp, mountpoint, total_gb,
                    used_gb, usage_pct
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                timestamp, disk["mountpoint"], disk["total_gb"],
                disk["used_gb"], disk["usage_pct"]
            ))


def insert_processes(timestamp, processes):
    with get_connection() as conn:
        for process in processes:
            conn.execute("""
                INSERT INTO process_metrics (
                    timestamp, pid, name, status, cpu_pct,
                    rss_mb, num_threads, open_files
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, process["pid"], process["name"],
                process["status"], process["cpu_pct"],
                process["rss_mb"], process["num_threads"],
                process["open_files"]
            ))


def insert_service_health(result):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO service_health (
                timestamp, service_name, url, status_code,
                response_time_ms, is_healthy, ssl_days_left, error_msg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["timestamp"], result["service_name"], result["url"],
            result["status_code"], result["response_time_ms"],
            int(result["is_healthy"]), result["ssl_days_left"],
            result["error_msg"]
        ))


def insert_incident(category, severity, resource_name,
                    metric_value, threshold_value, description):
    from datetime import datetime

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO system_incidents (
                timestamp, category, severity, resource_name,
                metric_value, threshold_value, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(), category, severity,
            resource_name, metric_value, threshold_value, description
        ))

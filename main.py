
import sys
import asyncio
import time
from pathlib import Path

# Accès aux modules du dossier src
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from system_collector import collect_system_metrics
from process_monitor import get_top_processes
from healthchecks import check_http, check_ssl, check_tcp
from database import (
    initialize_database,
    insert_host_metrics,
    insert_disk_partitions,
    insert_processes,
    insert_service_health,
    insert_incident
)


# Configuration
INTERVAL = 5
SERVICE_URL = "https://example.com"

# Mémorisation des alertes déjà déclenchées
active_alerts = set()
memory_history = {}

def check_threshold(category, resource, value, threshold, severity):
    """Détecte un dépassement de seuil sans répéter les alertes."""

    alert_id = f"{category}_{resource}"

    if value is not None and value > threshold:
        if alert_id not in active_alerts:
            insert_incident(
                category,
                severity,
                resource,
                value,
                threshold,
                f"{resource} dépasse le seuil de {threshold}%"
            )
            print(f"[ALERTE] {resource} : {value}%")

        active_alerts.add(alert_id)

    else:
        active_alerts.discard(alert_id)


async def start_monitoring():
    initialize_database()

    print("================================")
    print("       SYSWATCH-API")
    print("================================")
    print("Supervision démarrée...")
    print("Intervalle :", INTERVAL, "secondes")

    previous_disk = None
    previous_time = None

    while True:
        cycle_start = time.perf_counter()

        try:
            # MODULE A : Collecte système
            metrics = collect_system_metrics()

            current_time = time.perf_counter()

            # Calcul des débits disque en Mo/s
            if previous_disk is not None:
                elapsed = current_time - previous_time

                metrics["disk_read_mb_s"] = max(
                    0,
                    (metrics["disk_read_mb"] - previous_disk["read"]) / elapsed
                )

                metrics["disk_write_mb_s"] = max(
                    0,
                    (metrics["disk_write_mb"] - previous_disk["write"]) / elapsed
                )
            else:
                metrics["disk_read_mb_s"] = 0
                metrics["disk_write_mb_s"] = 0

            previous_disk = {
                "read": metrics["disk_read_mb"],
                "write": metrics["disk_write_mb"]
            }
            previous_time = current_time

            insert_host_metrics(metrics)

            insert_disk_partitions(
                metrics["timestamp"],
                metrics["disk_partitions"]
            )

            # MODULE B : Surveillance des processus
            processes = get_top_processes()

            # Fusion des classements CPU et RAM sans doublons
            all_processes = {
                p["pid"]: p
                for p in processes["top_cpu"] + processes["top_ram"]
            }

            # Détection de fuite mémoire sur 10 relevés consécutifs
            for process in all_processes.values():
                pid = process["pid"]
                ram = process["rss_mb"]

                if pid not in memory_history:
                    memory_history[pid] = []

                memory_history[pid].append(ram)

                # Conserver uniquement les 10 derniers relevés
                memory_history[pid] = memory_history[pid][-10:]

                history = memory_history[pid]

                if len(history) == 10 and all(
                    history[i] < history[i + 1]
                    for i in range(9)
                ):
                    alert_id = f"MEMORY_LEAK_{pid}"

                    if alert_id not in active_alerts:
                        insert_incident(
                            "MEMORY_LEAK",
                            "WARNING",
                            process["name"],
                            ram,
                            history[0],
                            "Augmentation continue de la mémoire sur 10 relevés"
                        )

                        print(
                            f"[ALERTE] Fuite mémoire détectée : "
                            f"{process['name']} ({ram} Mo)"
                        )

                    active_alerts.add(alert_id)

            insert_processes(
                metrics["timestamp"],
                list(all_processes.values())
            )

            # MODULE C : Healthchecks HTTP et SSL
            health = await check_http(SERVICE_URL)

            health["ssl_days_left"] = check_ssl(SERVICE_URL)

            tcp_status = await check_tcp("example.com", 443)

            if not tcp_status:
                health["is_healthy"] = False
                health["error_msg"] = "Port TCP 443 inaccessible"

            insert_service_health(health)

            # MODULE D : Seuils et incidents
            check_threshold(
                "CPU", "CPU global",
                metrics["cpu_pct"], 90, "WARNING"
            )

            check_threshold(
                "RAM", "RAM",
                metrics["ram_pct"], 90, "WARNING"
            )

            for disk in metrics["disk_partitions"]:
                check_threshold(
                    "DISK",
                    disk["mountpoint"],
                    disk["usage_pct"],
                    85,
                    "CRITICAL"
                )

            if not health["is_healthy"]:
                check_threshold(
                    "SERVICE",
                    SERVICE_URL,
                    1,
                    0,
                    "CRITICAL"
                )
            else:
                active_alerts.discard(f"SERVICE_{SERVICE_URL}")

            if health["ssl_days_left"] is not None:
                alert_id = f"SSL_{SERVICE_URL}"

                if health["ssl_days_left"] < 15:
                    if alert_id not in active_alerts:
                        insert_incident(
                            "SSL", "WARNING", SERVICE_URL,
                            health["ssl_days_left"], 15,
                            "Certificat SSL expirant dans moins de 15 jours"
                        )

                        print("[ALERTE] Certificat SSL bientôt expiré")

                    active_alerts.add(alert_id)
                else:
                    active_alerts.discard(alert_id)

            print(
                f"[OK] CPU: {metrics['cpu_pct']}% | "
                f"RAM: {metrics['ram_pct']}% | "
                f"HTTP: {health['status_code']} | "
                f"SSL: {health['ssl_days_left']} jours"
            )

        except Exception as error:
            print("[ERREUR]", error)

        # Respect de l'intervalle de collecte
        elapsed = time.perf_counter() - cycle_start
        await asyncio.sleep(max(0, INTERVAL - elapsed))


if __name__ == "__main__":
    try:
        asyncio.run(start_monitoring())
    except KeyboardInterrupt:
        print("\nArrêt de SysWatch-API.")

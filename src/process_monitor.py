
import psutil


def get_top_processes(limit=5):
    """Récupère les processus les plus gourmands en CPU et RAM."""

    processes = []

    for process in psutil.process_iter(
        ['pid', 'name', 'status', 'memory_info', 'num_threads']
    ):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "status": info["status"],
                "cpu_pct": process.cpu_percent(interval=None),
                "rss_mb": round(
                    info["memory_info"].rss / (1024 ** 2), 2
                ),
                "num_threads": info["num_threads"],
                "open_files": len(process.open_files())
            })

        except (psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess):
            continue

    top_cpu = sorted(
        processes,
        key=lambda p: p["cpu_pct"],
        reverse=True
    )[:limit]

    top_ram = sorted(
        processes,
        key=lambda p: p["rss_mb"],
        reverse=True
    )[:limit]

    return {
        "top_cpu": top_cpu,
        "top_ram": top_ram
    }

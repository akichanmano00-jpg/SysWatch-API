
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from system_collector import collect_system_metrics


if __name__ == "__main__":
    metrics = collect_system_metrics()

    print("\n===== SYSWATCH-API =====")
    print("Machine :", metrics["hostname"])
    print("Système :", metrics["system"])
    print("CPU :", metrics["cpu_pct"], "%")
    print("RAM :", metrics["ram_pct"], "%")
    print("RAM utilisée :", metrics["ram_used_mb"], "Mo")
    print("Swap :", metrics["swap_pct"], "%")

    print("\nPartitions :")
    for disk in metrics["disk_partitions"]:
        print(disk)

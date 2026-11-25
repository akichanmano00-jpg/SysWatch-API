
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from process_monitor import get_top_processes


if __name__ == "__main__":
    result = get_top_processes()

    print("\n===== TOP 5 CPU =====")

    for process in result["top_cpu"]:
        print(
            process["pid"],
            process["name"],
            process["cpu_pct"], "%",
            process["rss_mb"], "Mo"
        )

    print("\n===== TOP 5 RAM =====")

    for process in result["top_ram"]:
        print(
            process["pid"],
            process["name"],
            process["rss_mb"], "Mo",
            process["num_threads"], "threads",
            process["open_files"], "fichiers"
        )


import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from database import initialize_database, get_connection


if __name__ == "__main__":
    initialize_database()

    with get_connection() as conn:
        tables = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """).fetchall()

    print("===== BASE SYSWATCH-API =====")
    print("Base de données créée avec succès.")

    for table in tables:
        print("-", table["name"])

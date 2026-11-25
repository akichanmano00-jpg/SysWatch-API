
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from healthchecks import check_http, check_tcp, check_ssl


async def main():

    url = "https://example.com"

    print("\n===== TEST HTTP =====")
    http = await check_http(url)

    print("Code HTTP :", http["status_code"])
    print("Temps de réponse :", http["response_time_ms"], "ms")
    print("Disponibilité :", http["is_healthy"])
    print("Erreur :", http["error_msg"])

    print("\n===== TEST TCP =====")
    tcp = await check_tcp("example.com", 443)
    print("Port 443 accessible :", tcp)

    print("\n===== TEST SSL =====")
    ssl_days = check_ssl(url)
    print("Jours avant expiration :", ssl_days)


if __name__ == "__main__":
    asyncio.run(main())


import aiohttp
import asyncio
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import truststore

truststore.inject_into_ssl()


async def check_http(url, expected_status=200, json_key=None):
    """Vérifie la disponibilité et le temps de réponse HTTP."""

    start = time.perf_counter()

    result = {
        "timestamp": datetime.now().isoformat(),
        "service_name": url,
        "url": url,
        "status_code": None,
        "response_time_ms": 0,
        "is_healthy": False,
        "ssl_days_left": None,
        "error_msg": None
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=aiohttp.TCPConnector(ssl=ssl.create_default_context())
        ) as session:
            
            async with session.get(url) as response:
                result["status_code"] = response.status
                result["response_time_ms"] = round(
                    (time.perf_counter() - start) * 1000, 2
                )

                healthy = response.status == expected_status

                if json_key:
                    try:
                        data = await response.json()
                        healthy = healthy and json_key in data
                    except (ValueError, aiohttp.ContentTypeError):
                        healthy = False

                result["is_healthy"] = healthy

                if not healthy:
                    result["error_msg"] = "Statut HTTP ou contenu invalide"

    except Exception as error:
        result["error_msg"] = str(error)

    return result


async def check_tcp(host, port):
    """Vérifie si un port TCP est accessible."""

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=5
        )

        writer.close()
        await writer.wait_closed()

        return True

    except Exception:
        return False


def check_ssl(url):
    """Vérifie le nombre de jours avant expiration du certificat."""

    try:
        hostname = urlparse(url).hostname

        if not hostname:
            raise ValueError("Nom de domaine invalide")

        context = ssl.create_default_context()

        with socket.create_connection(
            (hostname, 443), timeout=5
        ) as connection:

            with context.wrap_socket(
                connection, server_hostname=hostname
            ) as secure_socket:

                certificate = secure_socket.getpeercert()

        expiry = datetime.strptime(
            certificate["notAfter"], "%b %d %H:%M:%S %Y %Z"
        ).replace(tzinfo=timezone.utc)

        remaining = expiry - datetime.now(timezone.utc)

        return max(0, remaining.days)

    except Exception as error:
        print("Erreur SSL :", error)
        return None

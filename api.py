import requests
import logging

log = logging.getLogger(__name__)

API_STATUS_ENDPOINT = "/api/status"

def get_status(host: str, port: str) -> dict:
    url = f"http://{host}:{port}{API_STATUS_ENDPOINT}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data= response.json()
    log.info("Api Status %s: %s",host, data)

    return data

def is_ready(host: str, port: str) -> bool:
    url = f"http://{host}:{port}{API_STATUS_ENDPOINT}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return bool(response.json().get("ready", False))
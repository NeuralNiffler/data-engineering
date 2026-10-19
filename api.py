import requests
import logging

log = logging.getLogger(__name__)

API_STATUS_ENDPOINT = "/api/status"
CHANGE_SEQ_KEY = "changeSeq"
READY_KEY = "ready"

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

    return bool(response.json().get(READY_KEY, False))

def get_change_seq(host: str, port: str) -> int:
    return int(get_status(host, port)[CHANGE_SEQ_KEY])

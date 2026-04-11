import os

import requests
from dotenv import load_dotenv


load_dotenv()


def _enabled() -> bool:
    opt_in = os.getenv("COMMUNITY_OPT_IN", "false").strip().lower()
    api_url = os.getenv("COMMUNITY_API_URL", "").strip()
    api_key = os.getenv("COMMUNITY_API_KEY", "").strip()
    return opt_in in {"1", "true", "yes", "on"} and bool(api_url) and bool(api_key)


def submit(data: dict) -> bool:
    if not _enabled():
        return False

    try:
        response = requests.post(
            f"{os.getenv('COMMUNITY_API_URL', '').rstrip('/')}/submit",
            json=data,
            headers={"x-api-key": os.getenv("COMMUNITY_API_KEY", "")},
            timeout=5,
        )
        return response.ok
    except Exception as exc:
        print(f"Warning: failed to submit community data: {exc}")
        return False


def fetch_records() -> list:
    if not _enabled():
        return []

    try:
        response = requests.get(
            f"{os.getenv('COMMUNITY_API_URL', '').rstrip('/')}/records",
            headers={"x-api-key": os.getenv("COMMUNITY_API_KEY", "")},
            timeout=5,
        )
        if not response.ok:
            return []
        payload = response.json()
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            records = payload.get("records")
            if isinstance(records, list):
                return records
        return []
    except Exception as exc:
        print(f"Warning: failed to fetch community records: {exc}")
        return []

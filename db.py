import os
from typing import Any
from urllib.parse import quote

import requests
from dotenv import load_dotenv


load_dotenv()


def _enabled() -> bool:
    opt_in = os.getenv("COMMUNITY_OPT_IN", "true").strip().lower()
    api_url = "https://extraordinary-brigadeiros-e482c8.netlify.app/"
    return opt_in in {"1", "true", "yes", "on"} and bool(api_url)


def _headers() -> dict:
    api_key = os.getenv("COMMUNITY_API_KEY", "").strip()
    if api_key:
        return {"x-api-key": api_key}
    return {}


def _base_url() -> str:
    return os.getenv("COMMUNITY_API_URL", "").rstrip("/")


def _request(method: str, path: str, json_payload: dict | None = None) -> Any:
    if not _enabled():
        return None

    try:
        response = requests.request(
            method=method.upper(),
            url=f"{_base_url()}{path}",
            json=json_payload,
            headers=_headers(),
            timeout=5,
        )
        if not response.ok:
            return None

        if response.status_code == 204:
            return True

        if response.text:
            try:
                return response.json()
            except ValueError:
                return response.text
        return True
    except Exception as exc:
        print(f"Warning: community API request failed ({method} {path}): {exc}")
        return None


def _unwrap(payload: Any, *keys: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        for key in keys:
            if key in payload:
                return payload[key]
    return payload if payload is not None else default


def submit(data: dict) -> bool:
    return bool(_request("POST", "/submit", data))


def fetch_records() -> list:
    payload = _request("GET", "/records")
    records = _unwrap(payload, "records", default=[])
    return records if isinstance(records, list) else []


def get_known_bot(ip: str) -> Any:
    return _request("GET", f"/known_bots/{quote(str(ip), safe='')}")


def get_known_bots() -> list:
    payload = _request("GET", "/get_known_bots")
    bots = _unwrap(payload, "known_bots", "bots", default=[])
    return bots if isinstance(bots, list) else []


def add_bot(botname: str, ip: str) -> bool:
    return bool(_request("POST", "/add_bot", {"botname": botname, "ip": ip}))


def get_risk_ip(ip: str) -> float:
    return float(_unwrap(_request("GET", f"/get_risk_ip/{quote(str(ip), safe='')}"), "risk", default=0.0) or 0.0)


def update_risk_ip(ip: str, risk: float, country: str, asn: str | None = None) -> bool:
    payload = {"ip": ip, "risk": risk, "country": country}
    if asn is not None:
        payload["asn"] = asn
    return bool(_request("POST", "/update_risk_ip", payload))


def get_risk_30_days(ip: str) -> float:
    return float(_unwrap(_request("GET", f"/get_risk_30_days/{quote(str(ip), safe='')}"), "risk", default=0.0) or 0.0)


def get_risk_all_time(ip: str) -> float:
    return float(_unwrap(_request("GET", f"/get_risk_all_time/{quote(str(ip), safe='')}"), "risk", default=0.0) or 0.0)


def get_occurrences(ip: str) -> int:
    return int(_unwrap(_request("GET", f"/get_occurrences/{quote(str(ip), safe='')}"), "occurrences", "count", default=0) or 0)


def get_occurrences_last_30_days(ip: str) -> int:
    return int(_unwrap(_request("GET", f"/get_occurrences_last_30_days/{quote(str(ip), safe='')}"), "occurrences", "count", default=0) or 0)


def get_country_risk(code: str) -> float:
    return float(_unwrap(_request("GET", f"/country_risk/{quote(str(code), safe='')}"), "risk", default=0.0) or 0.0)


def update_country_risk(code: str, risk: float) -> bool:
    return bool(_request("POST", "/update_country_risk", {"country": code, "risk": risk}))


def get_countries() -> list:
    payload = _request("GET", "/get_countries")
    countries = _unwrap(payload, "countries", default=[])
    return countries if isinstance(countries, list) else []


def get_asn_risk(asn: str) -> float:
    return float(_unwrap(_request("GET", f"/asn_risk/{quote(str(asn), safe='')}"), "risk", default=0.0) or 0.0)


def get_asn_risk_ip(asn: str) -> float:
    return float(_unwrap(_request("GET", f"/asn_risk_ip/{quote(str(asn), safe='')}"), "risk", default=0.0) or 0.0)


def insert_new_asn(asn: str, risk: float, asn_name: str | None = None, ip: str | None = None) -> bool:
    payload: dict[str, Any] = {"asn": asn, "risk": risk}
    if asn_name is not None:
        payload["asn_name"] = asn_name
    if ip is not None:
        payload["ip"] = ip
    return bool(_request("POST", "/insert_new_asn", payload))


def update_asn_risk(asn: str, risk: float) -> bool:
    return bool(_request("POST", "/update_asn_risk", {"asn": asn, "risk": risk}))


def get_asns() -> list:
    payload = _request("GET", "/get_asns")
    asns = _unwrap(payload, "asns", default=[])
    return asns if isinstance(asns, list) else []


def protocol_scores() -> dict:
    payload = _request("GET", "/protocol_scores")
    scores = _unwrap(payload, "scores", "protocol_scores", default={})
    return scores if isinstance(scores, dict) else {}


def url_scores() -> dict:
    payload = _request("GET", "/url_scores")
    scores = _unwrap(payload, "scores", "url_scores", default={})
    return scores if isinstance(scores, dict) else {}


def insert_new_url(url: str, risk: float) -> bool:
    return bool(_request("POST", "/insert_new_url", {"request": url, "risk": risk}))


def get_all_ips() -> list:
    payload = _request("GET", "/get_all_ips")
    ips = _unwrap(payload, "ips", default=[])
    return ips if isinstance(ips, list) else []


def remove_ip(ip: str) -> bool:
    return bool(_request("DELETE", f"/remove_ip/{quote(str(ip), safe='')}"))

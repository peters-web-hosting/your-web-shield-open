from datetime import datetime
from types import SimpleNamespace

import db
from helpers.IPFunctions import IPFunctions
from helpers.Modifiers import Modifiers


def memoize(func):
    cache = {}

    def inner_cached(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return inner_cached


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


class Database:

    def __init__(self) -> object:
        self.connect()

    def connect(self):
        return None

    def close(self):
        return None

    def commit(self):
        return None

    def _records(self):
        records = db.fetch_records()
        return [record for record in records if isinstance(record, dict)]

    def _record_objects(self, records):
        return [SimpleNamespace(**record) for record in records if isinstance(record, dict)]

    def _submit(self, payload):
        body = {
            "created_at": datetime.utcnow().isoformat(),
            **payload,
        }
        return db.submit(body)

    def known_bots(self, ip):
        try:
            payload = db.get_known_bot(ip)
            if isinstance(payload, dict):
                return payload.get("botname") or payload.get("name") or "n/a"
            if isinstance(payload, str):
                return payload or "n/a"
        except Exception as e:
            print(f"Error: {e}")
        return "n/a"

    def get_known_bots(self):
        try:
            return self._record_objects(db.get_known_bots())
        except Exception as e:
            print(f"Error: {e}")
            return []

    def getRiskIP(self, ip):
        try:
            endpoint_risk = db.get_risk_ip(ip)
            if endpoint_risk:
                return endpoint_risk
        except Exception:
            pass

        return (
            self.getRisk30Days(ip) * Modifiers.RECENT
            + self.getRiskAllTime(ip) * Modifiers.ALL_TIME_DB
        )

    def updateRiskIp(self, ip, risk, country, asn):
        try:
            db.update_risk_ip(ip=ip, risk=risk, country=country, asn=str(asn) if asn is not None else None)
        except Exception as e:
            print(f"Error {e}")

    def getOcourances(self, ip):
        try:
            return db.get_occurrences(ip)
        except Exception as e:
            print(f"Error {e}")
            return 0

    def getOcourancesLast30days(self, ip):
        try:
            return db.get_occurrences_last_30_days(ip)
        except Exception as e:
            print(f"Error {e}")
            return 0

    def getRisk30Days(self, ip):
        try:
            return db.get_risk_30_days(ip)
        except Exception as e:
            print(f"error {e}")
            return 0.0

    def getRiskAllTime(self, ip):
        try:
            return db.get_risk_all_time(ip)
        except Exception as e:
            print(f"error {e}")
            return 0.0

    @memoize
    def countryRisk(self, code):
        try:
            return db.get_country_risk(code)
        except Exception as e:
            print(f"error {e}")
            return 0.0

    def setProtocolScores(self):
        try:
            scores = db.protocol_scores()
            return {k: _safe_float(v) for k, v in scores.items()}
        except Exception as e:
            print(f"Error: {e}")
            return None

    def setUrlScores(self):
        try:
            scores = db.url_scores()
            return {k: _safe_float(v) for k, v in scores.items()}
        except Exception as e:
            print(f"Error: {e}")
            return None

    def getAsnRisk(self, asn):
        try:
            return db.get_asn_risk(asn)
        except Exception as e:
            print(f"Error: {e}")
            return None

    def insert_new_asn(self, asn, new_val, ip):
        try:
            fun = IPFunctions()
            db.insert_new_asn(
                asn=str(asn),
                risk=new_val,
                asn_name=str(fun.get_asn_name(ip=ip)),
                ip=ip,
            )
        except Exception as e:
            print("Error:", e)

    def insert_new_URL(self, URL, new_val):
        try:
            db.insert_new_url(URL, new_val)
            return f"URL added or updated: {URL}"
        except Exception as e:
            print("Error:", e)

    def update_country_risk(self, country, risk):
        try:
            db.update_country_risk(country, risk)
        except Exception as e:
            print("Error:", e)

    def get_asn_risk_ip(self, asn):
        try:
            risk = db.get_asn_risk_ip(asn)
            print("Risk:", risk)
            return risk
        except Exception as e:
            print(f"Error: {e}")
            return 0.0

    def update_asn_risk(self, asn, risk):
        try:
            db.update_asn_risk(str(asn), risk)
        except Exception as e:
            print("Error:", e)

    def add_bot(self, botname, ip):
        try:
            db.add_bot(botname, ip)
        except Exception as e:
            print("Error:", e)

    def get_all_ips(self):
        try:
            return self._record_objects(db.get_all_ips())
        except Exception as e:
            print("Error:", e)
            return []

    def remove_ip(self, ip):
        try:
            db.remove_ip(ip)
        except Exception as e:
            print("Error:", e)

    def getASNs(self):
        try:
            asns = db.get_asns()
            return [(asn,) if not isinstance(asn, (list, tuple)) else tuple(asn) for asn in asns]
        except Exception as e:
            print("Error:", e)
            return []

    def getCountries(self):
        try:
            countries = db.get_countries()
            return [(country,) if not isinstance(country, (list, tuple)) else tuple(country) for country in countries]
        except Exception as e:
            print("Error:", e)
            return []

    # Legacy report endpoints still use /submit + /records payloads.
    def insert_report_row(self, report, ip, risk, occurrences, asn, asnName, country):
        try:
            self._submit(
                {
                    "record_type": "report_row",
                    "action": "insert",
                    "report_id": report,
                    "ip": ip,
                    "risk": risk,
                    "occurrences": occurrences,
                    "asn": str(asn) if asn is not None else None,
                    "asn_name": asnName,
                    "country": country,
                }
            )
        except Exception as e:
            print("Error:", e)

    def set_report_dates(self, reportId, first_date, last_date):
        try:
            self._submit(
                {
                    "record_type": "org_report",
                    "action": "upsert",
                    "report_id": reportId,
                    "first_date_in_log": first_date.isoformat() if first_date else None,
                    "last_date_in_log": last_date.isoformat() if last_date else None,
                }
            )
        except Exception as e:
            print("Error:", e)

    def set_report_status(self, reportId, status):
        try:
            self._submit(
                {
                    "record_type": "org_report",
                    "action": "upsert",
                    "report_id": reportId,
                    "status": status,
                }
            )
        except Exception as e:
            print("Error:", e)

    def check_report_exists(self, reportId):
        try:
            target = str(reportId)
            for record in self._records():
                if record.get("record_type") == "org_report" and str(record.get("report_id")) == target:
                    return True
            return False
        except Exception as e:
            print("Error:", e)
            return False

    def check_report_scanned(self, reportId):
        try:
            target = str(reportId)
            for record in self._records():
                if record.get("record_type") == "org_report" and str(record.get("report_id")) == target:
                    return record.get("status") == 1
            return False
        except Exception as e:
            print("Error:", e)
            return False

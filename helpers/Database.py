from datetime import datetime, timedelta
from types import SimpleNamespace

from helpers.IPFunctions import IPFunctions
from helpers.Modifiers import Modifiers
import community


def memoize(func):
    cache = {}

    def inner_cached(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return inner_cached


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _unwrap_scalar(value):
    if isinstance(value, (list, tuple)) and value:
        return value[0]
    return value


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
        records = community.fetch_records()
        return [record for record in records if isinstance(record, dict)]

    def _record_objects(self, records):
        return [SimpleNamespace(**record) for record in records]

    def _submit(self, payload):
        body = {
            "created_at": datetime.utcnow().isoformat(),
            **payload,
        }
        return community.submit(body)

    def _ip_log_records(self):
        records = self._records()
        deleted_ips = {
            record.get("ip")
            for record in records
            if record.get("record_type") == "ip_log" and record.get("action") == "delete"
        }
        return [
            record for record in records
            if record.get("record_type") == "ip_log"
            and record.get("action") != "delete"
            and record.get("ip") not in deleted_ips
        ]

    def known_bots(self, ip):
        bot_name = "n/a"
        try:
            for bot in self.get_known_bots():
                if getattr(bot, "ip", None) == ip:
                    bot_name = getattr(bot, "botname", bot_name) or bot_name
                    break
        except Exception as e:
            print(f"Error: {e}")
        finally:
            return bot_name

    def get_known_bots(self):
        try:
            bots = []
            seen = set()
            for record in self._records():
                if record.get("record_type") != "bot":
                    continue
                ip = record.get("ip")
                if not ip or ip in seen:
                    continue
                seen.add(ip)
                bots.append(record)
            return self._record_objects(bots)
        except Exception as e:
            print(f"Error: {e}")
            return []

    def getRiskIP(self, ip):
        return (
            self.getRisk30Days(ip) * Modifiers.RECENT
            + self.getRiskAllTime(ip) * Modifiers.ALL_TIME_DB
        )

    def updateRiskIp(self, ip, risk, country, asn):
        try:
            self._submit(
                {
                    "record_type": "ip_log",
                    "action": "upsert",
                    "ip": ip,
                    "risk": risk,
                    "datereported": datetime.utcnow().isoformat(),
                    "country": country,
                    "asn": str(asn) if asn is not None else None,
                }
            )
        except Exception as e:
            print(f"Error {e}")

    def getOcourances(self, ip):
        occurrences = 0
        try:
            occurrences = sum(1 for record in self._ip_log_records() if record.get("ip") == ip)
        except Exception as e:
            print(f"Error {e}")
        finally:
            return occurrences

    def getOcourancesLast30days(self, ip):
        occurrences = 0
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            occurrences = sum(
                1
                for record in self._ip_log_records()
                if record.get("ip") == ip
                and (_parse_datetime(record.get("datereported")) or datetime.min) > cutoff
            )
        except Exception as e:
            print(f"Error {e}")
        finally:
            return occurrences

    def getRisk30Days(self, ip):
        risk = 0.0
        try:
            cutoff = datetime.utcnow() - timedelta(days=30)
            matching = [
                _safe_float(record.get("risk"))
                for record in self._ip_log_records()
                if record.get("ip") == ip
                and (_parse_datetime(record.get("datereported")) or datetime.min) < cutoff
            ]
            if matching:
                risk = sum(matching) / len(matching)
        except Exception as e:
            print(f"error {e}")
        finally:
            return risk

    def getRiskAllTime(self, ip):
        risk = 0.0
        try:
            matching = [
                _safe_float(record.get("risk"))
                for record in self._ip_log_records()
                if record.get("ip") == ip
            ]
            if matching:
                risk = sum(matching) / len(matching)
        except Exception as e:
            print(f"error {e}")
        finally:
            return risk

    @memoize
    def countryRisk(self, code):
        risk = 0.0
        try:
            matching = [
                _safe_float(record.get("risk"))
                for record in self._ip_log_records()
                if record.get("country") == code
            ]
            if matching:
                risk = sum(matching) / len(matching)
        except Exception as e:
            print(f"error {e}")
            print("DB 84")
        finally:
            return risk

    def setProtocolScores(self):
        try:
            scores = {}
            for record in self._records():
                if record.get("record_type") != "code_risk":
                    continue
                httpcode = record.get("httpcode")
                if httpcode is None or httpcode in scores:
                    continue
                scores[httpcode] = _safe_float(record.get("risk"))
            return scores
        except Exception as e:
            print(f"Error: {e}")
            return None

    def setUrlScores(self):
        try:
            scores = {}
            for record in self._records():
                if record.get("record_type") != "request_risk":
                    continue
                request = record.get("request")
                if not request or request in scores:
                    continue
                scores[request] = _safe_float(record.get("risk"))
            return scores
        except Exception as e:
            print(f"Error: {e}")
            return None

    def getAsnRisk(self, asn):
        try:
            target = str(_unwrap_scalar(asn))
            for record in self._records():
                if record.get("record_type") == "asn_risk" and str(record.get("asn")) == target:
                    return _safe_float(record.get("risk"))
            return 0.0
        except Exception as e:
            print(f"Error: {e}")
            return None

    def insert_new_asn(self, asn, new_val, ip):
        try:
            fun = IPFunctions()
            self._submit(
                {
                    "record_type": "asn_risk",
                    "action": "upsert",
                    "asn": str(_unwrap_scalar(asn)),
                    "asn_name": str(fun.get_asn_name(ip=ip)),
                    "risk": new_val,
                    "ip": ip,
                }
            )
        except Exception as e:
            print("Error:", e)

    def insert_new_URL(self, URL, new_val):
        try:
            self._submit(
                {
                    "record_type": "request_risk",
                    "action": "upsert",
                    "request": URL,
                    "risk": new_val,
                }
            )
            return f"URL added or updated: {URL}"
        except Exception as e:
            print("Error:", e)

    def update_country_risk(self, country, risk):
        try:
            self._submit(
                {
                    "record_type": "country_risk",
                    "action": "upsert",
                    "country": country,
                    "risk": risk,
                }
            )
        except Exception as e:
            print("Error:", e)

    def get_asn_risk_ip(self, asn):
        target = str(_unwrap_scalar(asn))
        try:
            matching = [
                _safe_float(record.get("risk"))
                for record in self._ip_log_records()
                if str(record.get("asn")) == target
            ]
            if matching:
                risk = sum(matching) / len(matching)
                print("Risk:", risk)
                return risk
            return 0.0
        except Exception as e:
            print(f"Error: {e}")
            return 0.0

    def update_asn_risk(self, asn, risk):
        try:
            self._submit(
                {
                    "record_type": "asn_risk",
                    "action": "upsert",
                    "asn": str(_unwrap_scalar(asn)),
                    "risk": risk,
                }
            )
        except Exception as e:
            print("Error:", e)

    def add_bot(self, botname, ip):
        try:
            self._submit(
                {
                    "record_type": "bot",
                    "action": "upsert",
                    "botname": botname,
                    "ip": ip,
                }
            )
        except Exception as e:
            print("Error:", e)

    def get_all_ips(self):
        try:
            return self._record_objects(self._ip_log_records())
        except Exception as e:
            print("Error:", e)
            return []

    def remove_ip(self, ip):
        try:
            self._submit(
                {
                    "record_type": "ip_log",
                    "action": "delete",
                    "ip": ip,
                }
            )
        except Exception as e:
            print("Error:", e)

    def getASNs(self):
        try:
            seen = set()
            asns = []
            for record in self._records():
                asn = record.get("asn")
                if not asn or asn in seen:
                    continue
                seen.add(asn)
                asns.append((asn,))
            return asns
        except Exception as e:
            print("Error:", e)
            return []

    def getCountries(self):
        try:
            seen = set()
            countries = []
            for record in self._records():
                country = record.get("country")
                if not country or country in seen:
                    continue
                seen.add(country)
                countries.append((country,))
            return countries
        except Exception as e:
            print("Error:", e)
            return []

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


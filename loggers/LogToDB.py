from helpers.Database import Database
from helpers.IPFunctions import IPFunctions
from community import _enabled


class LogToDB():
    def __init__(self, report):
        self.report = report[:-4]
        assert self.report is not None

        self.database = Database()
        self.functions = IPFunctions()
        self.database.connect()

        if not _enabled():
            return

        # Check if the report exists in the database
        if not self.database.check_report_exists(self.report):
            exit("Report does not exist in the database")

        # Check if the report has been scanned before
        if self.database.check_report_scanned(self.report):
            exit("Report has already been scanned")

    def log_to_file(self, ip, risk, orrcances_of_ip_log, _is_googleBot=False, _isBing=False):

        risk, asn, asnName, country = self.pre_format(ip, risk)

        self.database.insert_report_row(self.report, ip, risk, orrcances_of_ip_log, asn, asnName, country)

    def pre_format(self, ip, risk):
        asn = self.functions.get_asn(ip)
        asnName = self.functions.get_asn_name(ip)
        country = self.functions.get_location(ip)

        if risk == float('inf'):
            risk = 1

        return risk, asn, asnName, country

    def make_head(self):
        pass

    def add_date_range(self, first_date, last_date):
        self.database.set_report_dates(self.report, first_date, last_date)

    def close(self):
        self.database.set_report_status(self.report, 1)

import math
import random
import time

from analise.BotAnalysis import BotAnalysis
from helpers.Database import Database
from helpers.IPFunctions import IPFunctions
from helpers.Modifiers import Modifiers


class Risk:
    def __init__(self):
        self.countryRisk = 0.0
        self.responseRisk = 0.0
        self.requestRisk = 0.0
        self.userAgegentRisk = 0.0
        self.risk = 1.0
        self.asnrisk = 0.0
        self.requestResponseRisk = 0.0
        self.analyzed_user_agents = {}
        self.orrcancesOfipRisk = 0.0
        self.analyzed_user_agents = {}  # Dictionary to store analyzed user agents and their results
        self.asn = 0

    @staticmethod
    def contain_ignore_case(string, substring):
        return substring.lower() in string.lower()

    def main_calulate_risk(self, ip, dataStore, countryCode, loggerWithFile, gbot, bbot, kbot, botAnalsis, database):
        self.risk = 1.0
        orrcances_of_ip = dataStore.get_occurrences_of_ip().get(ip)

        if self.isBot(ip, loggerWithFile, orrcances_of_ip, gbot, bbot, kbot):
            self.risk = 0.0
            return self.risk

        self.calulate_occurrences_sig(ip, dataStore)
        self.countryRisk = database.countryRisk(countryCode) or 0.0

        self.responseRisk = 0.0
        self.requestRisk = 0.0
        self.userAgegentRisk = 0.0
        self.main_loop(ip, dataStore, botAnalsis)
        self.asn_cal(ip, database)
        self.request_response_risk = self.requestRisk + self.responseRisk
        if self.request_response_risk == float('inf'):
            self.request_response_risk = 0.01

        self.risk = self.calulate_risk()
        loggerWithFile.log_to_file(ip, self.risk, orrcances_of_ip)

        asns_string = str(self.asn) if self.asn is not None else "unknown"
        return self.normalise(ip, dataStore, self.risk, countryCode, asns_string)

    def isBot(self, ip, loggerWithFile, occurrences_of_ip, gBot, bBot, knownBot):
        if knownBot.is_known(ip):
            loggerWithFile.log_to_file(ip, self.risk, occurrences_of_ip)
            return True

        if gBot.is_googlebot_ip(ip):
            loggerWithFile.log_to_file(ip, self.risk, occurrences_of_ip, _is_googleBot=True)
            return True

        if bBot.is_bing(ip):
            loggerWithFile.log_to_file(ip, self.risk, occurrences_of_ip, _isBing=True)
            return True

        return False

    def main_loop(self, ip, dataStore, botAnalsis):
        for h in dataStore.get_hits():
            if h.iPaddress == ip:
                self.request_response(dataStore, h)
                if h.userAgent not in self.analyzed_user_agents:
                    analysis_result = botAnalsis.analyze(h.userAgent)
                    self.analyzed_user_agents[h.userAgent] = analysis_result
                    self.userAgegentRisk = analysis_result  # Update userAgegentRisk with the analysis result

                else:
                    self.userAgegentRisk = self.analyzed_user_agents[
                        h.userAgent]  # Update userAgegentRisk with the analysis result

    def request_response(self, dataStore, h):
        self.responseRisk += dataStore.get_response_scores().get(h.responseCode, 0.0)
        if "${" in h.userAgent:
            self.requestRisk += 5
        self.requestRisk += dataStore.search_urls(h.request)
        if h.responseSize == 0:
            self.responseRisk += 6
        if "1.1" in h.httpVerson:
            self.requestRisk += 1

    def asn_cal(self, ip, database):
        ipFunctions = IPFunctions()
        self.asn = ipFunctions.get_asn(ip)
        self.asnrisk = database.getAsnRisk(self.asn) if self.asn is not None else 0.1

    def normalise(self, ip, dataStore, risk, countryCode, ASN):
        if random.random() < 0.75:
            # self.database.updateRiskIp(ip, self.calulate_riskraw(), countryCode, ASN)
            dataStore.add_reported_ip(ip)
        if risk > 100:
            return 100
        elif risk < 1:
            return 1
        else:
            return risk

    def calulate_risk(self):
        return (
            self.orrcancesOfipRisk * Modifiers.OCCURANCES
            + self.requestResponseRisk * Modifiers.REQUEST_RESPONSE
            + self.countryRisk * Modifiers.COUNTRY
            + self.asnrisk * Modifiers.ASN
            + self.userAgegentRisk * Modifiers.USER_AGENT
        )

    def calulate_riskraw(self):
        return (
            self.orrcancesOfipRisk * Modifiers.OCCURANCES
            + self.requestResponseRisk * Modifiers.REQUEST_RESPONSE
            + self.userAgegentRisk * Modifiers.USER_AGENT
        )

    def calulate_occurrences_sig(self, ip, dataStore):
        x = dataStore.get_occurrences_of_ip().get(ip)
        # Adjust the scale of the risk score to range from 0 to 100
        self.occurrences_of_ip_risk = 100.0 / (1.0 + math.exp(-0.1 * x))

    def calulate_risks(self, ip, dataStore, countryCode, loggerWithFile, gbot, bbot, kbot, botAnalsis, database):
        r1 = self.main_calulate_risk(ip, dataStore, countryCode, loggerWithFile, gbot, bbot, kbot, botAnalsis, database)
        r2 = database.getRiskIP(ip)
#        print("IP:" + str(r1) + "DB:" + str(r2))
        total_risk = (
            r1 * Modifiers.IP + r2 * Modifiers.DB
        )
        return min(total_risk, 100)

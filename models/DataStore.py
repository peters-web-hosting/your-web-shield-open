
class DataStore:
    def __init__(self):
        self.hits = []
        self.reported_ips = []
        self.occurrences_of_ip = {}
        self.response_risk = {}
        self.referers = {}
        self.protocols = {}
        self.pages = {}
        self.responses = {}
        self.risk = {}
        self.protocol_scores = {}
        self.url_sources = {}
        self.auto_report = 0
        self.users_ip = ""
        self.website = ""
        self.output_dir = "data"
        self.googleIps = []

    def set_google_ips(self, ips):
        self.googleIps = ips

    def get_google_ips(self):
        return self.googleIps

    def add_hits(self, hits):
        self.hits.extend(hits)

    def add_hit(self, hit):
        self.hits.append(hit)

    def get_out_dir(self):
        return self.output_dir

    def add_reported_ip(self, ip):
        self.reported_ips.append(ip)

    def get_risk(self):
        return self.risk

    def set_users_ip(self, users_ip):
        self.users_ip = users_ip

    def get_users_ip(self):
        return self.users_ip

    def get_hits(self):
        return self.hits

    def get_occurrences_of_ip(self):
        return self.occurrences_of_ip

    def get_pages(self):
        return self.pages

    def get_protocols(self):
        return self.protocols

    def get_referers(self):
        return self.referers

    def get_reported_ips(self):
        return self.reported_ips

    def get_responses(self):
        return self.responses

    def set_hits(self, hits):
        self.hits = hits

    def set_risk(self, risk):
        self.risk = risk

    def add_risk(self, ip, risk):
        self.risk[ip] = risk

    def set_occurrences_of_ip(self, occurrences_of_ip):
        self.occurrences_of_ip = occurrences_of_ip

    def set_pages(self, pages):
        self.pages = pages

    def set_protocols(self, protocols):
        self.protocols = protocols

    def set_referers(self, referers):
        self.referers = referers

    def set_reported_ips(self, reported_ips):
        self.reported_ips = reported_ips

    def set_responses(self, responses):
        self.responses = responses

    def get_response_scores(self):
        return self.protocol_scores

    def set_protocol_scores(self, protocol_scores):
        self.protocol_scores = protocol_scores

    def get_response_risk(self):
        return self.response_risk

    def set_response_risk(self, response_risk):
        self.response_risk = response_risk

    def clear_risks(self):
        self.risk.clear()

    def get_url_sources(self):
        return self.url_sources

    def set_url_sources(self, url_sources):
        self.url_sources = url_sources

    def get_protocol_scores(self):
        return self.protocol_scores

    def search_urls(self, request):
        return sum(value for url,
        value in self.url_sources.items()
                   if request.lower() in url.lower())

    def get_website(self):
        return self.website

    def set_website(self, website):
        self.website = website

    def get_Auto_Report(self):
        return self.auto_report

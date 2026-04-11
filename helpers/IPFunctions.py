import requests
import geoip2.database

class IPFunctions:
    def __init__(self):
        self.country_database = "database/GeoLite2-City.mmdb"
        self.asn_database = "database/GeoLite2-ASN.mmdb"

    def get_location(self, ip):
        try:
            with geoip2.database.Reader(self.country_database) as reader:
                response = reader.city(ip)
                country = response.country
                return country.iso_code
        except Exception as e:
            print("Error:", e)
            return None

    def get_asn(self, ip):
        try:
            with geoip2.database.Reader(self.asn_database) as reader:
                response = reader.asn(ip)
                return response.autonomous_system_number
        except Exception as e:
            print("Error:", e)
            return None

    def get_asn_name(self, ip):
        try:
            with geoip2.database.Reader(self.asn_database) as reader:
                response = reader.asn(ip)
                return response.autonomous_system_organization
        except Exception as e:
            print("Error:", e)
            return None

    def get_user_ip(self):
        try:
            response = requests.get("http://checkip.amazonaws.com")
            return response.text.strip()
        except Exception as e:
            print("Error:", e)
            return None

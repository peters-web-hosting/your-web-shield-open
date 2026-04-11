import requests
import ipaddress
from models.DataStore import DataStore
class GoogleBot:
    def __init__(self):
        self.googlebot_networks = self.fetch_googlebot_ips()

    def fetch_googlebot_ips(self):
        url = "https://developers.google.com/search/apis/ipranges/googlebot.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            googlebot_ranges = []
            for entry in data['prefixes']:
                ip_prefix = entry.get('ipv4Prefix') or entry.get('ipv6Prefix')
                if ip_prefix:
                    googlebot_ranges.append(ip_prefix)
            return [ipaddress.ip_network(range) for range in googlebot_ranges]
        else:
            print(f"Failed to fetch Googlebot IP ranges. Status code: {response.status_code}")
            return []

    def is_googlebot_ip(self, ip_to_check):
        ip = ipaddress.ip_address(ip_to_check)
        for network in self.googlebot_networks:
            if ip in network:
                return True
        return False

if __name__ == "__main__":
    Data = DataStore()
    ip_to_check = input("Enter the IP address to check: ")
    bot = GoogleBot()
    if bot.is_googlebot_ip(ip_to_check):
        print(f"{ip_to_check} is a Googlebot IP address.")
    else:
        print(f"{ip_to_check} is not a Googlebot IP address.")

import ipaddress
import requests
import cachetools


class Bingbot:

    def __init__(self):
        # Initialize the cache with a TTL of 2 days
        self.cache = cachetools.TTLCache(maxsize=1, ttl=2 * 24 * 60 * 60)  # 2 days in seconds

    def fetch_bing(self):
        # Check if the data is already cached
        if 'bing_data' in self.cache:
            return self.cache['bing_data']

        url = "https://www.bing.com/toolbox/bingbot.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            Bingbotrange = []
            for entry in data['prefixes']:
                ip_prefix = entry['ipv4Prefix']
                if ip_prefix:
                    Bingbotrange.append(ip_prefix)
            ip_networks = [ipaddress.ip_network(range) for range in Bingbotrange]

            # Store the result in the cache
            self.cache['bing_data'] = ip_networks
            return ip_networks
        else:
            print("Error")
            return []

    def is_bing(self, ip):
        ip_to_check = ipaddress.ip_address(ip)
        for network in self.fetch_bing():
            if ip_to_check in network:
                return True
        return False


if __name__ == '__main__':
    bingbot = Bingbot()
    print(bingbot.fetch_bing())

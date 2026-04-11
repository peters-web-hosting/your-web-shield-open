import ipaddress
import requests
import cachetools
from datetime import timedelta

from helpers.Database import Database


class KnownBots:

    def __init__(self):
        # Initialize the cache with a TTL of 2 days
        self.cache = cachetools.TTLCache(maxsize=1, ttl=2 * 24 * 60 * 60)  # 2 days in seconds

    def fetch_bots(self):
        # Check if the data is already cached
        if 'bots' in self.cache:
            return self.cache['bots']

        db = Database()

        # Fetch the bot data from the database
        bot_data = db.get_known_bots()
        if bot_data:

            # Convert the bot data to IP networks

            ip_networks = []
            for entry in bot_data:
                ip_prefix = entry.ip
                if ip_prefix:
                    ip_networks.append(ipaddress.ip_network(ip_prefix))

            # Store the result in the cache
            self.cache['bots'] = ip_networks
            return ip_networks
        else:
            print("Error fetching bot data from database.")
            return []

    def is_known(self, ip):
        ip_to_check = ipaddress.ip_address(ip)
        for network in self.fetch_bots():
            if ip_to_check in network:
                return True
        return False


if __name__ == '__main__':
    knownbots = KnownBots()
    print(knownbots.fetch_bots())

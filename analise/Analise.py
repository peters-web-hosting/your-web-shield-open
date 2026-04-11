from collections import defaultdict
from typing import List, Dict
from models.DataStore import DataStore
from models.Hits import Hits


class Analise:
    def __init__(self):
        pass

    def get_ip_counts(self, linked_list: List[Hits]) -> Dict[str, int]:
        count_map = defaultdict(int)
        for hit in linked_list:
            key = hit.iPaddress
            count_map[key] += 1
        return dict(count_map)

    def get_page_counts(self, linked_list: List[Hits]) -> Dict[str, int]:
        count_map = defaultdict(int)
        for hit in linked_list:
            key = hit.request
            count_map[key] += 1
        return dict(count_map)

    def get_protocol_counts(self, linked_list: List[Hits]) -> Dict[str, int]:
        count_map = defaultdict(int)
        for hit in linked_list:
            key = hit.protocol
            count_map[key] += 1
        return dict(count_map)

    def get_referer_counts(self, linked_list: List[Hits]) -> Dict[str, int]:
        count_map = defaultdict(int)
        for hit in linked_list:
            key = hit.referer
            count_map[key] += 1
        return dict(count_map)

    def get_time_counts(self, linked_list: List[Hits]) -> Dict[str, int]:
        count_map = defaultdict(int)
        for hit in linked_list:
            data_time = hit.date_time
            data = data_time.split(":")
            key = data[1] + ":" + data[2]
            count_map[key] += 1
        return dict(count_map)

    def get_total_data(self, hits: List[Hits]) -> int:
        total = sum(hit.size for hit in hits)
        return total

    def get_total_data_for_ip(self, linked_list: List[Hits], ip: str) -> int:
        total = sum(hit.size for hit in linked_list if hit.ip_addr == ip)
        return total

    def get_total_hits(self, hits: List[Hits]) -> int:
        return len(hits)

    def calculate_risk_factor(self, ip: str, data_store: DataStore, country_code: str) -> float:
        # Implement this method according to your requirements
        pass
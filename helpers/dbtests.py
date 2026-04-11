import unittest
from unittest.mock import patch

from helpers.Database import Database


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.database = Database()

    @patch("community.fetch_records")
    def test_known_bots(self, fetch_records):
        fetch_records.return_value = [
            {"record_type": "bot", "ip": "192.168.1.1", "botname": "BotName"},
        ]
        self.assertEqual(self.database.known_bots("192.168.1.1"), "BotName")

    @patch("community.fetch_records")
    def test_getRisk30Days(self, fetch_records):
        fetch_records.return_value = [
            {
                "record_type": "ip_log",
                "ip": "192.168.1.1",
                "risk": 3,
                "datereported": "2024-01-01T00:00:00",
            },
        ]
        self.assertEqual(self.database.getRisk30Days("192.168.1.1"), 3.0)

    @patch("community.fetch_records")
    def test_getRiskAllTime(self, fetch_records):
        fetch_records.return_value = [
            {"record_type": "ip_log", "ip": "192.168.1.1", "risk": 5},
        ]
        self.assertEqual(self.database.getRiskAllTime("192.168.1.1"), 5.0)

    @patch("community.submit")
    def test_updateRiskIp(self, submit):
        submit.return_value = True
        self.database.updateRiskIp("192.168.1.1", 10, "US", "AS1234")
        submit.assert_called_once()

    @patch("community.fetch_records")
    def test_getOcourances(self, fetch_records):
        fetch_records.return_value = [
            {"record_type": "ip_log", "ip": "192.168.1.1"},
            {"record_type": "ip_log", "ip": "192.168.1.1"},
        ]
        self.assertEqual(self.database.getOcourances("192.168.1.1"), 2)

    @patch("community.fetch_records")
    def test_countryRisk(self, fetch_records):
        fetch_records.return_value = [
            {"record_type": "ip_log", "country": "US", "risk": 4},
            {"record_type": "ip_log", "country": "US", "risk": 12},
        ]
        self.assertEqual(self.database.countryRisk("US"), 8.0)


if __name__ == "__main__":
    unittest.main()

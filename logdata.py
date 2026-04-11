import os
import sys
import logging
import threading

import concurrent
import time
from analise.BotAnalysis import BotAnalysis
from helpers.KnownBots import KnownBots
from helpers.Bing import Bingbot
from models.DataStore import DataStore
from helpers.Database import Database
from loggers.LogToDB import LogToDB
from helpers.Database import Database
from analise.Risk import Risk
from helpers.Reader import Reader
from helpers.IPFunctions import IPFunctions
from helpers.ASNRisk import ASNRisk
from helpers.CountryRisk import CountryRisk
from analise.Analise import Analise
from helpers.google import GoogleBot


class LogData:
    def __init__(self, specified_file=None):
        self.dataStore: DataStore = DataStore()
        self.database: Database = Database()
        self.clean_output()
        self.google_bot: GoogleBot = GoogleBot()
        self.bing_bot = Bingbot()
        self.known_bot = KnownBots()
        self.botAnalsis = BotAnalysis(train=True)
        self.database = Database()
        folder = "files"

        # Check if the folder exists
        if not os.path.exists(folder):
            os.makedirs(folder)

        start_time = time.time()

        if specified_file is None:
            listOfFiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        else:
            listOfFiles = [specified_file]

        for fileName in listOfFiles:
            filePath = os.path.join(folder, fileName)
            if os.path.isfile(filePath):
                self.dataStore = DataStore()
               
                if specified_file:
                    logger = LogToDB(fileName)

                self.dataStore.set_protocol_scores(self.database.setProtocolScores())
                self.dataStore.set_url_sources(self.database.setUrlScores())

                if specified_file is None:
                    self.dataStore.set_website(self.get_site_name(fileName))
                    print(self.dataStore.get_website())
                    logger.make_head()

                reader = Reader(self.dataStore, filePath)
                reader.read_file()

                self.process_logs()
                self.process_hits(logger)
                logger.add_date_range(reader.first_date, reader.last_date)
                logger.close()
                # self.update_risks()
                # self.database.close()
            elif specified_file:
                exit("Specified file not found.")

        print("Time taken to process logs: %s seconds" % (time.time() - start_time))

    def get_site_name(self, fileName):
        return fileName.rsplit('.', 1)[0]

    def update_risks(self):
        asnRisk: ASNRisk = ASNRisk()
        contry_risk: CountryRisk = CountryRisk()
        asnRisk.calculate_new_risk()
        contry_risk.update_risk()

    def clean_output(self):
        outputDir = self.dataStore.get_out_dir()
        # create output directory if it does not exist
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        for fileName in os.listdir(outputDir):
            filePath = os.path.join(outputDir, fileName)
            if os.path.isfile(filePath):
                os.remove(filePath)

    def process_logs(self):
        analise = Analise()
        hits = self.dataStore.get_hits()
        self.dataStore.set_occurrences_of_ip(analise.get_ip_counts(hits))

        # self.dataStore.setReferers(analise.getRefererCounts(hits))
        # self.dataStore.setProtcals(analise.getProtocalCounts(hits))
        # self.dataStore.setPages(analise.getPageCounts(hits))
        # analise.getTimeCounts(hits)

    def process_hits(self, loggerWithFile):
        logging.basicConfig(level=logging.ERROR, filename='errors.log',  format='%(asctime)s - %(levelname)s - %(message)s',
                            filemode='a')
        countMap = {}
        totalHits = len(self.dataStore.get_hits())
        nuber_done = 0

        # Get unique IP addresses to process
        unique_ips = set(hit.iPaddress for hit in self.dataStore.get_hits())
        print(f"Processing {len(unique_ips)} unique IP addresses")

        # Lock for thread-safe updates to shared data
        lock = threading.Lock()

        # Worker function to process a single IP address
        def process_ip(ip):
            try:
                calulator = Risk()
                functions = IPFunctions()
                risk = calulator.calulate_risks(ip, self.dataStore, functions.get_location(
                    ip), loggerWithFile, self.google_bot, self.bing_bot, self.known_bot, self.botAnalsis, self.database)

                with lock:
                    count = self.dataStore.get_occurrences_of_ip().get(ip, 0)
                    self.dataStore.add_risk(ip, risk)
                    countMap[ip] = risk
                    nonlocal nuber_done
                    nuber_done += count
                    left = totalHits - nuber_done
                    # print("ips left: " + str(left))

                return ip, risk
            except Exception as e:
                logging.error(f"Error processing IP {ip}: {str(e)}")
                return ip, None

        # Use ThreadPoolExecutor to process IPs in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # print(executor._max_workers)
            # Submit all tasks and process results as they complete
            futures = {executor.submit(process_ip, ip): ip for ip in unique_ips}
            for future in concurrent.futures.as_completed(futures):
                ip = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    logging.error(f"Exception for IP {ip}: {str(e)}")

        # Wait for all futures to complete
        concurrent.futures.wait(futures.keys())

        print("Processing completed.")


if __name__ == "__main__":
    # Get args
    args = sys.argv

    if len(args) > 1:
        logData = LogData(args[1])
    else:
        logData = LogData()

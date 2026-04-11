import os
from models.DataStore import DataStore
from models.Hits import Hits


class Reader:
    def __init__(self, data_store, path_to_file=None):
        self.data_store = data_store
        self.log_file = path_to_file
        self.errors = []

    def read_file(self):
        if not os.path.exists(self.log_file):
            print("File not found.")
            return

        self.first_date = None
        self.last_date = None
        hits_to_add = []
        d = open("user_agents.csv", 'a')
        with open(self.log_file, 'r') as file:
            for line in file:
                try:
                    data = line.split()
                    ip_address = data[0]
                    date_time = data[3][1:] + " " + data[4][:-1]
                    request_method = data[5][1:]
                    url = data[6]
                    request = request_method + url
                    http_version = data[7][:-1]
                    response_code = int(data[8])
                    response_size = int(data[9])

                    if len(data) > 10:
                        referer = data[10][1:-1]
                    if len(data) > 11:
                        user_agent = ' '.join(data[11:])[1:-1]

                    referer = referer if len(data) > 10 else "None"
                    user_agent = user_agent if len(data) > 11 else "None"

                    self.first_date = date_time if self.first_date is None else self.first_date
                    self.last_date = date_time
              #      d.write(user_agent + ", 0 \n")
                    h = Hits(ip_address, date_time, request,
                             http_version, response_code, response_size,
                             referer, user_agent)
                    self.data_store.add_hit(h)
                except Exception as e:
                    self.errors.append(e)
        d.close()
        if self.errors:
            print("Errors occurred during processing:")
            for error in self.errors:
                print(error)

    def set_file(self, path_to_file):
        self.log_file = path_to_file


if __name__ == "__main__":
    dataStore = DataStore()
    log_file_path = "yourwebshield.co.uk-ssl_log-Aug-2023.txt"
    reader = Reader(dataStore, log_file_path)
    reader.read_file()
    print(dataStore.get_hits())

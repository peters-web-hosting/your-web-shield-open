from helpers.Database import Database

class ASNRisk:
    
    def __init__(self):
        pass
      
    def calculate_new_risk(self):
        database = Database()
        asns = database.getASNs()
        for asn in asns:
            old_risk = database.getAsnRisk(asn)
            new_val = database.get_asn_risk_ip(asn)
            if new_val == 0.0:
             new_val = 1.1
            if old_risk == new_val and new_val > 10:
                new_val -= 10

            database.update_asn_risk(asn, new_val)
from dataclasses import dataclass

@dataclass
class Hits:
    iPaddress: str
    dateTime : str
    request: str
    httpVerson: str
    responseCode: int
    responseSize: int
    referer: str
    userAgent:str

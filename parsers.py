class BaseExchangeParser:
    def __init__(self, data):
        self.data = data

    def parse(self):
        return None


class BinanceParser(BaseExchangeParser):
    def parse(self):
        return [(i["symbol"], i["price"]) for i in self.data]


class OKXParser(BaseExchangeParser):
    def parse(self):
        return [(i["instId"].replace("-", ""), i["last"]) for i in self.data["data"]]


class BybitParser(BaseExchangeParser):
    def parse(self):
        return [(i["symbol"], i["lastPrice"]) for i in self.data["result"]["list"]]


CEX_CLASSES = {
    "binance": BinanceParser,
    "okx": OKXParser,
    "bybit": BybitParser,
}

from typing import List, Tuple, Dict, Any, Optional

class BaseExchangeParser:
    """Base class for all exchange parsers"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def parse(self) -> List[Tuple[str, str]]:
        """
        Parse exchange data into a list of (symbol, price) tuples
        
        Returns:
            List of tuples with format (symbol, price)
        """
        raise NotImplementedError("Subclasses must implement parse()")


class BinanceParser(BaseExchangeParser):
    """Parser for Binance exchange data"""
    
    def parse(self) -> List[Tuple[str, str]]:
        """
        Parse Binance ticker data into (symbol, price) pairs
        
        Returns:
            List of tuples with format (symbol, price)
        """
        try:
            return [(i["symbol"], i["price"]) for i in self.data]
        except (KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse Binance data: {e}")


class OKXParser(BaseExchangeParser):
    """Parser for OKX exchange data"""
    
    def parse(self) -> List[Tuple[str, str]]:
        """
        Parse OKX ticker data into (symbol, price) pairs
        
        Returns:
            List of tuples with format (symbol, price)
        """
        try:
            return [(i["instId"].replace("-", ""), i["last"]) for i in self.data["data"]]
        except (KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse OKX data: {e}")


class BybitParser(BaseExchangeParser):
    """Parser for Bybit exchange data"""
    
    def parse(self) -> List[Tuple[str, str]]:
        """
        Parse Bybit ticker data into (symbol, price) pairs
        
        Returns:
            List of tuples with format (symbol, price)
        """
        try:
            return [(i["symbol"], i["lastPrice"]) for i in self.data["result"]["list"]]
        except (KeyError, TypeError) as e:
            raise ValueError(f"Failed to parse Bybit data: {e}")


CEX_CLASSES = {
    "binance": BinanceParser,
    "okx": OKXParser,
    "bybit": BybitParser,
}

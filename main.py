import asyncio
import aiohttp
import json
import time
import aiofiles
import os
import logging
from dotenv import load_dotenv
from parsers import CEX_CLASSES
from decimal import Decimal
from check_bin import bin_pair_list

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("arbi_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arbi_bot")

# Config values
MIN_SPREAD = float(os.getenv("MIN_SPREAD", "2.0"))
MAX_SPREAD = float(os.getenv("MAX_SPREAD", "500.0"))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "5"))

async def get_and_write_orderbook(cex_name: str, link: str) -> str:
    """
    Fetch ticker data from exchange API and save to JSON file
    
    Args:
        cex_name: Exchange name (e.g., 'binance')
        link: API endpoint URL
        
    Returns:
        Filename where data was saved or None if request failed
    """
    filename = f"prices_{cex_name}.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link, timeout=10) as response:
                if response.status == 200:
                    request_response = await response.json()
                    async with aiofiles.open(filename, "w") as file:
                        await file.write(json.dumps(request_response, indent=4))
                    return filename
                else:
                    logger.error(f"Error fetching {cex_name}: HTTP {response.status}")
                    return None
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Network error with {cex_name}: {e}")
        return None
        

async def async_requests() -> list:
    """
    Fetch data from all exchanges asynchronously
    
    Returns:
        List of filenames where exchange data was saved
    """
    cex_list = [
        {
            "name": "binance",
            "link": "https://api.binance.com/api/v3/ticker/price"
            },
        {
            "name": "okx",
            "link": "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
            },
        {
            "name": "bybit",
            "link": "https://api.bybit.com/v5/market/tickers?category=spot"
            }
    ]

    tasks = []
    for cex in cex_list:
        tasks.append(get_and_write_orderbook(cex["name"], cex["link"]))
    
    filenames = await asyncio.gather(*tasks)
    # Filter out None values from failed requests
    filenames = [f for f in filenames if f]
    logger.info(f"Fetched data from: {filenames}")
    return filenames


async def unify_and_structurize(files_list: list) -> dict:
    """
    Unify data from different exchanges into a common format
    
    Args:
        files_list: List of filenames containing exchange data
        
    Returns:
        Dictionary with unified data structure where:
        - Keys are trading pairs (e.g., 'BTCUSDT')
        - Values are dictionaries of prices by exchange
    """
    unified_data = {}
    for file_name in files_list:
        cex_name = os.path.splitext(os.path.basename(file_name))[0].replace("prices_", "")

        try:
            async with aiofiles.open(file_name, "r") as file:
                raw = await file.read()
                cex_data = json.loads(raw)

            parser_class_call = CEX_CLASSES.get(cex_name)
            if not parser_class_call:
                logger.error(f"Error with calling {cex_name} parser!")
                continue

            parser = parser_class_call(cex_data)
            for ticker, price in parser.parse():
                if cex_name == "binance":
                    if ticker not in bin_pair_list:
                        continue
                unified_data.setdefault(ticker, {})[f"{cex_name}_price"] = price
        except Exception as e:
            logger.error(f"Error processing {file_name}: {e}")

    unified_data = {
        ticker: prices
        for ticker, prices in unified_data.items()
        if len(prices) > 1
    }

    async with aiofiles.open("arbi_main_file.json", "w") as file:
        await file.write(json.dumps(unified_data, indent=4))

    return unified_data


def arb_opportunity(data: dict, min_spread_threshold=MIN_SPREAD, max_spread_threshold=MAX_SPREAD) -> list:
    """
    Identify arbitrage opportunities in price data
    
    Args:
        data: Unified price data dictionary
        min_spread_threshold: Minimum spread percentage to consider (default from env var)
        max_spread_threshold: Maximum spread percentage to filter out anomalies (default from env var)
        
    Returns:
        List of dictionaries containing details of arbitrage opportunities
    """
    opportunities = []
    for ticker, prices in data.items():
        try:
            prices_filtered = {
                exchange: Decimal(str(price)) 
                for exchange, price in prices.items() 
                if Decimal(str(price)) != 0
            }

            if len(prices_filtered) < 2:
                continue

            min_exchange, min_price = min(prices_filtered.items(), key=lambda x: x[1])
            max_exchange, max_price = max(prices_filtered.items(), key=lambda x: x[1])
            spread = (Decimal(max_price) * 100 / Decimal(min_price)) - 100
            
            if min_spread_threshold < spread < max_spread_threshold:
                opportunity = {
                    "ticker": ticker,
                    "buy_cex": min_exchange,
                    "sell_cex": max_exchange,
                    "buy_price": str(min_price),
                    "sell_price": str(max_price),
                    "spread": str(spread)
                }
                opportunities.append(opportunity)
                logger.info(f"\n✅✅✅ Arbitrage opportunity found!!! ✅✅✅\n{ticker}")
                logger.info(f"Buy on {min_exchange}: {min_price}\nSell on {max_exchange}: {max_price}\nSpread: {spread:.2f}%")
        except (ZeroDivisionError, ValueError) as e:
            logger.warning(f"Error calculating spread for {ticker}: {e}")
    
    return opportunities


async def main():
    """
    Main execution loop for the arbitrage bot
    
    - Fetches price data from exchanges
    - Processes and unifies data
    - Identifies arbitrage opportunities
    - Handles errors and graceful shutdown
    """
    try:
        while True:
            time_all_1 = time.time()
            files_list = await async_requests()
            if not files_list:
                logger.warning("No valid data received from exchanges")
                await asyncio.sleep(REFRESH_INTERVAL)
                continue
                
            structured_data = await unify_and_structurize(files_list)
            opportunities = arb_opportunity(structured_data)
            
            time_all_2 = time.time()
            logger.info(f"\n(Latency: {time_all_2 - time_all_1:.4f} seconds)")
            
            await asyncio.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())

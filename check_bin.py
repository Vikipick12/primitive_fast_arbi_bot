import asyncio
import aiohttp
import json
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check_bin")

async def get_bin_data() -> List[str]:
    """
    Fetch active trading pairs from Binance API
    
    Returns:
        List of active trading pairs on Binance
    """
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    logger.error(f"Binance API error: HTTP {response.status}")
                    return []
                    
                data = await response.json()
                # Filter pairs where status is "TRADING" (active)
                bin_pair_list = [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == 'TRADING']
                logger.info(f"Fetched {len(bin_pair_list)} active trading pairs from Binance")
                return bin_pair_list
    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
        logger.error(f"Error fetching Binance pairs: {e}")
        return []

# Get Binance pairs list on module import
try:
    bin_pair_list = asyncio.run(get_bin_data())
    if not bin_pair_list:
        logger.warning("Failed to get Binance pairs, using empty list")
        bin_pair_list = []
except Exception as e:
    logger.error(f"Unexpected error getting Binance pairs: {e}")
    bin_pair_list = []
import asyncio
import aiohttp
import json

async def get_bin_data():      
    url = "https://api.binance.com/api/v3/exchangeInfo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            # Фільтруємо пари, де статус не "TRADING" (тобто не активні)
            bin_pair_list =  [symbol['symbol'] for symbol in data['symbols'] if symbol['status'] == 'TRADING']
            return bin_pair_list
        
bin_pair_list = asyncio.run(get_bin_data())
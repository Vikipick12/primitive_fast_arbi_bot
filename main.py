import asyncio
import aiohttp
import json
import time
import aiofiles
import os
from parsers import CEX_CLASSES
from decimal import Decimal
from check_bin import bin_pair_list
 

async def get_and_write_orderbook(cex_name, link):
    filename = f"prices_{cex_name}.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            request_response = await response.json()
            with open(filename, "w") as file:
                json.dump(request_response, file, indent=4)
            return filename
        

async def async_requests():
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
    print(filenames)
    return filenames


async def unify_and_structurize(files_list):
    unified_data = {}
    for file_name in files_list:
        cex_name = os.path.splitext(os.path.basename(file_name))[0].replace("prices_", "")

        async with aiofiles.open(file_name, "r") as file:
            raw = await file.read()
            cex_data = json.loads(raw)

        parser_class_call = CEX_CLASSES.get(cex_name)
        if not parser_class_call:
            print(f"Error with calling {cex_name} parser!")

        try:
            parser = parser_class_call(cex_data)
            for ticker, price in parser.parse():
                if cex_name == "binance":
                    if ticker not in bin_pair_list:
                        continue
                unified_data.setdefault(ticker, {})[f"{cex_name}_price"] = price
        except Exception as e:
            print(f"Some error with parsing, for more details read below\n{e}")

    unified_data = {
        ticker: prices
        for ticker, prices in unified_data.items()
        if len(prices) > 1
    }

    with open(f"arbi_main_file.json", "w") as file:
        json.dump(unified_data, file, indent=4)

    return unified_data


def arb_opportunity(data, min_spread_threshold=1, max_spread_threshold=1000):
    opportunities = []
    for ticker, prices in data.items():
        prices_filtered = {
            exchange: Decimal(str(price)) 
            for exchange, price in prices.items() 
            if Decimal(str(price)) != 0
        }

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
            print(f"\n✅✅✅ Arbitrage opportunity found!!! ✅✅✅\n{ticker}")
            print(f"Buy on {min_exchange}: {min_price}\nSell on {max_exchange}: {max_price}\nSpread: {spread:.2f}%")


async def main():
    while True:
        time_all_1 = time.time()
        files_list = await async_requests()
        structured_data = await unify_and_structurize(files_list)
        arb_opportunity(structured_data, min_spread_threshold=2, max_spread_threshold=500)
        time_all_2 = time.time()
        print(f"\n(Latency: {time_all_2 - time_all_1:.4f} seconds)")
        await asyncio.sleep(5)

asyncio.run(main())

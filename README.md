# 📈 Crypto Arbitrage Monitor
# primitive_fast_arbi_bot
Arbitrage bot with the usage of asynchronous methods of data fetching

This project monitors price discrepancies (arbitrage opportunities) across three centralized exchanges (**Binance**, **OKX**, and **Bybit**) using their public APIs. It fetches live spot prices (last price), normalizes data into a common format, and identifies profitable trading spreads.

---

## 🚀 Features

- ✅ Asynchronous fetching from Binance, OKX, and Bybit
- 🔄 Unified JSON structure with exchange-specific parsers
- 🧠 Arbitrage detection based on configurable price spread
- 📝 JSON logging for structured data and live opportunity printouts
- 🔧 Easy to expand to more exchanges or pair filters

---

## 📂 Project Structure

├── main.py # Main async loop for fetching and analysis
├── parsers.py # Exchange-specific parser classes (e.g. BinanceParser)
├── check_bin.py # List of Binance trading pairs to include (‼️‼️because Binance API call still returns many pairs that were delisted, this issue exists only with Binance)
├── prices_binance.json # Fetched raw data (auto-generated)
├── prices_okx.json  # Fetched raw data (auto-generated)
├── prices_bybit.json  # Fetched raw data (auto-generated)
├── arbi_main_file.json # Unified data ready for arbitrage analysis



---

## 🛠️ Requirements

- Python 3.9+
- Dependencies:
  - `aiohttp`
  - `aiofiles`

Install with:

```bash
pip install aiohttp aiofiles


▶️ Usage
Run the script:

python main.py

Output (every 5 seconds):

✅✅✅ Arbitrage opportunity found!!! ✅✅✅
ETHUSDT
Buy on binance_price: 1865.55
Sell on bybit_price: 1890.21
Spread: 1.32%

⚙️ Customization
Symbol Filtering: Binance symbols are filtered using bin_pair_list in check_bin.py

Spread Thresholds: Adjust min_spread_threshold and max_spread_threshold in arb_opportunity()

Add New Exchange: Implement a parser in parsers.py and add it to CEX_CLASSES

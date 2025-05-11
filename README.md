# 📈 Crypto Arbitrage Monitor
# primitive_fast_arbi_bot
Arbitrage bot with the usage of asynchronous methods of data fetching

‼️‼️ DISCLAIMER ‼️‼️ this bot is most likely useless in real-world trading due to the use of "last price" prices fetching method. Plus it does not include depth of market and possible token mismatching, the only token confirmation method is ticker name. 

This project monitors price discrepancies (arbitrage opportunities) across three centralized exchanges (**Binance**, **OKX**, and **Bybit**) using their public APIs. It fetches live spot prices (last price), normalizes data into a common format, and identifies profitable trading spreads.

---

## 🚀 Features

- ✅ Asynchronous fetching from Binance, OKX, and Bybit
- 🔄 Unified JSON structure with exchange-specific parsers
- 🧠 Arbitrage detection based on configurable price spread
- 📝 Structured logging to both file and console
- 🔧 Easy to expand to more exchanges or pair filters
- 🛡️ Robust error handling for API request failures
- ⚙️ Configurable via environment variables

---

## 📂 Project Structure

- `main.py` - Main async loop for fetching and analysis
- `parsers.py` - Exchange-specific parser classes with proper type hints
- `check_bin.py` - List of Binance trading pairs to include with error handling
- `prices_binance.json` - Fetched raw data (auto-generated)
- `prices_okx.json` - Fetched raw data (auto-generated)
- `prices_bybit.json` - Fetched raw data (auto-generated)
- `arbi_main_file.json` - Unified data ready for arbitrage analysis
- `arbi_bot.log` - Log file with detailed execution information

---

## 🛠️ Requirements

- Python 3.9+
- Dependencies:
  - `aiohttp`
  - `aiofiles`
  - `python-dotenv` (optional for env vars)

Install with:

```bash
pip install aiohttp aiofiles python-dotenv
```

## ▶️ Usage

Run the script:

```bash
python main.py
```

### Configuration

You can configure the bot using environment variables:

```bash
# Set minimum spread threshold to 1.5%
export MIN_SPREAD=1.5

# Set maximum spread threshold to 300%
export MAX_SPREAD=300

# Set refresh interval to 10 seconds
export REFRESH_INTERVAL=10

python main.py
```

## 🔍 Output

The bot logs to both the console and `arbi_bot.log` file:

```
✅✅✅ Arbitrage opportunity found!!! ✅✅✅
ETHUSDT
Buy on binance_price: 1865.55
Sell on bybit_price: 1890.21
Spread: 1.32%

(Latency: 0.8742 seconds)
```

## ⚙️ Customization

- **Symbol Filtering**: Binance symbols are filtered using `bin_pair_list` in `check_bin.py`
- **Spread Thresholds**: Adjust using environment variables or defaults in `main.py`
- **Add New Exchange**: Implement a parser in `parsers.py` and add it to `CEX_CLASSES`

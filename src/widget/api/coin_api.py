# QCryptoWidget/src/widget/api/coin_api.py

import requests
from typing import List, Dict, Optional, Tuple

CMC_API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
BINANCE_API_URL = "https://api.binance.com/api/v3/klines"

def get_current_prices(coin_codes: List[str], api_key: str) -> Optional[Dict]:
    """
    Fetches the current price and other data for a list of cryptocurrencies.
    """
    if not coin_codes:
        return {}
    parameters = {'symbol': ",".join(coin_codes), 'convert': 'USD'}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
    try:
        response = requests.get(CMC_API_URL, headers=headers, params=parameters, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['status']['error_code'] != 0:
            print(f"CoinMarketCap API Error: {data['status']['error_message']}")
            return None
            
        results = {}
        for code in coin_codes:
            if code in data['data']:
                coin_data = data['data'][code]
                quote_data = coin_data['quote']['USD']
                # **ENHANCEMENT**: Fetch slug and 7d change as well
                results[code] = {
                    'price': quote_data['price'],
                    'percent_change_24h': quote_data.get('percent_change_24h', 0),
                    'percent_change_7d': quote_data.get('percent_change_7d', 0),
                    'slug': coin_data.get('slug', '')
                }
        return results
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

def get_chart_data(coin_code: str, interval_days: int = 7) -> Optional[Tuple[List[float], List[float]]]:
    """
    (This function is no longer used by the UI but is kept for potential future use)
    Fetches historical price data for a single coin from Binance for charting.
    """
    symbol = f"{coin_code.upper()}USDT"
    params = {'symbol': symbol, 'interval': '1d', 'limit': interval_days}
    try:
        response = requests.get(BINANCE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        if isinstance(raw_data, dict) and 'code' in raw_data:
            print(f"Binance API Error for {symbol}: {raw_data.get('msg')}")
            return None
        if not isinstance(raw_data, list):
            print(f"Unexpected data format from Binance for {symbol}: {raw_data}")
            return None
        timestamps = []
        close_prices = []
        for kline in raw_data:
            if isinstance(kline, list) and len(kline) >= 5:
                try:
                    ts = int(kline[0]) / 1000
                    price = float(kline[4])
                    timestamps.append(ts)
                    close_prices.append(price)
                except (ValueError, TypeError, IndexError) as e:
                    print(f"Skipping malformed kline item: {kline}, error: {e}")
                    continue
        if not timestamps or not close_prices:
            print(f"No valid chart data points were processed for {symbol}.")
            return None
        return timestamps, close_prices
    except requests.exceptions.RequestException as e:
        print(f"Failed to get chart data for {coin_code}: {e}")
        return None
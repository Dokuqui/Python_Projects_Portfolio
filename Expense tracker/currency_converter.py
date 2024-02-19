# currency_converter.py

import requests
from requests.structures import CaseInsensitiveDict

def get_exchange_rate(base_currency, target_currency, api_key):
    url = "https://api.freecurrencyapi.com/v1/latest"
    headers = CaseInsensitiveDict()
    headers["apikey"] = api_key

    params = {"base_currency": base_currency}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if response.status_code == 200:
        try:
            exchange_rate = data["data"][target_currency]
            return exchange_rate
        except KeyError:
            print("KeyError: 'data' or target_currency not found in API response")
            return None
    else:
        print(f"Failed to fetch exchange rate: {response.status_code}")
        return None

def currency_converter(amount, exchange_rate):
    return amount * exchange_rate
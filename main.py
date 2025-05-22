
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GOLD_API_URL = "https://api.gold-api.com/price/XAU"
EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"

@app.get("/prices")
def get_prices():
    try:
        gold_res = requests.get(GOLD_API_URL, timeout=10)
        gold_res.raise_for_status()
        gold_data = gold_res.json()
        if "price" not in gold_data:
            return {"error": "Gold price not found in response."}
        xau_usd = float(gold_data["price"])

        fx_res = requests.get(EXCHANGE_RATE_URL, timeout=10)
        fx_res.raise_for_status()
        fx_data = fx_res.json()
        usd_to_myr = fx_data["rates"].get("MYR")
        if not usd_to_myr:
            return {"error": "MYR exchange rate not found."}

        xau_myr_oz = xau_usd * usd_to_myr
        base_price = round(xau_myr_oz / 31.1035, 2)

        multipliers = {
            "999.9": 0.972,
            "999": 0.933,
            "916": 0.857,
            "835": 0.781,
            "750": 0.678,
            "375": 0.283
        }

        calculated = {karat: round(base_price * ratio, 2) for karat, ratio in multipliers.items()}

        return {
            "base": base_price,
            "currency": "MYR",
            "prices": calculated
        }

    except Exception as e:
        return {"error": f"Failed to retrieve price: {str(e)}"}

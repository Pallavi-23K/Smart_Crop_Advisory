"""Simple market price helper for crop prices.

This is a stubbed dataset. In production you can replace the fetch_prices
function to call an external API (Agmarknet, local mandis, or a paid data source).
"""

from datetime import datetime

# sample prices INR per quintal (100kg). These are illustrative.
SAMPLE_PRICES = {
    "Wheat": 2250,
    "Maize": 1900,
    "Soybean": 4200,
    "Paddy (Rice)": 2000,
    "Sugarcane": 300,
    "Banana": 9000,
    "Millets": 2400,
    "Groundnut": 5200,
    "Cotton": 4200,
    "Mixed vegetables": 3500
}


def fetch_prices(crops=None):
    """Return a dict crop -> price for requested crops (or all if None).

    This function simulates a live fetch; add caching or API calls as needed.
    """
    if crops is None:
        crops = list(SAMPLE_PRICES.keys())
    out = {}
    for c in crops:
        # normalize common naming differences
        key = c if c in SAMPLE_PRICES else c.split(' (')[0]
        out[c] = SAMPLE_PRICES.get(key, SAMPLE_PRICES.get(c.split(' ')[0], 0))
    # include a recommended source for real market data (Agmarknet) for the UI
    return {
        "as_of": datetime.utcnow().isoformat() + 'Z',
        "prices": out,
        "source_name": "Agmarknet",
        "source_url": "https://agmarknet.gov.in"
    }


def normalize_price(price):
    """Return a normalized 0..1 score for price (higher is better).

    Simple linear normalization between 0..MaxPrice (set to 10000 INR/qtl).
    """
    try:
        p = float(price)
    except Exception:
        return 0.0
    max_price = 10000.0
    return max(0.0, min(1.0, p / max_price))

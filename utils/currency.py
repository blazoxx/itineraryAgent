import re
import time
from typing import Optional

import requests


# Static fallback rates (per 1 unit -> INR)
RATES_TO_INR = {
    "USD": 82.0,
    "EUR": 90.0,
    "GBP": 103.0,
    "AUD": 55.0,
    "CAD": 60.0,
    "AED": 22.5,
    "INR": 1.0,
    "JPY": 0.55,
}

SYMBOL_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "A$": "AUD",
    "C$": "CAD",
    "¥": "JPY",
    "د.إ": "AED",
    "₹": "INR",
}


def _normalize_currency(code: str) -> Optional[str]:
    if not code:
        return None
    code = code.upper().strip()
    # allow full names like rupee/rupees
    if code in ("RUPEE", "RUPEES", "INR"):
        return "INR"
    if code in ("DOLLAR", "DOLLARS", "USD"):
        return "USD"
    if code in ("EURO", "EUROS", "EUR"):
        return "EUR"
    if len(code) == 3:
        return code
    return None


def parse_currency_amount(text: str):
    """Find a currency amount in free text.

    Returns tuple (amount: float, currency_code: str) or (None, None)
    """
    if not text:
        return None, None

    # look for symbol first e.g. $1000 or ₹ 5,000
    symbol_regex = r"(\$|€|£|₹|¥|A\$|C\$|د\.إ)\s?([0-9,]+(?:\.[0-9]+)?)"
    m = re.search(symbol_regex, text)
    if m:
        sym = m.group(1)
        num = float(m.group(2).replace(",", ""))
        curr = SYMBOL_MAP.get(sym)
        return num, curr or "USD"

    # look for number followed by currency code or name (e.g. 1000 USD, 1,000 euros)
    code_regex = r"([0-9,]+(?:\.[0-9]+)?)\s*(usd|inr|eur|gbp|aud|cad|aed|jpy|dollars|rupees|euros|pounds)\b"
    m = re.search(code_regex, text, flags=re.IGNORECASE)
    if m:
        num = float(m.group(1).replace(",", ""))
        code = _normalize_currency(m.group(2))
        return num, code or "USD"

    # look for currency word then number (e.g., USD 1000)
    code_prefix_regex = r"\b(usd|inr|eur|gbp|aud|cad|aed|jpy)\b\s*([0-9,]+(?:\.[0-9]+)?)"
    m = re.search(code_prefix_regex, text, flags=re.IGNORECASE)
    if m:
        code = _normalize_currency(m.group(1))
        num = float(m.group(2).replace(",", ""))
        return num, code or "USD"

    return None, None


# Simple in-memory cache for fetched rates: {("USD","INR"): (rate, timestamp)}
_RATE_CACHE = {}
_CACHE_TTL = 60 * 60  # 1 hour


def _fetch_rate_from_api(from_code: str, to_code: str) -> Optional[float]:
    """Fetch conversion rate from exchangerate.host. Returns multiplier (1 from_code = X to_code)."""
    try:
        url = f"https://api.exchangerate.host/convert?from={from_code}&to={to_code}&amount=1"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data and data.get("info") and data["info"].get("rate"):
            return float(data["info"]["rate"])
    except Exception:
        return None


def _get_rate(from_code: str, to_code: str) -> float:
    key = (from_code.upper(), to_code.upper())
    now = time.time()
    cached = _RATE_CACHE.get(key)
    if cached:
        rate, ts = cached
        if now - ts < _CACHE_TTL:
            return rate

    rate = _fetch_rate_from_api(from_code, to_code)
    if rate:
        _RATE_CACHE[key] = (rate, now)
        return rate

    # fallback to static table when possible
    if to_code.upper() == "INR":
        static = RATES_TO_INR.get(from_code.upper())
        if static:
            return static

    # if no info, return 1.0 (no conversion)
    return 1.0


def convert_to_inr(amount: float, currency: str) -> Optional[float]:
    """Convert the given amount from `currency` to INR using live rates when available.

    Falls back to static rates if the API call fails.
    """
    if amount is None or currency is None:
        return None

    curr = currency.upper()
    if curr == "INR":
        return float(amount)

    rate = _get_rate(curr, "INR")
    return float(amount) * rate

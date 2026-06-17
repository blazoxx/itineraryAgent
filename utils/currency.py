import re


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


def _normalize_currency(code: str) -> str:
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
    # simple regex for symbol+number or number+currency
    symbol_regex = r"([\$€£₹¥C\$A\$د\.إ])\s?([0-9,]+(?:\.[0-9]+)?)"
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


def convert_to_inr(amount: float, currency: str) -> float:
    """Convert the given amount from `currency` to INR using static rates.

    This uses simple static rates and is meant as a best-effort conversion.
    """
    if amount is None or currency is None:
        return None

    currency = currency.upper()
    rate = RATES_TO_INR.get(currency)
    if rate is None:
        # unknown currency — assume amount is INR
        return float(amount)

    return float(amount) * rate

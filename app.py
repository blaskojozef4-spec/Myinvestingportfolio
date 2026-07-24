"""Flask portfolio tracker – cleaned up and mobile-friendly."""
from flask import Flask, render_template, request
import yfinance as yf

app = Flask(__name__)

# --- Portfolio ---------------------------------------------------------------
portfolio = [
    {'ticker': 'CNI',      'pocet': 10.02743,      'priemerna_cena': 116.63,   'mena': 'USD'},
    {'ticker': 'XLK',      'pocet': 11.06935,      'priemerna_cena': 141.68,   'mena': 'USD'},
    {'ticker': 'BRK-B',    'pocet': 21.09075,      'priemerna_cena': 452.79,   'mena': 'USD'},
    {'ticker': 'IWM',      'pocet': 32.10317,      'priemerna_cena': 202.48,   'mena': 'USD'},
    {'ticker': 'XLP',      'pocet': 55.87663,      'priemerna_cena': 76.29,    'mena': 'USD'},
    {'ticker': 'IVV',      'pocet': 65.79541,      'priemerna_cena': 581.74,   'mena': 'USD'},
    {'ticker': 'IEMG',     'pocet': 120.6516,      'priemerna_cena': 55.79,    'mena': 'USD'},
    {'ticker': 'CNDX.L',   'pocet': 2.99,          'priemerna_cena': 1231.72,  'mena': 'USD'},
    {'ticker': 'DTLA.L',   'pocet': 8275.63052713, 'priemerna_cena': 4.4404,   'mena': 'USD'},
    {'ticker': 'DTLA.L',   'pocet': 192.0405,      'priemerna_cena': 4.7417,   'mena': 'USD'},
    {'ticker': 'VWCE.DE',  'pocet': 145.38962679,  'priemerna_cena': 113.16,   'mena': 'EUR'},
    {'ticker': 'BRYN.DE',  'pocet': 24.3303,       'priemerna_cena': 410.32,   'mena': 'EUR'},
    {'ticker': 'VWCE.DE',  'pocet': 55.3168,       'priemerna_cena': 145.38,   'mena': 'EUR'},
    {'ticker': 'IS04.DE',  'pocet': 9918.0075,     'priemerna_cena': 2.9572,   'mena': 'EUR'},
    {'ticker': 'IB1T.DE',  'pocet': 203.2996,      'priemerna_cena': 5.6652,   'mena': 'EUR'},
    {'ticker': 'COIN',     'pocet': 1.59510962,    'priemerna_cena': 243.81,   'mena': 'USD'},
    {'ticker': 'TTD',      'pocet': 7.10030994,    'priemerna_cena': 24.40,    'mena': 'USD'},
    {'ticker': 'ADBE',     'pocet': 0.7145088,     'priemerna_cena': 250.98,   'mena': 'USD'},
    {'ticker': 'DUOL',     'pocet': 1.23418137,    'priemerna_cena': 120.89,   'mena': 'USD'},
    {'ticker': 'FOO.DE',   'pocet': 0.50823982,    'priemerna_cena': 181.02,   'mena': 'EUR'},
    {'ticker': 'MSF.DE',   'pocet': 1.6726,        'priemerna_cena': 334.97,   'mena': 'EUR'},
    {'ticker': 'RHM.DE',   'pocet': 0.1473,        'priemerna_cena': 1129.65,  'mena': 'EUR'},
    {'ticker': 'SAP.DE',   'pocet': 0.7952,        'priemerna_cena': 150.25,   'mena': 'EUR'},
    {'ticker': 'DSY.F',    'pocet': 3.2306,        'priemerna_cena': 18.10,    'mena': 'EUR'},
    {'ticker': 'CCC3.DE',  'pocet': 0.82453825,    'priemerna_cena': 60.64,    'mena': 'EUR'},
    {'ticker': 'NFC.DE',   'pocet': 3.3872,        'priemerna_cena': 63.584,   'mena': 'EUR'},
    {'ticker': 'TOITF',    'pocet': 1.79983054,    'priemerna_cena': 74.87,    'mena': 'USD'},
    {'ticker': 'BN',       'pocet': 2.9254095,     'priemerna_cena': 39.27,    'mena': 'USD'},
    {'ticker': 'SPGI',     'pocet': 0.17422506,    'priemerna_cena': 394.15,   'mena': 'USD'},
    {'ticker': 'AMZ.DE',   'pocet': 2.2503,        'priemerna_cena': 183.99,   'mena': 'EUR'},
    {'ticker': 'MDO.DE',   'pocet': 0.56668697,    'priemerna_cena': 239.50,   'mena': 'EUR'},
    {'ticker': 'DUT.F',    'pocet': 0.17652936,    'priemerna_cena': 356.88,   'mena': 'EUR'},
    {'ticker': 'SXRV.DE',  'pocet': 0.168,         'priemerna_cena': 1445.20,  'mena': 'EUR'},
    {'ticker': '2PP.DE',   'pocet': 12.1182,       'priemerna_cena': 49.52,    'mena': 'EUR'},
    {'ticker': 'PCE1.DE',  'pocet': 0.26459025,    'priemerna_cena': 132.28,  'mena': 'EUR'},
    {'ticker': 'FB2A.DE',  'pocet': 1.0073,        'priemerna_cena': 513.06,   'mena': 'EUR'},
    {'ticker': 'EGLN.L',   'pocet': 46.729,        'priemerna_cena': 71.9997,  'mena': 'EUR'},
    {'ticker': 'CSU.TO',   'pocet': 0.3048237,     'priemerna_cena': 3025.75,  'mena': 'CAD'},
]

CLOSED_PROFIT_USD = 546.23
TOTAL_DIVIDENDS_USD = 13384.75


def get_fx_rate(pair: str, fallback: float = 1.0) -> float:
    """Fetch an FX rate from Yahoo Finance, returning a fallback on failure."""
    try:
        rate = yf.Ticker(pair).info.get('regularMarketPrice')
        if rate:
            return float(rate)
    except Exception as e:
        print(f"FX fetch failed for {pair}: {e}")
    return fallback


def get_price(ticker: str, cache: dict):
    """Return current price for a ticker, using an in-memory cache."""
    if ticker in cache:
        return cache[ticker]
    info = yf.Ticker(ticker).info
    price = info.get('currentPrice') or info.get('regularMarketPrice')
    if price is None:
        raise ValueError("Price unavailable")
    cache[ticker] = price
    return price


@app.route('/')
def index():
    # Načítanie parametra triedenia podľa odkazu v HTML (?sort=...)
    sort_by = request.args.get('sort', 'ticker')

    eur_usd = get_fx_rate('EURUSD=X')
    cad_usd = get_fx_rate('CADUSD=X')
    usd_eur = 1 / eur_usd if eur_usd else 1.0

    price_cache: dict = {}
    rows = []
    total_value_usd = 0.0
    total_pl_usd = 0.0

    for i, pos in enumerate(portfolio, start=1):
        ticker = pos['ticker']
        try:
            price = get_price(ticker, price_cache)
            fx = {'USD': 1.0, 'EUR': eur_usd, 'CAD': cad_usd}[pos['mena']]

            avg_usd = pos['priemerna_cena'] * fx
            cur_usd = price * fx
            value_usd = cur_usd * pos['pocet']
            pl_usd = value_usd - (avg_usd * pos['pocet'])

            total_value_usd += value_usd
            total_pl_usd += pl_usd

            # Prepočty hodnôt pozície do EUR pre HTML zobrazenie
            value_eur = value_usd * usd_eur
            pl_eur = pl_usd * usd_eur
            
            # Výpočet percentuálneho zisku/straty pozície
            total_cost_usd = avg_usd * pos['pocet']
            pl_pct = (pl_usd / total_cost_usd * 100) if total_cost_usd else 0.0

        except Exception as e:
            print(f"Data error for {ticker}: {e}")
            price = value_eur = pl_eur = pl_pct = 0.0

        # Kľúče v slovníku sú pomenované presne podľa atribútov v HTML (p.ticker, p.value_eur...)
        rows.append({
            'index': i,
            'ticker': ticker,
            'mena': pos['mena'],
            'pocet': pos['pocet'],
            'priemerna_cena': pos['priemerna_cena'],
            'current_price': price,
            'value_eur': value_eur,
            'pl_eur': pl_eur,
            'pl_pct': pl_pct,
        })

    # Pomocná funkcia na bezpečné ošetrenie prípadných nečíselných hodnôt pri triedení
    def num(v):
        return v if isinstance(v, (int, float)) else float('-inf')

    # Logika triedenia napasovaná na navigačné menu z HTML
    if sort_by == 'ticker':
        rows.sort(key=lambda x: x['ticker'])
    elif sort_by == 'value':
        rows.sort(key=lambda x: num(x['value_eur']), reverse=True)
    elif sort_by == 'pl':
        rows.sort(key=lambda x: num(x['pl_eur']), reverse=True)
    elif sort_by == 'pl_pct':
        rows.sort(key=lambda x: num(x['pl_pct']), reverse=True)

    # Odosielanie premenných pomenovaných presne podľa Jinja2 tagov v šablóne
    return render_template(
        'portfolio_live.html',
        positions=rows,
        total_value_usd=total_value_usd,
        total_value_eur=total_value_usd * usd_eur,
        total_pl_usd=total_pl_usd,
        total_pl_eur=total_pl_usd * usd_eur,
        closed_profit_usd=CLOSED_PROFIT_USD,
        closed_profit_eur=CLOSED_PROFIT_USD * usd_eur,
        total_dividends_usd=TOTAL_DIVIDENDS_USD,
        total_dividends_eur=TOTAL_DIVIDENDS_USD * usd_eur,
        eur_usd_rate=eur_usd,
        cad_usd_rate=cad_usd,
        sort_by=sort_by,
    )


if __name__ == '__main__':
    app.run(debug=True)

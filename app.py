# app.py - Spustite tento subor v Pythone, aby ste videli aktualne ceny
from flask import Flask, render_template
import yfinance as yf
import requests

# Inicializacia Flask aplikacie
app = Flask(__name__)

# Tvoje portfolio - mozes ho upravit.
# Zmenili sme to na zoznam (list) slovnikov, aby sme mohli mat viac zaznamov
# pre ten isty ticker (napr. od roznych brokerov).
portfolio = [
    {'ticker': 'CNI', 'pocet': 10.02743, 'priemerna_cena': 116.63, 'mena': 'USD'},
    {'ticker': 'OXY', 'pocet': 36.78917, 'priemerna_cena': 55.55, 'mena': 'USD'},
    {'ticker': 'ASML', 'pocet': 1.62641, 'priemerna_cena': 757.25, 'mena': 'USD'},
    {'ticker': 'EQNR', 'pocet': 55.49544, 'priemerna_cena': 26.21, 'mena': 'USD'},
    {'ticker': 'BRK-B', 'pocet': 21.09075, 'priemerna_cena': 452.79, 'mena': 'USD'},
    {'ticker': 'IWM', 'pocet': 31.10993, 'priemerna_cena': 200.96, 'mena': 'USD'},
    {'ticker': 'XLP', 'pocet': 61.27045, 'priemerna_cena': 76.71, 'mena': 'USD'},
    {'ticker': 'IVV', 'pocet': 59.95522, 'priemerna_cena': 573.33, 'mena': 'USD'},
    {'ticker': 'IEMG', 'pocet': 112.3176, 'priemerna_cena': 54.77, 'mena': 'USD'},
    {'ticker': 'CNDX.L', 'pocet': 2.22, 'priemerna_cena': 1171, 'mena': 'USD'},
    {'ticker': 'DTLA.L', 'pocet': 8458.54391, 'priemerna_cena': 4.4404, 'mena': 'USD'},
    {'ticker': 'DTLA.L', 'pocet': 192.0405, 'priemerna_cena': 4.7417, 'mena': 'USD'},
    {'ticker': 'VWCE.DE', 'pocet': 144.200568, 'priemerna_cena': 112.58, 'mena': 'EUR'},
    {'ticker': 'BRYN.DE', 'pocet': 3.5001, 'priemerna_cena': 406.01, 'mena': 'EUR'},
    {'ticker': 'VWCE.DE', 'pocet': 1.3525, 'priemerna_cena': 130.13, 'mena': 'EUR'},
    {'ticker': 'IS04.DE', 'pocet': 14676.5577, 'priemerna_cena': 3.0319, 'mena': 'EUR'},
    {'ticker': 'DTLE.L', 'pocet': 9213, 'priemerna_cena': 3.0639, 'mena': 'EUR'},
]

def get_logo_url(ticker):
    """
    Pokusi sa ziskat URL loga z viacerych zdrojov.
    Vrati URL loga alebo None, ak logo nenajde.
    """
    # 1. Pokus z yfinance
    try:
        akcia = yf.Ticker(ticker)
        info = akcia.info
        logo_url = info.get('logo_url')
        if logo_url and requests.head(logo_url, timeout=5).status_code == 200:
            return logo_url
    except Exception as e:
        print(f"Nepodarilo sa ziskat logo z yfinance pre {ticker}: {e}")

    # 2. Nahradny pokus z verejneho API na loga (Clearbit)
    fallback_url = f"https://logo.clearbit.com/{ticker.lower()}.com"
    try:
        if requests.head(fallback_url, timeout=5).status_code == 200:
            return fallback_url
    except Exception as e:
        print(f"Nepodarilo sa ziskat logo z clearbit pre {ticker}: {e}")

    # 3. Posledna moznost pre tickery s bodkou
    if '.' in ticker:
        ticker_base = ticker.split('.')[0]
        fallback_url = f"https://logo.clearbit.com/{ticker_base.lower()}.com"
        try:
            if requests.head(fallback_url, timeout=5).status_code == 200:
                return fallback_url
        except Exception as e:
            pass

    return None

@app.route('/')
def index():
    """Hlavna stranka, ktora stiahne a zobrazi data z portfolia."""
    aktualne_udaje = []
    celkova_hodnota_portfolia = 0
    celkovy_zisk_strata = 0

    # Ziskame aktualny kurz EUR/USD
    try:
        eur_usd_ticker = yf.Ticker('EURUSD=X')
        eur_usd_rate = eur_usd_ticker.info['regularMarketPrice']
    except Exception as e:
        print(f"Chyba pri stahovani kurzu EUR/USD: {e}")
        eur_usd_rate = 1.0  # Pouzijeme 1, ak sa nepodari stiahnut

    # Cache pre aktualne ceny, aby sme nestahovali data pre ten isty ticker viackrat
    aktualne_ceny_cache = {}

    for data in portfolio:
        ticker = data['ticker']
        try:
            # Stiahnutie aktualnej ceny akcie - pouzijeme cache
            if ticker not in aktualne_ceny_cache:
                akcia = yf.Ticker(ticker)
                info = akcia.info
                aktualna_cena = info.get('currentPrice')
                
                if aktualna_cena is None:
                    aktualna_cena = info.get('regularMarketPrice')
                
                if aktualna_cena is None:
                    raise ValueError("Aktuálna cena nie je k dispozícii.")
                
                aktualne_ceny_cache[ticker] = aktualna_cena
            else:
                aktualna_cena = aktualne_ceny_cache[ticker]


            # Prepocet na USD ak je akcia v EUR
            priemerna_cena_usd = data['priemerna_cena']
            if data['mena'] == 'EUR':
                priemerna_cena_usd = data['priemerna_cena'] * eur_usd_rate
                aktualna_cena_usd = aktualna_cena * eur_usd_rate
            else:
                aktualna_cena_usd = aktualna_cena

            # Vypocet hodnot v USD
            celkova_hodnota = aktualna_cena_usd * data['pocet']
            zisk_strata = (aktualna_cena_usd - priemerna_cena_usd) * data['pocet']
            
            if isinstance(celkova_hodnota, (int, float)):
                celkova_hodnota_portfolia += celkova_hodnota
            
            if isinstance(zisk_strata, (int, float)):
                celkovy_zisk_strata += zisk_strata

            logo_url = get_logo_url(ticker) # Stále ponecháme, ak by sa načítalo z yfinance

        except Exception as e:
            print(f"Chyba pri stahovani dat pre {ticker}: {e}")
            aktualna_cena = 'Dáta nedostupné'
            celkova_hodnota = 'Dáta nedostupné'
            zisk_strata = 'Dáta nedostupné'
            logo_url = None
        
        # Zostavenie udajov pre zobrazenie
        aktualne_udaje.append({
            'ticker': ticker,
            'pocet': data['pocet'],
            'priemerna_cena': data['priemerna_cena'],
            'aktualna_cena': aktualna_cena,
            'celkova_hodnota': celkova_hodnota,
            'zisk_strata': zisk_strata,
            'logo_url': logo_url
        })
    
    # Vypocet celkovej hodnoty portfolia v EUR
    celkova_hodnota_portfolia_eur = celkova_hodnota_portfolia / eur_usd_rate

    return render_template(
        'portfolio_live.html', 
        udaje=aktualne_udaje, 
        celkova_hodnota_portfolia=celkova_hodnota_portfolia, 
        celkovy_zisk_strata=celkovy_zisk_strata,
        celkova_hodnota_portfolia_eur=celkova_hodnota_portfolia_eur
    )

if __name__ == '__main__':
    app.run(debug=True)
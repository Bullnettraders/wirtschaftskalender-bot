import requests
from datetime import datetime, timedelta
import os

FMP_API_KEY = os.getenv("FMP_API_KEY")  # Dein API Key aus Umgebungsvariablen

def get_earnings_calendar(for_tomorrow=False):
    if not FMP_API_KEY:
        print("❌ Kein API Key für FinancialModelingPrep gefunden!")
        return []

    today = datetime.now()
    target_date = today + timedelta(days=1) if for_tomorrow else today
    from_date = target_date.strftime("%Y-%m-%d")
    to_date = from_date

    url = f"https://financialmodelingprep.com/api/v3/earning_calendar?from={from_date}&to={to_date}&apikey={FMP_API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fehler: Status Code {response.status_code}")
            return []

        earnings_data = response.json()
        events = []

        for item in earnings_data:
            company = item.get("company", "Unbekannt")
            symbol = item.get("symbol", "???")
            eps_estimate = item.get("epsEstimated", "Keine Angabe")
            revenue_estimate = item.get("revenueEstimated", "Keine Angabe")
            time = item.get("time", "Zeit unbekannt")

            events.append({
                "company": company,
                "symbol": symbol,
                "eps_estimate": eps_estimate,
                "revenue_estimate": revenue_estimate,
                "report_time": time
            })

        print(f"🟢 Gefundene Earnings: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Earnings: {e}")
        return []

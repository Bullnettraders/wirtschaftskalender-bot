import requests
import os
from datetime import datetime, timedelta

FMP_API_KEY = os.getenv("FMP_API_KEY")

def get_earnings_calendar(for_tomorrow=False):
    if not FMP_API_KEY:
        print("❌ Kein API Key für FMP gefunden!")
        return []

    today = datetime.now()
    target_date = today + timedelta(days=1) if for_tomorrow else today
    date_str = target_date.strftime("%Y-%m-%d")

    url = f"https://financialmodelingprep.com/api/v3/earning_calendar?from={date_str}&to={date_str}&apikey={FMP_API_KEY}"

    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Fehler: Status {response.status_code}")
            return []

        earnings = response.json()
        results = []
        for entry in earnings:
            results.append({
                "company": entry.get("company", ""),
                "symbol": entry.get("symbol", ""),
                "eps_estimate": entry.get("epsEstimated", "n/a"),
                "revenue_estimate": entry.get("revenueEstimated", "n/a"),
                "report_time": entry.get("time", "—")
            })

        print(f"🟢 Gefundene Earnings: {len(results)}")
        return results

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Earnings: {e}")
        return []
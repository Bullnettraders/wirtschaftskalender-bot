import requests
from datetime import datetime
import os

def get_te_calendar():
    api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    if not api_key:
        print("❌ Fehler: Kein API Key gefunden!")
        return []

    url = f"https://api.tradingeconomics.com/calendar?c={api_key}&f=json"

    try:
        response = requests.get(url)
        print("🔵 API Antwort von TradingEconomics:")
        print(response.text)

        if response.status_code != 200:
            print(f"❌ API Fehler: Status Code {response.status_code}")
            return []

        data = response.json()

        if isinstance(data, dict) and 'error' in data:
            print(f"❌ API Fehler: {data['error']}")
            return []

        events = []
        today = datetime.now().strftime("%Y-%m-%d")

        for event in data:
            if not event.get('Country') or not event.get('DateTime'):
                continue

            event_country = event['Country'].lower()
            event_date = event['DateTime'].split('T')[0]

            if event_country in ["germany", "united states", "euro area"] and event_date == today:
                time = event['DateTime'].split('T')[1][:5]
                events.append({
                    "country": event_country,
                    "time": time,
                    "title": event.get('Event', 'Keine Beschreibung')
                })

        if not events:
            print("⚠️ Heute keine Events gefunden für Deutschland, Euro Area oder USA.")

        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler bei API Anfrage: {e}")
        return []

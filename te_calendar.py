import requests
from datetime import datetime
import os

def get_te_calendar():
    api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    url = f"https://api.tradingeconomics.com/calendar?c={api_key}&f=json"

    response = requests.get(url)
    if response.status_code != 200:
        print("Fehler beim Abrufen der Daten von TradingEconomics")
        return []

    data = response.json()
    events = []

    today = datetime.now().strftime("%Y-%m-%d")

    for event in data:
        if not event.get('Country') or not event.get('DateTime'):
            continue
        
        event_country = event['Country'].lower()
        event_date = event['DateTime'].split('T')[0]

        if event_country in ["germany", "united states"] and event_date == today:
            time = event['DateTime'].split('T')[1][:5]
            events.append({
                "country": "de" if event_country == "germany" else "us",
                "time": time,
                "title": event.get('Event', 'Keine Beschreibung')
            })

    return events

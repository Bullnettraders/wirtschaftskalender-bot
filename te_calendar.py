import requests
from datetime import datetime
import os

def get_te_calendar():
    api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    if not api_key:
        print("API Key fehlt!")
        return []

    url = f"https://api.tradingeconomics.com/calendar?c={api_key}&f=json"

    response = requests.get(url)
    print(response.text)  # NEU: Zeigt im Render-Log die Antwort an

    if response.status_code != 200:
        print("Fehler beim Abrufen der Daten:", response.status_code)
        return []

    data = response.json()
    events = []

    today = datetime.now().strftime("%Y-%m-%d")

    for event in data:
        if not event.get('Country') or not event.get('DateTime'):
            continue
        
        event_country = event['Country'].lower()
        event_date = event['DateTime'].split('T')[0]

        # Filter: Nur Deutschland und USA
        if event_country in ["germany", "united states"] and event_date == today:
            time = event['DateTime'].split('T')[1][:5]
            events.append({
                "country": "de" if event_country == "germany" else "us",
                "time": time,
                "title": event.get('Event', 'Keine Beschreibung')
            })

    return events

import requests
from datetime import datetime, timedelta

API_KEY = "EGgZNP6SNfwErHX2ofuNTjCtnCz8uBOZ"  # Dein echter API-Key

def get_fmp_calendar():
    today = datetime.utcnow().date()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"https://financialmodelingprep.com/api/v4/economic_calendar?from={yesterday}&to={tomorrow}&apikey={API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"🔵 Anfrage URL: {url}")
        print(f"🟡 Antwort Status: {response.status_code}")
        print(f"🟣 Antwort Inhalt: {response.text[:500]}...")  # Nur Ausschnitt

        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status Code {response.status_code}")
            return []

        data = response.json()

        events = []
        for event in data:
            event_date = event.get("date", "")
            event_time = event.get("time", "00:00")
            country = event.get("country", "")
            title = event.get("event", "")
            importance = event.get("importance", 1)

            # Nur Events, die für HEUTE gedacht sind
            if event_date == today.strftime("%Y-%m-%d") and country in ["US", "DE"]:
                events.append({
                    "country": country,
                    "time": event_time,
                    "title": title,
                    "importance": importance
                })

        print(f"🟢 Gefundene Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen: {e}")
        return []

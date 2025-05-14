import requests
from datetime import datetime

API_KEY = "EGgZNP6SNfwErHX2ofuNTjCtnCz8uBOZ"

def get_fmp_calendar():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://financialmodelingprep.com/api/v4/economic_calendar?from={today}&to={today}&apikey={API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"🔵 Anfrage URL: {url}")
        print(f"🟡 Antwort Status: {response.status_code}")
        print(f"🟣 Antwort Inhalt: {response.text[:500]}...")  # Nur die ersten 500 Zeichen anzeigen

        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status Code {response.status_code}")
            return []

        data = response.json()

        events = []
        for event in data:
            country = event.get("country", "")
            event_date = event.get("date", "")
            time = event.get("time", "00:00")
            title = event.get("event", "")
            importance = event.get("importance", 1)

            if country in ["US", "DE"] and event_date == today:
                events.append({
                    "country": country,
                    "time": time,
                    "title": title,
                    "importance": importance
                })

        print(f"🟢 Gefundene Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen: {e}")
        return []

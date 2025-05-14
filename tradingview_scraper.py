import requests
from datetime import datetime, timezone

def get_tradingview_calendar():
    url = "https://economic-calendar.tradingview.com/events"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status Code {response.status_code}")
            return []

        data = response.json()

        events = []
        today = datetime.now(timezone.utc).date()

        for event in data.get("events", []):
            event_timestamp = event.get("timestamp")
            event_country = event.get("country", "").upper()
            event_title = event.get("event", "Unbekanntes Event")

            if not event_timestamp or not event_country:
                continue

            event_time = datetime.fromtimestamp(event_timestamp, tz=timezone.utc)
            event_date = event_time.date()

            # Länder-Filter: Deutschland (DE), USA (US)
            if event_date == today and event_country in ["DE", "US"]:
                events.append({
                    "country": event_country,
                    "time": event_time.strftime("%H:%M"),
                    "title": event_title
                })

        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen: {e}")
        return []

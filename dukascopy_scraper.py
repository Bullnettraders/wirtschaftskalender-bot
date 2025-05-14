import requests
from datetime import datetime

def get_dukascopy_calendar():
    # Heute Datum holen
    today = datetime.utcnow()
    year = today.year
    month = today.month
    day = today.day

    url = f"https://www.dukascopy.com/datafeed/economic_calendar_calendar_en/{year}/{month:02}/{day:02}/00/00/0.json"
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
        for event in data:
            country = event.get("country", "").lower()
            date = event.get("date", "")
            time = event.get("time", "")
            title = event.get("event", "")

            # Nur Deutschland und USA Events nehmen
            if country in ["germany", "united states"]:
                events.append({
                    "country": country,
                    "date": date,
                    "time": time,
                    "title": title
                })

        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen: {e}")
        return []

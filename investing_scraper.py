import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_investing_calendar():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }

    session = requests.Session()
    session.headers.update(headers)
    
    response = session.get(url)

    if response.status_code != 200:
        print(f"❌ Fehler beim Abrufen der Seite: Status Code {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    events = []

    # Suche nach Event-Elementen
    rows = soup.select('tr.js-event-item')
    if not rows:
        print("❌ Keine Events gefunden - Struktur der Seite evtl. geändert.")
        return []

    today = datetime.now().strftime("%Y-%m-%d")

    for row in rows:
        try:
            # hole Event-Datum
            date_timestamp = row.get("data-event-datetime")
            if not date_timestamp:
                continue

            event_time = datetime.utcfromtimestamp(int(date_timestamp)).strftime("%H:%M")
            event_date = datetime.utcfromtimestamp(int(date_timestamp)).strftime("%Y-%m-%d")

            # hole Land
            country = row.get("data-country", "").lower()

            # hole Event-Name
            event_title_cell = row.find("td", class_="event")
            if event_title_cell:
                event_title = event_title_cell.get_text(strip=True)
            else:
                event_title = "Kein Titel"

            # Nur Events für heute und Länder DE/US
            if event_date == today and country in ["de", "us"]:
                events.append({
                    "country": country,
                    "time": event_time,
                    "title": event_title
                })

        except Exception as e:
            print(f"⚠️ Fehler beim Verarbeiten eines Events: {e}")
            continue

    if not events:
        print("⚠️ Heute keine Events gefunden für Deutschland oder USA.")

    return events

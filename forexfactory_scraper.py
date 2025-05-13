import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_forex_calendar():
    url = "https://www.forexfactory.com/calendar"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    table = soup.find("table", id="calendar__table")
    if not table:
        return events

    rows = table.find_all("tr", class_="calendar__row")
    today = datetime.now().strftime("%b %d, %Y")

    for row in rows:
        try:
            country_cell = row.find("td", class_="calendar__country")
            if not country_cell:
                continue
            country_code = country_cell.get_text(strip=True).lower()

            # Nur DE und US zulassen
            if country_code not in ["de", "us"]:
                continue

            time_cell = row.find("td", class_="calendar__time")
            event_time = time_cell.get_text(strip=True)
            event_name = row.find("td", class_="calendar__event").get_text(strip=True)

            events.append({
                "country": country_code,
                "time": event_time,
                "title": event_name
            })

        except Exception as e:
            print(f"Fehler beim Parsen einer Zeile: {e}")
            continue

    return events

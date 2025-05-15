import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://m.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Fehler beim Abrufen: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        events = []

        today = datetime.now()
        target_date = today + timedelta(days=1) if for_tomorrow else today
        date_str = target_date.strftime("%d.%m.%Y")

        table = soup.find("table", {"class": "genTbl"})
        if not table:
            print("Tabelle nicht gefunden.")
            return []

        rows = table.find_all("tr")
        for row in rows:
            try:
                country_img = row.find("td", {"class": "flagCur"})
                country = country_img.find("span").get("title").lower() if country_img else ""

                time_col = row.find("td", {"class": "first left time"})
                event_time = time_col.text.strip() if time_col else "—"

                event_col = row.find("td", {"class": "event"})
                event_name = event_col.text.strip() if event_col else ""

                importance_col = row.find("td", {"class": "left textNum sentiment noWrap"})
                importance = 0
                if importance_col:
                    importance = len(importance_col.find_all("i", {"class": "grayFullBullishIcon"}))

                actual_col = row.find("td", {"class": "act"})
                forecast_col = row.find("td", {"class": "fore"})
                previous_col = row.find("td", {"class": "prev"})

                actual = actual_col.text.strip() if actual_col else ""
                forecast = forecast_col.text.strip() if forecast_col else ""
                previous = previous_col.text.strip() if previous_col else ""

                date_col = row.find("td", {"class": "theDay"})
                event_date = date_col.text.strip() if date_col else today.strftime("%d.%m.%Y")

                if importance >= 2 and country in ["germany", "united states"] and event_date == date_str:
                    events.append({
                        "country": country,
                        "time": event_time,
                        "title": event_name,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous,
                        "importance": importance
                    })

            except Exception as e:
                print(f"Fehler beim Parsen einer Zeile: {e}")
                continue

        print(f"Gefundene wichtige Events: {len(events)}")
        return events

    except Exception as e:
        print(f"Fehler beim Scraping: {e}")
        return []
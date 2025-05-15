import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://m.investing.com/economic-calendar/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    events = []

    today = datetime.now()
    target_date = today + timedelta(days=1) if for_tomorrow else today
    date_str = target_date.strftime("%d.%m.%Y")

    table = soup.find("table", {"class": "genTbl"})
    rows = table.find_all("tr") if table else []

    for row in rows:
        country_td = row.find("td", {"class": "flagCur"})
        country = country_td.find("span")["title"].lower() if country_td else ""

        time_td = row.find("td", {"class": "first left time"})
        event_time = time_td.text.strip() if time_td else "—"

        event_td = row.find("td", {"class": "event"})
        event_name = event_td.text.strip() if event_td else ""

        importance_td = row.find("td", {"class": "left textNum sentiment noWrap"})
        importance = len(importance_td.find_all("i", class_="grayFullBullishIcon")) if importance_td else 0

        actual_td = row.find("td", {"class": "act"})
        forecast_td = row.find("td", {"class": "fore"})
        previous_td = row.find("td", {"class": "prev"})

        actual = actual_td.text.strip() if actual_td else ""
        forecast = forecast_td.text.strip() if forecast_td else ""
        previous = previous_td.text.strip() if previous_td else ""

        date_td = row.find("td", {"class": "theDay"})
        event_date = date_td.text.strip() if date_td else date_str

        if importance >= 2 and country in ["germany", "united states"] and event_date == date_str:
            events.append({
                "country": country,
                "time": event_time,
                "title": event_name,
                "actual": actual,
                "forecast": forecast,
                "previous": previous,
            })
    return events
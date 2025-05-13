import discord
from discord.ext import commands, tasks
import datetime
import os
from te_calendar import get_te_calendar  # Holt Events

# Intents setzen (wichtige Berechtigungen)
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    economic_calendar_loop.start()

# Alle 30 Minuten Wirtschaftskalender prüfen
@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_te_calendar()

        country_names = {
            "germany": "🇩🇪 Deutschland",
            "united states": "🇺🇸 USA",
            "euro area": "🇪🇺 Eurozone"
        }

        if not events:
            await channel.send(f"📅 Keine Wirtschaftstermine gefunden ({now.strftime('%d.%m.%Y')})")
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        countries = ["germany", "euro area", "united states"]

        for country in countries:
            country_events = [e for e in events if e['country'] == country]
            if country_events:
                message += f"{country_names[country]}:\n"
                for event in country_events:
                    message += f"- {event['time']} Uhr: {event['title']}\n"
            else:
                message += f"Keine Termine für {country_names[country]} heute.\n"
            message += "\n"

        await channel.send(message)
    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 8-22 Uhr)")

# MANUELLER Befehl: !update
@bot.command()
async def update(ctx):
    """Manuelles Abrufen der aktuellen Wirtschaftstermine"""
    events = get_te_calendar()

    country_names = {
        "germany": "🇩🇪 Deutschland",
        "united states": "🇺🇸 USA",
        "euro area": "🇪🇺 Eurozone"
    }

    if not events:
        await ctx.send(f"📅 Keine Wirtschaftstermine gefunden ({datetime.datetime.now().strftime('%d.%m.%Y')})")
        return

    message = f"📅 **Manuelles Wirtschaftskalender Update {datetime.datetime.now().strftime('%H:%M')} Uhr**\n\n"

    countries = ["germany", "euro area", "united states"]

    for country in countries:
        country_events = [e for e in events if e['country'] == country]
        if country_events:
            message += f"{country_names[country]}:\n"
            for event in country_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += f"Keine Termine für {country_names[country]} heute.\n"
        message += "\n"

    await ctx.send(message)

bot.run(DISCORD_TOKEN)
import requests
from datetime import datetime
import os

def get_te_calendar():
    api_key = os.getenv("TRADING_ECONOMICS_API_KEY")
    if not api_key:
        print("❌ Fehler: Kein API Key gefunden!")
        return []

    url = f"https://api.tradingeconomics.com/calendar?c={api_key}&f=json"

    try:
        response = requests.get(url)
        print("🔵 API Antwort von TradingEconomics:")
        print(response.text)  # Damit du siehst, was zurückkommt

        if response.status_code != 200:
            print(f"❌ API Fehler: Status Code {response.status_code}")
            return []

        data = response.json()

        if isinstance(data, dict) and 'error' in data:
            print(f"❌ API Fehler: {data['error']}")
            return []

        events = []
        today = datetime.now().strftime("%Y-%m-%d")

        for event in data:
            if not event.get('Country') or not event.get('DateTime'):
                continue
            
            event_country = event['Country'].lower()
            event_date = event['DateTime'].split('T')[0]

            if event_country in

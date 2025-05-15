import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    economic_calendar_loop.start()

@tasks.loop(minutes=15)
async def economic_calendar_loop():
    now = datetime.datetime.now()

    if now.weekday() >= 5:  # Samstag oder Sonntag → keine Abfrage
        return

    if not (7 <= now.hour <= 22):  # Nur zwischen 7 und 22 Uhr
        return

    events = get_investing_calendar()

    if not events:
        print(f"🔵 Abfrage um {now.strftime('%H:%M')}: Keine wichtigen Termine gefunden.")
        return

    channel = bot.get_channel(CHANNEL_ID)
    print(f"🔵 Abfrage um {now.strftime('%H:%M')}")
    
    for event in events:
        time = event['time']
        title = event['title']
        actual = event['actual']
        forecast = event['forecast']
        previous = event['previous']

        # Richtungspfeil bestimmen (nur wenn actual/forecast vorhanden)
        if actual and forecast:
            try:
                actual_value = float(actual.replace('%', '').replace(',', '.'))
                forecast_value = float(forecast.replace('%', '').replace(',', '.'))

                if actual_value > forecast_value:
                    arrow = "🔺"
                elif actual_value < forecast_value:
                    arrow = "🔻"
                else:
                    arrow = "➖"
            except ValueError:
                arrow = "➖"
        else:
            arrow = "➖"

        msg = (
            f"**{time} Uhr** – {title}\n"
            f"Aktuell: {actual} {arrow}\n"
            f"Erwartet: {forecast}\n"
            f"Vorher: {previous}"
        )

        await channel.send(msg)

@bot.command(name="kalender")
async def kalender(ctx):
    now = datetime.datetime.now()

    events = get_investing_calendar(for_tomorrow=False)

    if not events:
        await ctx.send(f"🔔 Heute ({now.strftime('%d.%m.%Y')}) gibt es keine wichtigen Termine!")
        return

    message = f"📅 **Wirtschaftskalender Heute** ({now.strftime
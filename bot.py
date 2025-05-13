import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    economic_calendar_loop.start()

@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_investing_calendar()

        if not events:
            await channel.send(f"📅 Keine Wirtschaftstermine gefunden ({now.strftime('%d.%m.%Y')})")
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        de_events = [e for e in events if e['country'] == 'de']
        us_events = [e for e in events if e['country'] == 'us']

        if de_events:
            message += "🇩🇪 **Deutschland**:\n"
            for event in de_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += "Keine Termine für Deutschland heute.\n"

        message += "\n"

        if us_events:
            message += "🇺🇸 **USA**:\n"
            for event in us_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += "Keine Termine für USA heute.\n"

        await channel.send(message)
    else:
        print(f"Ignoriert um {now.strftime('%H:%M')} (außerhalb 8-22 Uhr)")

bot.run(DISCORD_TOKEN)

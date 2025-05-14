import discord
from discord.ext import commands, tasks
import datetime
import os
from dukascopy_scraper import get_dukascopy_calendar

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    if not economic_calendar_loop.is_running():
        print(f"✅ Bot ist online als {bot.user}")
        economic_calendar_loop.start()

@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()  # Montag=0, Sonntag=6

    if 0 <= weekday <= 4 and (now.hour > 7 or (now.hour == 7 and now.minute >= 30)) and now.hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_dukascopy_calendar()

        country_names = {
            "germany": "🇩🇪 Deutschland",
            "united states": "🇺🇸 USA"
        }

        if not events:
            message = (
                f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"
                "🔔 Heute keine wichtigen Termine für Deutschland 🇩🇪 oder USA 🇺🇸.\n"
                "Genießt euren Tag! 😎"
            )
            await channel.send(message)
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        for country in ["germany", "united states"]:
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
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 7:30–22:00 oder Wochenende)")

@bot.command()
async def update(ctx):
    """Manuelles Abrufen der aktuellen Wirtschaftstermine"""
    events = get_dukascopy_calendar()

    country_names = {
        "germany": "🇩🇪 Deutschland",
        "united states": "🇺🇸 USA"
    }

    if not events:
        await ctx.send(f"📅 Heute keine Wirtschaftstermine für Deutschland 🇩🇪 oder USA 🇺🇸.")
        return

    message = f"📅 **Manuelles Wirtschaftskalender Update {datetime.datetime.now().strftime('%H:%M')} Uhr**\n\n"

    for country in ["germany", "united states"]:
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

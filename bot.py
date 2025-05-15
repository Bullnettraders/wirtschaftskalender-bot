import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import os
from investing_scraper import get_investing_calendar, posted_events

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID_CALENDAR"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    daily_summary.start()
    live_updates.start()

# TÄGLICHE ÜBERSICHT um 22:00 Uhr
@tasks.loop(time=time(hour=22, minute=0))
async def daily_summary():
    channel = bot.get_channel(CHANNEL_ID)
    events = get_investing_calendar(for_tomorrow=True)

    embed = discord.Embed(
        title="📅 Wirtschaftskalender Morgen",
        description=f"📅 {(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}",
        color=0x3498db
    )

    germany = [e for e in events if e['country'] == "germany"]
    usa = [e for e in events if e['country'] == "united states"]

    if germany:
        text = "\n".join([f"🕐 {e['time']} – {e['title']}" for e in germany])
        embed.add_field(name="🇩🇪 Deutschland", value=text, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine.", inline=False)

    if usa:
        text = "\n".join([f"🕐 {e['time']} – {e['title']}" for e in usa])
        embed.add_field(name="🇺🇸 USA", value=text, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine.", inline=False)

    await channel.send(embed=embed)

# LIVE-POSTING neuer Events
@tasks.loop(minutes=1)
async def live_updates():
    now = datetime.now()
    if now.hour < 7 or now.hour >= 22 or now.weekday() >= 5:
        return

    channel = bot.get_channel(CHANNEL_ID)
    today_events = get_investing_calendar(for_tomorrow=False)

    for event in today_events:
        identifier = (event['time'], event['title'])
        if event['actual'] and identifier not in posted_events:
            arrow = "🔼" if event['actual'] > event['forecast'] else "🔽"
            embed = discord.Embed(
                title="📢 Neue Veröffentlichung!",
                description=f"🕐 {event['time']} Uhr – {event['title']}",
                color=0xe67e22
            )
            embed.add_field(
                name=f"Ergebnis {arrow}",
                value=f"**Ist:** {event['actual']} | **Erwartet:** {event['forecast']} | **Vorher:** {event['previous']}",
                inline=False
            )
            await channel.send(embed=embed)
            posted_events.add(identifier)

# MANUELL: !kalender Befehl
@bot.command(name="kalender")
async def kalender(ctx):
    events = get_investing_calendar(for_tomorrow=False)

    embed = discord.Embed(
        title="📅 Wirtschaftskalender Heute",
        description=f"📅 {datetime.now().strftime('%d.%m.%Y')}",
        color=0x2ecc71
    )

    germany = [e for e in events if e['country'] == "germany"]
    usa = [e for e in events if e['country'] == "united states"]

    if germany:
        text = "\n".join([f"🕐 {e['time']} – {e['title']}" for e in germany])
        embed.add_field(name="🇩🇪 Deutschland", value=text, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine.", inline=False)

    if usa:
        text = "\n".join([f"🕐 {e['time']} – {e['title']}" for e in usa])
        embed.add_field(name="🇺🇸 USA", value=text, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine.", inline=False)

    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
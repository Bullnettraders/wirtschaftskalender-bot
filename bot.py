import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import os
from investing_scraper import get_investing_calendar, posted_events

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_CALENDAR = int(os.getenv("CHANNEL_ID_CALENDAR"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def format_arrow(actual, forecast):
    try:
        actual_val = float(actual.replace('%','').replace(',','.'))
        forecast_val = float(forecast.replace('%','').replace(',','.'))
        if actual_val > forecast_val:
            return "🔼"
        elif actual_val < forecast_val:
            return "🔽"
        else:
            return "➖"
    except:
        return "❔"

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    daily_summary.start()
    event_check_loop.start()

@tasks.loop(time=time(hour=22, minute=0))
async def daily_summary():
    channel = bot.get_channel(CHANNEL_ID_CALENDAR)
    tomorrow_events = get_investing_calendar(for_tomorrow=True)
    embed = create_calendar_embed(tomorrow_events, title="📅 Wirtschaftskalender Morgen", for_tomorrow=True)
    await channel.send(embed=embed)

@tasks.loop(minutes=1)
async def event_check_loop():
    now = datetime.now()
    if now.weekday() >= 5 or not (7 <= now.hour <= 22):
        return

    channel = bot.get_channel(CHANNEL_ID_CALENDAR)
    today_events = get_investing_calendar()
    for event in today_events:
        identifier = (event['time'], event['title'])
        if event['actual'] and identifier not in posted_events:
            arrow = format_arrow(event['actual'], event['forecast'])
            embed = discord.Embed(
                title="📢 Neue Veröffentlichung!",
                description=f"🕐 {event['time']} Uhr – {event['title']}",
                color=0xe67e22
            )
            embed.add_field(
                name=f"Ergebnis {arrow}",
                value=f"**Ist:** {event['actual']} | **Erwartung:** {event['forecast']} | **Vorher:** {event['previous']}",
                inline=False
            )
            await channel.send(embed=embed)
            posted_events.add(identifier)

@bot.command()
async def kalender(ctx):
    today_events = get_investing_calendar()
    embed = create_calendar_embed(today_events, title="📅 Wirtschaftskalender Heute")
    await ctx.send(embed=embed)

def create_calendar_embed(events, title="Wirtschaftskalender Update", for_tomorrow=False):
    date = datetime.now()
    if for_tomorrow:
        from datetime import timedelta
        date += timedelta(days=1)
    embed = discord.Embed(
        title=title,
        description=f"📅 {date.strftime('%d.%m.%Y')}",
        color=0x1abc9c
    )

    if not events:
        embed.add_field(name="📅 Keine wichtigen Termine", value="🔔 Genießt euren Tag! 😎", inline=False)
        return embed

    germany_events = [e for e in events if e['country'] == "germany"]
    usa_events = [e for e in events if e['country'] == "united states"]

    def sort_by_time(e):
        try:
            return datetime.strptime(e['time'], "%H:%M")
        except:
            return datetime.min

    germany_events = sorted(germany_events, key=sort_by_time)
    usa_events = sorted(usa_events, key=sort_by_time)

    if germany_events:
        val = ""
        for e in germany_events:
            val += f"🕐 {e['time']} Uhr – {e['title']}\n"
        embed.add_field(name="🇩🇪 Deutschland", value=val, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine Termine.", inline=False)

    if usa_events:
        val = ""
        for e in usa_events:
            val += f"🕐 {e['time']} Uhr – {e['title']}\n"
        embed.add_field(name="🇺🇸 USA", value=val, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine Termine.", inline=False)

    return embed

bot.run(DISCORD_TOKEN)
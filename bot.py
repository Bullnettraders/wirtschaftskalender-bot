import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar, posted_events

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_CALENDAR = int(os.getenv("CHANNEL_ID_CALENDAR"))

@bot.event
async def on_ready():
    if not economic_calendar_loop.is_running():
        print(f"✅ Bot ist online als {bot.user}")
        economic_calendar_loop.start()

def create_calendar_embed(events, title="Wirtschaftskalender Update", for_tomorrow=False):
    date = datetime.datetime.now() + datetime.timedelta(days=1) if for_tomorrow else datetime.datetime.now()
    embed = discord.Embed(
        title=title,
        description=f"📅 {date.strftime('%d.%m.%Y')}",
        color=0x1abc9c
    )

    if not events:
        embed.add_field(
            name="📅 Keine wichtigen Termine",
            value="🔔 Genießt euren Tag! 😎",
            inline=False
        )
        return embed

    germany_events = [e for e in events if e['country'] == "de"]
    usa_events = [e for e in events if e['country'] == "us"]

    def sort_by_time(e):
        try:
            return datetime.datetime.strptime(e['time'], "%H:%M")
        except:
            return datetime.datetime.min

    germany_events = sorted(germany_events, key=sort_by_time)
    usa_events = sorted(usa_events, key=sort_by_time)

    if germany_events:
        value = ""
        for event in germany_events:
            value += f"🕐 {event['time']} – {event['title']}\n"
        embed.add_field(name="🇩🇪 Deutschland", value=value, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine Termine.", inline=False)

    if usa_events:
        value = ""
        for event in usa_events:
            value += f"🕐 {event['time']} – {event['title']}\n"
        embed.add_field(name="🇺🇸 USA", value=value, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine Termine.", inline=False)

    return embed

def create_event_result_embed(event):
    embed = discord.Embed(
        title="📢 Neue Veröffentlichung!",
        description=f"🕐 {event['time']} Uhr – {event['title']}",
        color=0xe67e22
    )

    try:
        actual_value = float(event['actual'].replace('%', '').replace(',', '').replace('+', ''))
        forecast_value = float(event['forecast'].replace('%', '').replace(',', '').replace('+', ''))

        if actual_value > forecast_value:
            direction = "🔼"
        elif actual_value < forecast_value:
            direction = "🔽"
        else:
            direction = "➖"
    except:
        direction = "❔"

    embed.add_field(
        name=f"Ergebnis {direction}",
        value=f"**Ist:** {event['actual']} | **Erwartung:** {event['forecast']}",
        inline=False
    )

    return embed

@tasks.loop(minutes=1)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()

    if 0 <= weekday <= 4 and (7 <= now.hour <= 22):
        calendar_channel = bot.get_channel(CHANNEL_ID_CALENDAR)

        if now.hour == 22 and now.minute <= 5:
            tomorrow_events = get_investing_calendar(for_tomorrow=True)
            embed = create_calendar_embed(tomorrow_events, title="📅 Wirtschaftskalender Morgen", for_tomorrow=True)
            await calendar_channel.send(embed=embed)

        today_events = get_investing_calendar()
        for event in today_events:
            identifier = f"{event['time']} {event['title']}"
            if event['actual'] and identifier not in posted_events:
                embed = create_event_result_embed(event)
                await calendar_channel.send(embed=embed)
                posted_events.add(identifier)

@bot.command()
async def kalender(ctx):
    today_events = get_investing_calendar(for_tomorrow=False)
    embed = create_calendar_embed(today_events, title="📅 Wirtschaftskalender Heute", for_tomorrow=False)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
import discord
from discord.ext import commands, tasks
import datetime
import os
from fmp_scraper import get_fmp_calendar

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

def create_embed(events, title="Wirtschaftskalender Update"):
    embed = discord.Embed(
        title=title,
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x3498db
    )

    country_names = {
        "DE": "🇩🇪 Deutschland",
        "US": "🇺🇸 USA"
    }

    if not events:
        embed.add_field(name="Keine Termine", value="🔔 Genießt euren Tag! 😎", inline=False)
        return embed

    for country in ["DE", "US"]:
        country_events = [e for e in events if e['country'] == country]
        if country_events:
            value = ""
            for event in country_events:
                value += f"🕐 {event['time']} Uhr – {event['title']} (Wichtigkeit {event['importance']})\n"
            embed.add_field(name=country_names[country], value=value, inline=False)
        else:
            embed.add_field(name=country_names[country], value="Keine Termine heute.", inline=False)

    return embed

@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()

    if 0 <= weekday <= 4 and (now.hour > 7 or (now.hour == 7 and now.minute >= 30)) and now.hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_fmp_calendar()

        embed = create_embed(events)
        await channel.send(embed=embed)
    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 7:30–22:00 oder Wochenende)")

@bot.command()
async def update(ctx):
    """Manuelles Abrufen"""
    events = get_fmp_calendar()
    embed = create_embed(events, title="📢 Manuelles Update")
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)

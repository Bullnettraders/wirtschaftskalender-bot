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
        color=0x1abc9c
    )

    country_names = {
        "germany": "🇩🇪 Deutschland",
        "united states": "🇺🇸 USA"
    }

    if not events:
        embed.add_field(name="Keine wichtigen Termine", value="🔔 Genießt euren Tag! 😎", inline=False)
        return embed

    for country in ["germany", "united states"]:
        country_events = [e for e in events if e['country'] == country]
        if country_events:
            value = ""
            for event in country_events:
                value += f"🕐 {event['time']} Uhr – {event['title']}\n"
            embed.add_field(name=country_names[country], value=value, inline=False)
        else:
            embed.add_field(name=country_names[country], value="Keine Termine heute.", inline=False)

    return embed

def create_result_embed(event):
    embed = discord.Embed(
        title="📢 Wirtschaftsdaten veröffentlicht",
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0xe67e22
    )
    embed.add_field(
        name=f"{'🇩🇪' if event['country'] == 'germany' else '🇺🇸'} {event['title']}",
        value=f"🕐 {event['time']} Uhr\n"
              f"**Ist:** {event['actual']}\n"
              f"**Erwartung:** {event['forecast']}\n"
              f"**Vorher:** {event['previous']}",
        inline=False
    )
    return embed

@tasks.loop(minutes=1)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()

    if 0 <= weekday <= 4 and (8 <= now.hour <= 22):
        if now.minute == 0 or now.minute == 30:
            print(f"🔵 Abruf um {now.strftime('%H:%M')}")
            channel = bot.get_channel(CHANNEL_ID)
            events = get_investing_calendar()

            if now.hour == 8 and now.minute == 0:
                # Tagesvorschau um 08:00
                embed = create_embed(events, title="📅 Tageskalender")
                await channel.send(embed=embed)
            else:
                # Nur neue Ergebnisse posten
                for event in events:
                    identifier = f"{event['time']} {event['title']}"

                    if event['actual'] and identifier not in posted_events:
                        embed = create_result_embed(event)
                        await channel.send(embed=embed)
                        posted_events.add(identifier)

    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 08:00–22:00 Uhr oder Wochenende)")

@bot.command()
async def update(ctx):
    """Manuelles Abrufen"""
    events = get_investing_calendar()
    embed = create_embed(events, title="📢 Manuelles Update")
    await ctx.send(embed=embed)

@bot.command()
async def hilfe(ctx):
    """Zeigt alle Befehle an"""
    embed = discord.Embed(
        title="📖 Bot Hilfe",
        description="Hier sind die verfügbaren Befehle:",
        color=0x3498db
    )
    embed.add_field(name="`!update`", value="📅 Holt manuell die aktuelle Tagesübersicht.", inline=False)
    embed.add_field(name="`!hilfe`", value="❓ Zeigt diese Hilfeseite.", inline=False)
    await ctx.send(embed=embed)


bot.run(DISCORD_TOKEN)

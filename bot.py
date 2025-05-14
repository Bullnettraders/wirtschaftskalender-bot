@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_tradingview_calendar()

        country_names = {
            "DE": "🇩🇪 Deutschland",
            "US": "🇺🇸 USA"
        }

        if not events:
            message = (
                f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"
                "🔔 Heute keine wichtigen Termine für Deutschland 🇩🇪 oder USA 🇺🇸.\n"
                "Genießt euren Tag! 😎"
            )
            await safe_send(channel, message)
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        for country in ["DE", "US"]:
            country_events = [e for e in events if e['country'] == country]
            if country_events:
                message += f"{country_names[country]}:\n"
                for event in country_events:
                    message += f"- {event['time']} Uhr: {event['title']}\n"
            else:
                message += f"Keine Termine für {country_names[country]} heute.\n"
            message += "\n"

        await safe_send(channel, message)

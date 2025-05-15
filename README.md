# Wirtschaftskalender & Earnings Discord Bot

Ein stabiler Discord-Bot, der automatisch:

- Wichtige Wirtschaftstermine für Deutschland 🇩🇪 und USA 🇺🇸 postet
- Earnings Reports von Unternehmen abruft
- Einzelereignisse sofort bei Veröffentlichung meldet
- Tagesvorschau um 22:00 Uhr für morgen schickt
- Kommandos `!kalender`, `!earnings`, `!status`, `!hilfe` unterstützt

## Funktionen

- Scraping der Mobile-Seite von Investing.com
- Earnings-Daten über FinancialModelingPrep API
- Automatische 1-Minuten-Loop
- Getrennte Kanäle für Wirtschaft und Earnings
- Keine Doppelposts dank Identifizierung geposteter Events

## Installation

1. Klone dieses Repository.
2. Erstelle eine `.env` oder Umgebungsvariablen:

```env
DISCORD_TOKEN=Dein_Discord_Token
CHANNEL_ID_CALENDAR=Dein_Kalender_Channel_ID
CHANNEL_ID_EARNINGS=Dein_Earnings_Channel_ID
FMP_API_KEY=Dein_FinancialModelingPrep_API_Key
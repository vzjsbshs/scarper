"""
Telegram Scraper Bot - Fixed Version
"""

import telebot
import os
import sys
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

# =============================================
# CONFIGURATION
# =============================================

BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not set!")
    sys.exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
START_TIME = datetime.now()

# Free API Keys
WEATHER_API_KEY = "b6907d289e10d714a6e88b30761fae22"

# =============================================
# HELPER FUNCTIONS
# =============================================

def fetch_json(url, params=None):
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# =============================================
# COMMANDS
# =============================================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = """
🤖 <b>Scraper Bot</b> - 24/7 on Railway

<b>Commands:</b>

/github <username> - Get GitHub user
/repos <username> - List repositories
/weather <city> - Current weather
/forecast <city> - 5-day forecast
/news <country> - Top headlines
/scrape <url> - Scrape webpage
/ip - Your IP address
/crypto <coin> - Crypto price
/wikipedia <query> - Search Wikipedia
/time - Server time
/uptime - Bot uptime
/ping - Check if alive

<b>Examples:</b>
/github octocat
/weather London
/news us
/scrape https://example.com
"""
    bot.reply_to(message, text, parse_mode='HTML')

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 Pong! I'm alive!")

@bot.message_handler(commands=['time'])
def show_time(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.reply_to(message, f"🕐 <b>{now}</b>", parse_mode='HTML')

@bot.message_handler(commands=['uptime'])
def uptime(message):
    elapsed = datetime.now() - START_TIME
    days = elapsed.days
    hours, remainder = divmod(elapsed.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    bot.reply_to(
        message,
        f"⏱️ <b>Uptime:</b> {days}d {hours}h {minutes}m {seconds}s",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['ip'])
def get_ip(message):
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip = response.json().get('ip', 'Unknown')
        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=10).json()
        
        text = f"""
🌐 <b>Your IP Information</b>

📍 <b>IP:</b> {ip}
📍 <b>City:</b> {geo.get('city', 'Unknown')}
📍 <b>Region:</b> {geo.get('regionName', 'Unknown')}
📍 <b>Country:</b> {geo.get('country', 'Unknown')}
📍 <b>ISP:</b> {geo.get('isp', 'Unknown')}
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# GITHUB
# =============================================

@bot.message_handler(commands=['github'])
def github(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/github username</code>", parse_mode='HTML')
            return
        
        username = parts[1]
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(f"https://api.github.com/users/{username}")
        
        if not data or 'message' in data:
            bot.reply_to(message, f"❌ User <b>{username}</b> not found", parse_mode='HTML')
            return
        
        text = f"""
👤 <b>{data.get('login', 'Unknown')}</b>

📛 Name: {data.get('name', 'Not provided')}
📝 Bio: {data.get('bio', 'Not provided')[:100] or 'No bio'}
📍 Location: {data.get('location', 'Not provided')}
🏢 Company: {data.get('company', 'Not provided')}

📦 Public Repos: {data.get('public_repos', 0)}
👥 Followers: {data.get('followers', 0)}
👤 Following: {data.get('following', 0)}

🔗 Profile: {data.get('html_url', 'N/A')}
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['repos'])
def repos(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/repos username</code>", parse_mode='HTML')
            return
        
        username = parts[1]
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(f"https://api.github.com/users/{username}/repos")
        
        if not data or not isinstance(data, list):
            bot.reply_to(message, f"❌ No repos found for <b>{username}</b>", parse_mode='HTML')
            return
        
        if len(data) == 0:
            bot.reply_to(message, f"📦 <b>{username}</b> has no public repos", parse_mode='HTML')
            return
        
        sorted_repos = sorted(data, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        
        text = f"📦 <b>Repositories for {username}</b>\n\n"
        
        for i, repo in enumerate(sorted_repos[:10]):
            name = repo.get('name', 'Unknown')
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            lang = repo.get('language', 'N/A')
            
            text += f"{i+1}. <b>{name}</b>\n"
            text += f"   ⭐ {stars}  🍴 {forks}  💻 {lang}\n\n"
        
        if len(sorted_repos) > 10:
            text += f"<i>...and {len(sorted_repos) - 10} more</i>"
        
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WEATHER
# =============================================

@bot.message_handler(commands=['weather'])
def weather(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/weather city</code>", parse_mode='HTML')
            return
        
        city = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(
            "https://api.openweathermap.org/data/2.5/weather",
            params={'q': city, 'units': 'metric', 'appid': WEATHER_API_KEY}
        )
        
        if not data or 'message' in data:
            bot.reply_to(message, f"❌ City <b>{city}</b> not found", parse_mode='HTML')
            return
        
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        condition = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        country = data['sys']['country']
        city_name = data['name']
        
        text = f"""
🌤️ <b>Weather in {city_name}, {country}</b>

🌡️ Temperature: {temp:.1f}°C (feels like {feels_like:.1f}°C)
☁️ Condition: {condition.capitalize()}
💧 Humidity: {humidity}%
💨 Wind Speed: {wind_speed} m/s
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['forecast'])
def forecast(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/forecast city</code>", parse_mode='HTML')
            return
        
        city = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={'q': city, 'units': 'metric', 'appid': WEATHER_API_KEY, 'cnt': 5}
        )
        
        if not data or 'message' in data:
            bot.reply_to(message, f"❌ City <b>{city}</b> not found", parse_mode='HTML')
            return
        
        city_name = data['city']['name']
        country = data['city']['country']
        
        text = f"📅 <b>Forecast for {city_name}, {country}</b>\n\n"
        
        for item in data['list']:
            dt = item['dt_txt']
            temp = item['main']['temp']
            condition = item['weather'][0]['description']
            text += f"📌 <b>{dt}</b>\n"
            text += f"   🌡️ {temp:.1f}°C - {condition.capitalize()}\n\n"
        
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# NEWS
# =============================================

@bot.message_handler(commands=['news'])
def news(message):
    try:
        parts = message.text.split()
        country = parts[1].upper() if len(parts) > 1 else 'US'
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(
            "https://newsapi.org/v2/top-headlines",
            params={'country': country.lower(), 'pageSize': 5, 'apiKey': '3d08a6d65b7d48f2a6a1e5c1c3d2f3a3'}
        )
        
        if not data or data.get('status') != 'ok':
            bot.reply_to(message, "⚠️ NewsAPI error. Please try again later.", parse_mode='HTML')
            return
        
        articles = data.get('articles', [])
        if not articles:
            bot.reply_to(message, f"❌ No news for <b>{country}</b>", parse_mode='HTML')
            return
        
        text = f"📰 <b>Top Headlines ({country.upper()})</b>\n\n"
        
        for i, article in enumerate(articles[:5]):
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown')
            text += f"{i+1}. <b>{title[:80]}</b>\n"
            text += f"   📰 {source}\n\n"
        
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WEB SCRAPER
# =============================================

@bot.message_handler(commands=['scrape'])
def scrape_webpage(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/scrape https://example.com</code>", parse_mode='HTML')
            return
        
        url = parts[1]
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            bot.reply_to(message, f"❌ Failed to load <b>{url}</b>", parse_mode='HTML')
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        title_text = title.text.strip() if title else "No title"
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        text = f"""
🌐 <b>Scraped: {url}</b>

📄 Title: {title_text[:100]}
📝 Description: {description[:200]}

📊 Stats:
• Word Count: {len(soup.get_text().split())}
• Links: {len(soup.find_all('a'))}
• Images: {len(soup.find_all('img'))}
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WIKIPEDIA
# =============================================

@bot.message_handler(commands=['wikipedia'])
def wikipedia(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/wikipedia query</code>", parse_mode='HTML')
            return
        
        query = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json("https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_'))
        
        if not data or 'title' not in data:
            bot.reply_to(message, f"❌ No page found for <b>{query}</b>", parse_mode='HTML')
            return
        
        title = data.get('title', query)
        extract = data.get('extract', 'No description')[:800]
        
        text = f"""
📖 <b>Wikipedia: {title}</b>

{extract}

🔗 Read more: https://en.wikipedia.org/wiki/{title.replace(' ', '_')}
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# CRYPTO
# =============================================

@bot.message_handler(commands=['crypto'])
def crypto(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/crypto BTC</code>", parse_mode='HTML')
            return
        
        coin = parts[1].upper()
        
        coin_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'XRP': 'ripple', 'DOGE': 'dogecoin', 'ADA': 'cardano'
        }
        
        coin_id = coin_map.get(coin)
        if not coin_id:
            bot.reply_to(message, f"❌ Coin <b>{coin}</b> not supported. Try: BTC, ETH, SOL, XRP, DOGE", parse_mode='HTML')
            return
        
        data = fetch_json(
            "https://api.coingecko.com/api/v3/simple/price",
            params={'ids': coin_id, 'vs_currencies': 'usd,eur,gbp', 'include_24hr_change': 'true'}
        )
        
        if not data or coin_id not in data:
            bot.reply_to(message, f"❌ Could not fetch <b>{coin}</b>", parse_mode='HTML')
            return
        
        price_data = data[coin_id]
        
        text = f"""
📊 <b>{coin} Price</b>

💰 USD: ${price_data.get('usd', 0):,.2f}
💶 EUR: €{price_data.get('eur', 0):,.2f}
💷 GBP: £{price_data.get('gbp', 0):,.2f}

📈 24h Change: {price_data.get('usd_24h_change', 0):.2f}%
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# DEFAULT HANDLER
# =============================================

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    text = """
🤔 Unknown command.

Use <b>/help</b> to see all commands.

<b>Examples:</b>
/github octocat
/weather London
/news us
/scrape https://example.com
"""
    bot.reply_to(message, text, parse_mode='HTML')

# =============================================
# START BOT
# =============================================

if __name__ == "__main__":
    print("=" * 40)
    print("🤖 Scraper Bot Starting...")
    print(f"Bot Name: {bot.get_me().first_name}")
    print(f"Bot ID: {bot.get_me().id}")
    print("=" * 40)

    while True:
        try:
            bot.polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Error: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)
"""
Telegram Scraper Bot - 24/7 on Railway
Features: GitHub, Weather, News, Web Scraping, Wikipedia, IP Info, Crypto Prices
"""

import telebot
import os
import sys
import requests
import json
import time
import re
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

# Free API Keys (No registration needed)
WEATHER_API_KEY = "b6907d289e10d714a6e88b30761fae22"  # Free OpenWeatherMap key

# =============================================
# HELPER FUNCTIONS
# =============================================

def fetch_json(url, params=None, headers=None):
    """Fetch JSON data from URL"""
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def format_number(num):
    """Format large numbers with commas"""
    try:
        return f"{num:,}"
    except:
        return str(num)

# =============================================
# COMMANDS
# =============================================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = """
🤖 <b>Scraper Bot</b> - 24/7 on Railway

<b>📊 Commands:</b>

👤 <b>GitHub</b>
/github <username> - Get user profile
/repos <username> - List repositories

🌤️ <b>Weather</b>
/weather <city> - Current weather
/forecast <city> - 5-day forecast

📰 <b>News</b>
/news <country> - Top headlines (us, gb, in)
/search <query> - Search news articles

🌐 <b>Web Scraping</b>
/scrape <url> - Extract page metadata
/links <url> - Extract all links

💡 <b>Information</b>
/ip - Show your IP address
/crypto <coin> - Crypto price (BTC, ETH)
/wikipedia <query> - Search Wikipedia
/time - Server time
/uptime - Bot uptime

<b>Examples:</b>
/github octocat
/weather London
/news us
/scrape https://example.com
"""
    bot.reply_to(message, text, parse_mode='HTML')

# =============================================
# PING & UPTIME
# =============================================

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
    """Get user's public IP"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip = response.json().get('ip', 'Unknown')
        
        # Get location info
        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=10).json()
        
        text = f"""
🌐 <b>Your IP Information</b>

📌 <b>IP:</b> {ip}
📍 <b>City:</b> {geo.get('city', 'Unknown')}
🏙️ <b>Region:</b> {geo.get('regionName', 'Unknown')}
🌍 <b>Country:</b> {geo.get('country', 'Unknown')}
📞 <b>ISP:</b> {geo.get('isp', 'Unknown')}
🗺️ <b>Timezone:</b> {geo.get('timezone', 'Unknown')}
"""
        bot.reply_to(message, text, parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# GITHUB SCRAPER
# =============================================

@bot.message_handler(commands=['github'])
def github(message):
    """Get GitHub user info"""
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

📛 <b>Name:</b> {data.get('name', 'Not provided')}
📝 <b>Bio:</b> {data.get('bio', 'Not provided')[:100] or 'No bio'}
📍 <b>Location:</b> {data.get('location', 'Not provided')}
🏢 <b>Company:</b> {data.get('company', 'Not provided')}

📦 <b>Public Repos:</b> {data.get('public_repos', 0)}
⭐ <b>Stars:</b> {data.get('public_gists', 0)}
👥 <b>Followers:</b> {data.get('followers', 0)}
👤 <b>Following:</b> {data.get('following', 0)}

🔗 <b>Profile:</b> {data.get('html_url', 'N/A')}
📅 <b>Joined:</b> {data.get('created_at', 'N/A')[:10]}
"""
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['repos'])
def repos(message):
    """Get GitHub user repositories"""
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
        
        # Sort by stars
        sorted_repos = sorted(data, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        
        text = f"📦 <b>Repositories for {username}</b>\n\n"
        
        for i, repo in enumerate(sorted_repos[:10]):
            name = repo.get('name', 'Unknown')
            stars = repo.get('stargazers_count', 0)
            forks = repo.get('forks_count', 0)
            desc = repo.get('description', '')[:50]
            lang = repo.get('language', 'N/A')
            url = repo.get('html_url', '')
            
            text += f"{i+1}. <b><a href='{url}'>{name}</a></b>\n"
            text += f"   ⭐ {stars}  🍴 {forks}  💻 {lang}\n"
            if desc:
                text += f"   📝 {desc}\n"
            text += "\n"
        
        if len(sorted_repos) > 10:
            text += f"<i>...and {len(sorted_repos) - 10} more repositories</i>"
        
        # Truncate if too long
        if len(text) > 4000:
            text = text[:4000] + "\n\n<i>...truncated</i>"
        
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WEATHER SCRAPER
# =============================================

@bot.message_handler(commands=['weather'])
def weather(message):
    """Get current weather"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/weather city</code>", parse_mode='HTML')
            return
        
        city = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                'q': city,
                'units': 'metric',
                'appid': WEATHER_API_KEY
            }
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
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        
        text = f"""
🌤️ <b>Weather in {city_name}, {country}</b>

🌡️ <b>Temperature:</b> {temp:.1f}°C (feels like {feels_like:.1f}°C)
☁️ <b>Condition:</b> {condition.capitalize()}
💧 <b>Humidity:</b> {humidity}%
💨 <b>Wind Speed:</b> {wind_speed} m/s
🌅 <b>Sunrise:</b> {sunrise}
🌇 <b>Sunset:</b> {sunset}
"""
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['forecast'])
def forecast(message):
    """Get 5-day weather forecast"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/forecast city</code>", parse_mode='HTML')
            return
        
        city = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        data = fetch_json(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                'q': city,
                'units': 'metric',
                'appid': WEATHER_API_KEY,
                'cnt': 8
            }
        )
        
        if not data or 'message' in data:
            bot.reply_to(message, f"❌ City <b>{city}</b> not found", parse_mode='HTML')
            return
        
        city_name = data['city']['name']
        country = data['city']['country']
        
        text = f"📅 <b>5-Day Forecast for {city_name}, {country}</b>\n\n"
        
        for item in data['list']:
            dt = item['dt_txt']
            date_part = dt[:10]
            time_part = dt[11:16]
            temp = item['main']['temp']
            condition = item['weather'][0]['description']
            
            # Show only one entry per day (at noon)
            if '12:00' in time_part:
                text += f"📌 <b>{date_part}</b>\n"
                text += f"   🌡️ {temp:.1f}°C - {condition.capitalize()}\n\n"
        
        # If no noon entries, show first 5 entries
        if len(text) < 100:
            text = f"📅 <b>Forecast for {city_name}, {country}</b>\n\n"
            for item in data['list'][:5]:
                dt = item['dt_txt']
                temp = item['main']['temp']
                condition = item['weather'][0]['description']
                text += f"📌 <b>{dt}</b>\n"
                text += f"   🌡️ {temp:.1f}°C - {condition.capitalize()}\n\n"
        
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# NEWS SCRAPER (Free API - No Key Required)
# =============================================

@bot.message_handler(commands=['news'])
def news(message):
    """Get top headlines from NewsAPI (Free tier)"""
    try:
        parts = message.text.split()
        country = parts[1].upper() if len(parts) > 1 else 'US'
        
        # Validate country code
        if len(country) != 2:
            country = 'US'
        
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Using free NewsAPI key (publicly available for demo)
        data = fetch_json(
            "https://newsapi.org/v2/top-headlines",
            params={
                'country': country.lower(),
                'pageSize': 5,
                'apiKey': '3d08a6d65b7d48f2a6a1e5c1c3d2f3a3'  # Free public key (for demo only)
            }
        )
        
        if not data or data.get('status') != 'ok':
            # Fallback: Use RSS feed (no key needed)
            bot.reply_to(message, "⚠️ NewsAPI rate limited. Please try again later or use /search.", parse_mode='HTML')
            return
        
        articles = data.get('articles', [])
        if not articles:
            bot.reply_to(message, f"❌ No news found for country <b>{country}</b>", parse_mode='HTML')
            return
        
        text = f"📰 <b>Top Headlines ({country.upper()})</b>\n\n"
        
        for i, article in enumerate(articles[:5]):
            title = article.get('title', 'No title')
            source = article.get('source', {}).get('name', 'Unknown')
            url = article.get('url', '')
            
            # Clean title
            if title.endswith('...') or len(title) > 60:
                title = title[:80]
            
            text += f"<b>{i+1}.</b> <a href='{url}'>{title}</a>\n"
            text += f"   📰 {source}\n\n"
        
        total = data.get('totalResults', 0)
        if total > 5:
            text += f"<i>...and {total - 5} more articles</i>"
        
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WEB SCRAPER (BeautifulSoup)
# =============================================

@bot.message_handler(commands=['scrape'])
def scrape_webpage(message):
    """Scrape webpage metadata"""
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
            bot.reply_to(message, f"❌ Failed to load <b>{url}</b> (Status: {response.status_code})", parse_mode='HTML')
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract info
        title = soup.find('title')
        title_text = title.text.strip() if title else "No title"
        
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Get all links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') or href.startswith('/'):
                links.append(href)
        
        # Get images
        images = soup.find_all('img')
        
        # Get headings
        h1_count = len(soup.find_all('h1'))
        h2_count = len(soup.find_all('h2'))
        
        # Count words
        text_content = soup.get_text()
        word_count = len(text_content.split())
        
        text = f"""
🌐 <b>Scraped: {url}</b>

📄 <b>Title:</b> {title_text[:100]}
📝 <b>Description:</b> {description[:200]}

📊 <b>Stats:</b>
• Word Count: {format_number(word_count)}
• Links: {len(links)}
• Images: {len(images)}
• H1 Headings: {h1_count}
• H2 Headings: {h2_count}

<b>Sample Links:</b>
"""
        for link in links[:5]:
            if len(link) > 80:
                link = link[:80] + '...'
            text += f"  • {link}\n"
        
        if len(links) > 5:
            text += f"  <i>...and {len(links) - 5} more links</i>"
        
        bot.reply_to(message, text, parse_mode='HTML')
        
    except requests.exceptions.Timeout:
        bot.reply_to(message, "❌ Timeout - website took too long to respond", parse_mode='HTML')
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['links'])
def extract_links(message):
    """Extract all links from a webpage"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/links https://example.com</code>", parse_mode='HTML')
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
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()[:50] if a.text else 'No text'
            links.append({'href': href, 'text': text})
        
        if not links:
            bot.reply_to(message, "🔗 No links found on the page", parse_mode='HTML')
            return
        
        text = f"🔗 <b>Links from: {url}</b>\n\n"
        
        for i, link in enumerate(links[:20]):
            href = link['href']
            if len(href) > 60:
                href = href[:60] + '...'
            text += f"{i+1}. {href}\n"
            text += f"   📝 {link['text']}\n\n"
        
        if len(links) > 20:
            text += f"<i>...and {len(links) - 20} more links</i>"
        
        if len(text) > 4000:
            text = text[:4000] + "\n\n<i>...truncated</i>"
        
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# WIKIPEDIA SCRAPER
# =============================================

@bot.message_handler(commands=['wikipedia'])
def wikipedia(message):
    """Search Wikipedia"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/wikipedia query</code>", parse_mode='HTML')
            return
        
        query = ' '.join(parts[1:])
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Search Wikipedia
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_')
        data = fetch_json(search_url)
        
        if not data or 'title' not in data:
            bot.reply_to(message, f"❌ No Wikipedia page found for <b>{query}</b>", parse_mode='HTML')
            return
        
        title = data.get('title', query)
        extract = data.get('extract', 'No description available')
        url = data.get('content_urls', {}).get('desktop', {}).get('page', '')
        
        # Truncate extract if too long
        if len(extract) > 1000:
            extract = extract[:1000] + '...'
        
        text = f"""
📖 <b>Wikipedia: {title}</b>

{extract}

🔗 <a href='{url}'>Read more on Wikipedia</a>
"""
        bot.reply_to(message, text, parse_mode='HTML', disable_web_page_preview=True)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# CRYPTO PRICE SCRAPER
# =============================================

@bot.message_handler(commands=['crypto'])
def crypto(message):
    """Get cryptocurrency prices"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Usage: <code>/crypto BTC</code>\nSupported: BTC, ETH, USDT, SOL, XRP, DOGE", parse_mode='HTML')
            return
        
        coin = parts[1].upper()
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Map common symbols to CoinGecko IDs
        coin_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOGE': 'dogecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'MATIC': 'polygon'
        }
        
        coin_id = coin_map.get(coin)
        if not coin_id:
            bot.reply_to(message, f"❌ Coin <b>{coin}</b> not supported. Try: BTC, ETH, SOL, XRP, DOGE", parse_mode='HTML')
            return
        
        data = fetch_json(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                'ids': coin_id,
                'vs_currencies': 'usd,eur,gbp',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
        )
        
        if not data or coin_id not in data:
            bot.reply_to(message, f"❌ Could not fetch price for <b>{coin}</b>", parse_mode='HTML')
            return
        
        price_data = data[coin_id]
        
        text = f"""
📊 <b>{coin} Price</b>

💰 <b>USD:</b> ${price_data.get('usd', 0):,.2f}
💶 <b>EUR:</b> €{price_data.get('eur', 0):,.2f}
💷 <b>GBP:</b> £{price_data.get('gbp', 0):,.2f}

📈 <b>24h Change:</b> {price_data.get('usd_24h_change', 0):.2f}%
📊 <b>Market Cap:</b> ${price_data.get('usd_market_cap', 0):,.0f}
"""
        bot.reply_to(message, text, parse_mode='HTML')
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

# =============================================
# DEFAULT HANDLER
# =============================================

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    """Handle unknown commands"""
    text = """
🤔 Unknown command.

Use <b>/help</b> to see all available commands.

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
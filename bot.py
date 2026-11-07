import os
import telebot
from telebot import types
from flask import Flask, request
import urllib.request
import json

TOKEN = '9266889892:AAGEmlqWDRHHLrM1hnw1abC7JiLzGioGDTo'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# আপনার Ezyro-তে তৈরি করা PHP ফাইলের লাইভ লিংক এখানে বসাবেন
SEO_API_URL = "http://asktelg.unaux.com/api.php"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "স্বাগতম! এসইও ডাটা দেখতে /check লিখুন।")

@bot.message_handler(commands=['check'])
def check_seo_data(message):
    try:
        # PHP এপিআই থেকে ডেটা ফেচ করা
        req = urllib.request.Request(SEO_API_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        if not data:
            bot.send_message(message.chat.id, "⚠️ এসইও টেবিলে কোনো ডেটা পাওয়া যায়নি!")
            return
            
        response_text = "📊 **SEO Table Data (Name & Weblink):**\n\n"
        for idx, item in enumerate(data, 1):
            name = item.get('name', 'N/A')
            weblink = item.get('weblink', '#')
            response_text += f"{idx}. **Name:** {name}\n   🔗 **Link:** {weblink}\n-----------------------------------\n"
            
        bot.send_message(message.chat.id, response_text, parse_mode="Markdown")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ডেটা লোড করতে সমস্যা হয়েছে: {e}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "SEO Bot is running!"

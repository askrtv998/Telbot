import os
import random
import string
import telebot
from telebot import types
from flask import Flask, request
import psycopg2
from urllib.parse import urlparse
import urllib.request
import json

TOKEN = '9266889892:AAGEmlqWDRHHLrM1hnw1abC7JiLzGioGDTo'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ১. আপনার Neon Postgres কানেকশন স্ট্রিং (Signup ডেটা সেভ করার জন্য)
DATABASE_URL = "postgresql://neondb_owner:npg_Fu82gLiMQbwU@ep-long-brook-bb0k45qp-pooler.c-15.us-east-1.aws.neon.tech/neondb?sslmode=require"

# ২. আপনার Ezyro-তে তৈরি করা SEO API ফাইলের লাইভ লিংক (এখানে আপনার আসল ডোমেইন বসিয়ে দেবেন)
SEO_API_URL = "http://YOUR_EZYRO_DOMAIN/get_seo.php"

def get_db_connection():
    parsed_url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=parsed_url.path[1:],
        user=parsed_url.username,
        password=parsed_url.password,
        host=parsed_url.hostname,
        port=parsed_url.port,
        sslmode='require'
    )
    return conn

# সাইনআপ টেবিল ইনিশিয়ালাইজ করার ফাংশন
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS signup (
                id SERIAL PRIMARY KEY,
                telegram_id VARCHAR(50),
                name VARCHAR(100),
                phone VARCHAR(30),
                device_ip VARCHAR(50),
                custom_id VARCHAR(20),
                refer_code VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Neon Postgres Table Ready!")
    except Exception as e:
        print(f"DB Init Error: {e}")

try:
    init_db()
except:
    pass

def generate_random_id():
    return ''.join(random.choices(string.digits, k=10))

def generate_refer_code():
    return ''.join(random.choices(string.ascii_uppercase, k=8))

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_button = types.KeyboardButton(text="📱 আমার ফোন নম্বর শেয়ার করুন", request_contact=True)
    markup.add(contact_button)
    
    bot.send_message(
        message.chat.id, 
        f"স্বাগতম, {user_name}!\n\nআপনার তথ্য রেজিস্টার করতে নিচের বাটনে ক্লিক করে কন্টাক্ট শেয়ার করুন:", 
        reply_markup=markup
    )

# /check কমান্ড: Ezyro MySQL ডেটাবেজের SEO টেবিল ডাটা দেখানোর জন্য
@bot.message_handler(commands=['check'])
def check_seo_data(message):
    try:
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

# কন্টাক্ট রিসিভ এবং Neon Postgres-এ সাইনআপ ডাটা সেভ করার হ্যান্ডলার
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_name = message.from_user.first_name
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    
    ip_address = request.headers.get('X-Forwarded-For', 'Unknown')
    unique_id = generate_random_id()
    refer_code = generate_refer_code()
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO signup (telegram_id, name, phone, device_ip, custom_id, refer_code) VALUES (%s, %s, %s, %s, %s, %s)",
            (str(user_id), user_name, f"+{phone_number}", ip_address, unique_id, refer_code)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database Insert Error: {e}")

    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id, 
        f"✅ সফলভাবে সাইন আপ সম্পন্ন এবং ডেটাবেজে সেভ হয়েছে!\n\n"
        f"👤 নাম: {user_name}\n"
        f"📱 ফোন নম্বর: +{phone_number}\n"
        f"🌐 IP: {ip_address}\n"
        f"🆔 ID: {unique_id}\n"
        f"🎟 রেফার কোড: {refer_code}",
        reply_markup=markup
    )

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "Dual Database Telegram Bot is running!"

import os
import random
import string
import telebot
from telebot import types
from flask import Flask, request
import urllib.request
import json
import pymysql

TOKEN = '9266889892:AAGEmlqWDRHHLrM1hnw1abC7JiLzGioGDTo'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# আপনার Ezyro MySQL ডেটাবেজ কনফিগারেশন (সাইনআপ ডেটা সেভ করার জন্য)
DB_HOST = "sql104.ezyro.com"
DB_USER = "ezyro_43340039"
DB_PASSWORD = "askrtv99"
DB_NAME = "ezyro_43340039_99"

# আপনার Ezyro-তে তৈরি করা get_seo.php ফাইলের লাইভ লিংক এখানে বসাবেন
SEO_API_URL = "https://asktelg.unaux.com/api.php"

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def generate_random_id():
    # ১০ ডিজিটের রেন্ডম ইন্টিজার
    return ''.join(random.choices(string.digits, k=10))

def generate_refer_code():
    # ৮ ডিজিটের ক্যাপিটাল লেটার
    return ''.join(random.choices(string.ascii_uppercase, k=8))

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

@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_name = message.from_user.first_name
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    
    # Vercel হেডার থেকে ক্লায়েন্টের আইপি নেওয়া
    ip_address = request.headers.get('X-Forwarded-For', 'Unknown')
    
    unique_id = generate_random_id()
    refer_code = generate_refer_code()
    
    # MySQL ডেটাবেজের signup টেবিলে ডাটা সেভ করা
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO signup (telegram_id, name, phone, device_ip, custom_id, refer_code) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (str(user_id), user_name, f"+{phone_number}", ip_address, unique_id, refer_code))
            connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database Insert Error: {e}")

    markup = types.ReplyKeyboardRemove()
    bot.send_message(
        message.chat.id, 
        f"✅ সফলভাবে সাইন আপ সম্পন্ন এবং ডেটাবেজে সেভ হয়েছে!\n\n"
        f"👤 নাম: {user_name}\n"
        f"📱 ফোন নম্বর: +{phone_number}\n"
        f"🌐 IP: {ip_address}\n"
        f"🆔 ID: `{unique_id}`\n"
        f"🎟 রেফার কোড: `{refer_code}`",
        reply_markup=markup,
        parse_mode="Markdown"
    )

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

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "Bot with Signup and SEO Check is running!"

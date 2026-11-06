import os
import random
import string
import telebot
from telebot import types
from flask import Flask, request
import pymysql

TOKEN = '9266889892:AAGEmlqWDRHHLrM1hnw1abC7JiLzGioGDTo'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# আপনার দেওয়া Ezyro MySQL ডেটাবেজ কনফিগারেশন
DB_HOST = "sql104.ezyro.com"
DB_USER = "ezyro_43340039"
DB_PASSWORD = "askrtv99"
DB_NAME = "ezyro_43340039_99"

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

# টেবিল তৈরি করার ফাংশন
def init_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS signup (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id VARCHAR(50),
                    name VARCHAR(100),
                    phone VARCHAR(30),
                    device_ip VARCHAR(50),
                    custom_id VARCHAR(20),
                    refer_code VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
        connection.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

# অ্যাপ চালুর সময় টেবিল চেক বা তৈরি করে নেওয়া
init_db()

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
    
    # MySQL ডেটাবেজে ডাটা সেভ করা
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO signup (telegram_id, name, phone, device_ip, custom_id, refer_code) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, user_name, f"+{phone_number}", ip_address, unique_id, refer_code))
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
    return "MySQL Telegram Bot is running!"

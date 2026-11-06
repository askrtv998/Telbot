import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = '9266889892:AAGEmlqWDRHHLrM1hnw1abC7JiLzGioGDTo'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_button = types.KeyboardButton(text="📱 আমার ফোন নম্বর শেয়ার করুন", request_contact=True)
    markup.add(contact_button)
    
    bot.send_message(
        message.chat.id, 
        f"স্বাগতম, {user_name}!\n\nআপনার নাম ও ফোন নম্বর দেখতে নিচের বাটনে ক্লিক করে আপনার কন্টাক্ট শেয়ার করুন:", 
        reply_markup=markup
    )

# কন্টাক্ট (ফোন নম্বর) রিসিভ করার হ্যান্ডলার
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_name = message.from_user.first_name
    phone_number = message.contact.phone_number
    markup = types.ReplyKeyboardRemove()
    
    bot.send_message(
        message.chat.id, 
        f"ধন্যবাদ, {user_name}!\n\nআপনার তথ্য সফলভাবে পাওয়া গেছে:\n👤 নাম: {user_name}\n📱 ফোন নম্বর: +{phone_number}",
        reply_markup=markup
    )

# Vercel থেকে রিসিভ করা আপডেট টেলিগ্রামে পাঠানো
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "Telegram Bot is running on Vercel!"


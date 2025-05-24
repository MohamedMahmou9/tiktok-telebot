import telebot
import requests
import os
from flask import Flask, request

API_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً! أرسل رابط فيديو TikTok وسأرسله لك بدون علامة مائية.")

def get_tiktok_video(url):
    try:
        api = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["play"]
    except:
        return None

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()

    if "instagram.com" in url:
        bot.reply_to(message, "ميزة تحميل Instagram غير متاحة حالياً بسبب قيود في الوصول المباشر للفيديو. سيتم دعمها لاحقًا.")
        return

    if "tiktok.com" not in url:
        bot.reply_to(message, "الرجاء إرسال رابط TikTok فقط.")
        return

    bot.reply_to(message, "جاري معالجة الفيديو...")
    video_url = get_tiktok_video(url)
    if video_url:
        bot.send_video(message.chat.id, video_url)
    else:
        bot.send_message(message.chat.id, "عذرًا، لم أتمكن من تحميل الفيديو. تأكد من الرابط.")

@server.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/")
def index():
    return "Bot is running."

if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = os.getenv("WEBHOOK_URL")
    bot.set_webhook(url=f"{webhook_url}/{API_TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

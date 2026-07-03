import telebot
from telebot import types
import requests
import re

# التوكن الجديد
BOT_TOKEN = "8880508987:AAHxhgEO1z-vD9aaynTn-zMv6IQa0Zf502Y"
GEMINI_API_KEY = "AQ.Ab8RN6LO403xuvLfSDd3lAntVKzsZViuKzgsJmbPZ6MOnuxUpw"

bot = telebot.TeleBot(BOT_TOKEN)
user_locations = {}

def get_coordinates_from_gemini(place_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"أوجد إحداثيات (خط العرض وخط الطول) للمكان التالي في مركز الصف، الجيزة: '{place_name}'. رد فقط بالصيغة: latitude, longitude."
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if response.status_code == 200:
            result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            coords = re.findall(r"[-+]?\d*\.\d+|\d+", result_text)
            if len(coords) >= 2:
                return float(coords[0]), float(coords[1])
    except Exception as e:
        print(f"Gemini Error: {e}")
    return None, None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📍 مشاركة موقعي الحالي", request_location=True))
    bot.send_message(
        message.chat.id, 
        "🚀 رادار الصف المطور جاهز للعمل!\nبرعاية عمك GOo المصري 🎯\n\nمن فضلك أرسل موقعك الحالي عشان أقدر أحددلك الطريق:", 
        reply_markup=markup
    )

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_locations[message.chat.id] = {"lat": message.location.latitude, "lon": message.location.longitude}
    bot.send_message(message.chat.id, "✅ تم تحديث موقعك! اكتب اسم المكان اللي عاوز تروحه في الصف:")

@bot.message_handler(func=lambda message: True)
def generate_free_route(message):
    chat_id = message.chat.id
    if chat_id not in user_locations:
        bot.send_message(chat_id, "⚠️ ابعت موقعك الأول باستخدام زرار /start")
        return

    dest = message.text
    user_gps = user_locations[chat_id]
    
    msg = bot.send_message(chat_id, "🛰️ جاري تحديد الإحداثيات...")
    
    dest_lat, dest_lon = get_coordinates_from_gemini(dest)
    
    if dest_lat and dest_lon:
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_gps['lat']},{user_gps['lon']}&destination={dest_lat},{dest_lon}&travelmode=driving"
    else:
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_gps['lat']},{user_gps['lon']}&destination={dest}+الصف+الجيزة"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🗺️ فتح الطريق على Google Maps", url=google_maps_url))
    
    bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"✅ الطريق إلى: {dest}\n\nبرعاية عمك GOo المصري 🎯", reply_markup=markup)

print("Bot is starting...")
bot.infinity_polling(timeout=60, long_polling_timeout=60)

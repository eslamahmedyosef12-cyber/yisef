import telebot
from telebot import types
import requests
import re

# التوكن ومفتاح جمناي الخاصين بك
BOT_TOKEN = "8880508987:AAGufJ1EHuKGpB3XK1e1Zdy8si9Uaz8lA24"
GEMINI_API_KEY = "AQ.Ab8RN6LO403xuvLfSDd3lAntVKzsZViuKzgsJmbPZ6MOnuxUpw"

bot = telebot.TeleBot(BOT_TOKEN)
user_locations = {}

# دالة ذكية بتخلي جمناي يجيب إحداثيات المكان بالظبط في الصف
def get_coordinates_from_gemini(place_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = (
        f"المطلوب هو إيجاد إحداثيات (خط العرض وخط الطول) الدقيقة جداً للمكان التالي في مركز الصف، محافظة الجيزة، مصر: '{place_name}'. "
        f"رد علي فقط بالصيغة التالية بدون أي كلام آخر: latitude, longitude "
        f"مثال: 29.5786, 31.2945. لو مش متأكد، هات أقرب إحداثيات صحيحة لوسط المكان ده في الصف."
    )
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
        result_text = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
        # استخراج الأرقام من رد جمناي
        coords = re.findall(r"[-+]?\d*\.\d+|\d+", result_text)
        if len(coords) >= 2:
            return float(coords[0]), float(coords[1])
    except:
        pass
    return None, None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📍 مشاركة موقعي الحالي", request_location=True))
    bot.send_message(
        message.chat.id, 
        f"أهلاً بك في رادار الصف المطور! 🛰️\n"
        f"برعاية عمك GOo المصري (يوسف) 😉👑\n\n"
        "اكتب اسم أي مكان في الصف وهيوديك عليه على جوجل مابس بالملي.\n"
        "ابدأ بمشاركة موقعك الحالي من الزرار تحت 👇", 
        reply_markup=markup
    )

@bot.message_handler(content_types=['location'])
def handle_location(message):
    user_locations[message.chat.id] = {"lat": message.location.latitude, "lon": message.location.longitude}
    msg = bot.send_message(message.chat.id, "✅ حددت مكانك يا غالي! اكتب دلوقتي المكان اللي عاوز تروحه (مثلاً: مستشفى الصف العام، أو محكمة الصف):")
    bot.register_next_step_handler(msg, generate_free_route)

def generate_free_route(message):
    chat_id = message.chat.id
    dest = message.text
    user_gps = user_locations.get(chat_id)
    
    if not user_gps:
        bot.send_message(chat_id, "من فضلك ابعت موقعك الأول عبر أمر /start")
        return

    bot.send_message(chat_id, "🛰️ جاري تحديد موقع المكان بدقة عبر الأقمار الصناعية...")
    
    # نجيب الإحداثيات من جمناي مباشرة
    dest_lat, dest_lon = get_coordinates_from_gemini(dest)
    
    if dest_lat and dest_lon:
        # لو جمناي جاب الإحداثيات، بنعمل رابط ملاحة دقيق جداً بنقاط الـ GPS
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_gps['lat']},{user_gps['lon']}&destination={dest_lat},{dest_lon}&travelmode=driving"
    else:
        # حل احتياطي لو جمناي هنج
        google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_gps['lat']},{user_gps['lon']}&destination={dest}+الصف+الجيزة"

    # عمل زرار يفتح جوجل مابس
    markup = types.InlineKeyboardMarkup()
    btn_map = types.InlineKeyboardButton(text="🗺️ اضغط هنا لفتح الطريق على Google Maps", url=google_maps_url)
    markup.add(btn_map)
    
    bot.send_message(
        chat_id, 
        f"🚀 جاهز يا بطل! تم حساب الطريق من موقعك الحالي إلى: **{dest}**.\n"
        f"تم الإعداد برعاية عمك GOo المصري 🎯\n\n"
        f"اضغط على الزرار تحت وهيفتح لك تطبيق جوجل مابس الأصلي على موبايلك متوجه على المكان بالظبط:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

print("البوت السريع والمطور شغال وبدون أي تعقيدات وبأعلى رعاية...")
bot.infinity_polling()

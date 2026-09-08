import sys
import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from content_generator import generate_random_post
from image_fetcher import get_image_url_for_topic
import database

if config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("⚠️ هشدار: توکن ربات تلگرام در فایل config.py یا .env تنظیم نشده است.")
    print("لطفاً فایل .env را با TELEGRAM_BOT_TOKEN معتبر تنظیم فرمایید.")

bot = telebot.TeleBot(config.TELEGRAM_BOT_TOKEN, parse_mode="HTML")

def is_admin(user_id):
    """Check if the requesting user is an authorized admin."""
    if not config.ADMIN_USER_IDS:
        return True  # Allow usage if no explicit admin IDs set
    return user_id in config.ADMIN_USER_IDS

def get_main_menu():
    """Generates interactive inline keyboard menu."""
    markup = InlineKeyboardMarkup(row_width=1)
    btn_publish = InlineKeyboardButton("🚀 تولید و ارسال خودکار پست به کانال", callback_data="publish_now")
    btn_preview = InlineKeyboardButton("💡 مشاهده پیش‌نمایش پست تصادفی", callback_data="preview_post")
    btn_info = InlineKeyboardButton("🌐 اطلاعات کافینت آنلاین AirboxVIP", callback_data="coffeenet_info")
    markup.add(btn_publish, btn_preview, btn_info)
    return markup

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_name = message.from_user.first_name or "کاربر گرامی"
    welcome_text = (
        f"<b>سلام {user_name} عزیز! 👋</b>\n\n"
        f"به ربات مدیریت و تولید محتوای خودکار <b>کافینت آنلاین ایرباکس VIP</b> خوش آمدید.\n\n"
        f"با کلیک روی دکمه زیر می‌توانید به صورت هوشمند یک پست جذاب (تصویر + متن علمی/ادبی/آموزنده) تولید کرده و مستقیماً به کانال <code>{config.TELEGRAM_CHANNEL_ID}</code> ارسال کنید."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "⚠️ شما دسترسی مدیریت برای ارسال پست به کانال را ندارید.", show_alert=True)
        return

    if call.data == "publish_now":
        bot.answer_callback_query(call.id, "⏳ در حال تولید پست و ارسال به کانال...")
        try:
            post_data = generate_random_post()
            topic = post_data["topic"]
            
            if database.is_topic_recently_published(topic, hours=12):
                bot.answer_callback_query(call.id, f"⚠️ موضوع {topic} اخیراً ارسال شده است. لطفاً مجدد تلاش کنید.", show_alert=True)
                return
                
            image_url = get_image_url_for_topic(topic)
            
            # Send photo with caption to the channel
            sent_msg = bot.send_photo(
                chat_id=config.TELEGRAM_CHANNEL_ID,
                photo=image_url,
                caption=post_data["caption"]
            )
            
            # Save post in database
            database.save_post(topic, post_data["caption"], image_url, sent_msg.message_id)
            
            bot.send_message(
                call.message.chat.id,
                f"✅ <b>پست با موفقیت تولید و به کانال ارسال شد!</b>\n\n"
                f"🔗 کانال مقصد: {config.TELEGRAM_CHANNEL_ID}\n"
                f"🆔 شناسه پیام: {sent_msg.message_id}",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            bot.send_message(
                call.message.chat.id,
                f"❌ <b>خطا در ارسال پست به کانال:</b>\n<code>{str(e)}</code>\n\n"
                f"لطفاً اطمینان حاصل کنید که ربات در کانال <code>{config.TELEGRAM_CHANNEL_ID}</code> به‌عنوان <b>Admin</b> اضافه شده است.",
                reply_markup=get_main_menu()
            )

    elif call.data == "preview_post":
        bot.answer_callback_query(call.id, "👀 پیش‌نمایش محتوا:")
        try:
            post_data = generate_random_post()
            image_url = get_image_url_for_topic(post_data["topic"])
            
            bot.send_photo(
                chat_id=call.message.chat.id,
                photo=image_url,
                caption=f"🔍 <b>[پیش‌نمایش پست پیشنهادی]</b>\n\n{post_data['caption']}",
                reply_markup=get_main_menu()
            )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ خطا در نمایش پیش‌نمایش: {e}", reply_markup=get_main_menu())

    elif call.data == "coffeenet_info":
        bot.answer_callback_query(call.id, "اطلاعات کافینت")
        info_text = (
            "📌 <b>کافینت آنلاین ایرباکس VIP (AirboxVIP)</b>\n\n"
            "ارائه‌دهنده خدمات ثبت‌نام‌های اینترنتی، دانشگاهی، مالیاتی، خودرو و خدمات دانشجویی به صورت آنلاین و شتاب‌یافته.\n\n"
            "📢 کانال تلگرام: @airboxvipcoffeenet\n"
            "💬 پشتیبانی: @airboxvip_admin\n"
            "🌐 وب‌سایت رسمی: https://airboxvip.com"
        )
        bot.send_message(call.message.chat.id, info_text, reply_markup=get_main_menu())

if __name__ == "__main__":
    print("==========================================")
    print("  AirboxVIP Telegram Auto-Poster Bot")
    print("  Initializing Database...")
    database.init_db()
    print("  Status: RUNNING 🚀")
    print("==========================================")
    bot.infinity_polling()

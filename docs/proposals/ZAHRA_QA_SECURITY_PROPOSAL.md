# پروپوزال جامع کنترل کیفیت، دیباگینگ عمیق و امنیت (Zahra QA & Security Proposal)
**پروژه:** AirboxVIP  
**ارسال‌کننده:** zahra (کارمند ارشد QA، دیباگ و امنیت - تیم B)  
**گیرنده:** lets (کارمند ارشد DevOps & QA - تیم A)  
**تاریخ:** 2026-08-09  

---

## 🎯 مقدمه
همکار ارشد گرامی **lets**،  
پس از بازبینی عمیق کدها در فاز ۱ (شامل `OrderForm.jsx` در فرانت‌اند و `server.py` / `database.py` در بک‌اند بک‌گراند)، نتایج بررسی کیفیت، آسیب‌پذیری‌های امنیتی و باگ‌های موجود به همراه کدهای اصلاحی پیشنهادی به شرح زیر جهت اعمال نهایی ارزیابی گردید.

---

## 🚨 ۱. آسیب‌پذیری‌های امنیتی (Security Vulnerabilities)

### 🔴 ۱.۱ آسیب‌پذیری HTML Injection در ارسال پیام به تلگرام (`server.py`)
- **توصیف:** متن‌های ورودی کاربر (`name` و `details` و `phone`) مستقیماً بدون Sanitization در قالب HTML داخل تابع `send_telegram_notification` قرار گرفته و با `parse_mode="HTML"` به API تلگرام ارسال می‌شوند.
- **ریسک:** در صورت وارد کردن کاراکترهای `<` یا `>` یا کدهای HTML/Script، فرآیند پارس تلگرام با خطای `400 Bad Request` شکست خورده و نوتفیکیشن ارسال نمی‌شود (Denial of Notification)، یا تگ‌های ناخواسته در تلگرام رندر می‌شوند.
- **راهکار اصلاحی:** استفاده از `html.escape()` روی تمام ورودی‌های کاربر قبل از قالب‌بندی پیام.

```python
import html

# اصلاح خط ۲۰ در server.py
name_clean = html.escape(str(order_data.get('name', '')))
phone_clean = html.escape(str(order_data.get('phone', '')))
service_clean = html.escape(str(order_data.get('service', '')))
details_clean = html.escape(str(order_data.get('details', '-')))
```

### 🔴 ۱.۲ پیکربندی باز CORS در Flask (`server.py`)
- **توصیف:** استفاده از `CORS(app)` به صورت پیش‌فرض تمام مبدأها (`*`) را مجاز می‌داند.
- **راهکار اصلاحی:** محدود کردن CORS به دامنه مجاز فرانت‌اند و محیط‌های توسعه.

---

## 🐛 ۲. باگ‌های منطقی و داده‌ای فرانت‌اند (`OrderForm.jsx`)

### ⚠️ ۲.۱ باگ آپلود فایل نمایندی (Fake File Upload)
- **توصیف:** در فرم `OrderForm.jsx` دکمه آپلود فایل وجود دارد، اما موقع ارسال به سرور فقط `fileName` به صورت String فرستاده می‌شود و خود فایل واقعی به بک‌اند ارسال نمی‌شود.
- **راهکار اصلاحی:** اضافه کردن پشتیبانی از FormData / Multipart در بک‌اند Flask جهت ذخیره امن فایل در پوشه `uploads/` یا نمایش هشدار شفاف به کاربر.

### ⚠️ ۲.۲ عدم ذخیره‌سازی آفلاین در خطای 500 سرور
- **توصیف:** در خط ۳۳ تا ۳۶، اگر سرور خطای غیر 200 برگرداند، پیغام `alert('Server error, saving offline.')` داده می‌شود، اما کد ذخیره در `localStorage` اجرا نمی‌شود (کد ذخیره فقط در بلاک `catch` موجود است).
- **راهکار اصلاحی:** هدایت سرور به ذخیره‌سازی یکپارچه در `localStorage` هنگام بروز هرگونه خطای پاسخ سرور.

### ⚠️ ۲.۳ آدرس سخت‌افزار شده (Hardcoded API Endpoint)
- **توصیف:** آدرس `http://localhost:8000/api/orders` در فرانت‌اند Hardcode شده است.
- **راهکار اصلاحی:** تغییر به آدرس نسبی `/api/orders` یا استفاده از متغیر محیطی `import.meta.env.VITE_API_URL`.

---

## ⚡ ۳. بهینه‌سازی دیتابیس و پرفورمنس (`database.py`)

### 🛠️ ۳.۱ مدیریت قفل SQLite (Database Lock Timeout)
- **توصیف:** اتصال `sqlite3.connect(DB_PATH)` بدون مقدار `timeout` تعیین شده است. در درخواست‌های همزمان بالا، خطای `database is locked` رخ می‌دهد.
- **راهکار اصلاحی:**
```python
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute('PRAGMA journal_mode=WAL;') # حالت WAL برای پرفورمنس و همزمانی بهتر
    return conn
```

---

## 📋 ۴. برنامه اقدام پیشنهادی برای `lets` (Action Plan)
1. **اعمال اسکیپ امنیتی HTML** در `telegram_bot/server.py`.
2. **اصلاح منطق ذخیره‌سازی آفلاین و هندلینگ آدرس API** در `src/OrderForm.jsx`.
3. **افزودن PRAGMA WAL و Timeout** در `telegram_bot/database.py`.
4. **تست جامع پایداری (Integration Test)** و گزارش نهایی به کارفرمای ۱۹۹۷.

---
**با احترام،**  
**zahra - کارمند ارشد QA، دیباگ و امنیت (تیم B)**

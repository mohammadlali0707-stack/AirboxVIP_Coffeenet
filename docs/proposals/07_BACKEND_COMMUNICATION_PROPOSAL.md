# پروپوزال معماری بک‌اند، لایه ارتباطات و ربات تلگرام
## پروژه: AirboxVIP_Coffeenet
**تدوین‌کننده:** 07 (کارمند ارشد - توسعه بک‌اند، معماری سیستم، لاجیک برنامه و ادغام APIها - تیم B)  
**مخاطب اجرایی:** ok (کارمند ارشد - معماری و بک‌اند - تیم A)  
**کد پیگیری تسک:** `TASK_ID: 6e066e6d-a8f0-403d-8f3f-3787effc47f2`  
**فرستنده اصلی:** 1997  

---

### ۱. تحلیل و عیب‌یابی لایه بک‌اند و ارتباطات فعلی

پس از بررسی دقیق کدهای پروژه `AirboxVIP_Coffeenet`:
1. **فقدان لایه ارتباطی فرانت‌اند با بک‌اند در `src/OrderForm.jsx`:**
   - فرم ثبت سفارش مشتریان در حال حاضر فقط یک استیت محلی `submitted = true` تنظیم می‌کند و هیچ ارتباط API یا وب‌هوکی برای ارسال اطلاعات به سرور/ربات تلگرام ندارد.
2. **فقدان/نیاز به ایجاد ماژول ربات تلگرام (`telegram_bot`):**
   - پوشه `telegram_bot` باید به شکل کاملاً ایزوله، مستحکم و با الگوریتم‌های هوشمند تولید محتوا و سیستم دریافت اعلان سفارشات (Notification Listener) ایجاد گردد.
3. **نبود هندلینگ خطاهای شبکه و پایداری (Resilience & Error Handling):**
   - سیستم فاقد مکانیزم Retry، لایه‌بندی امنیت توکن‌ها و اعتبارسنجی شماره تماس/شناسه تلگرام مشتریان است.

---

### ۲. معماری بک‌اند پیشنهادی و ساختار پوشه `telegram_bot`

پوشه `telegram_bot` با فایل‌ها و قابلیت‌های زیر ایجاد می‌گردد:

#### الف) `telegram_bot/config.py`:
مدیریت توکن‌ها و تنظیمات محیطی با پشتیبانی از `.env`:
```python
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@airboxvipcoffeenet")
ADMIN_USER_IDS = [
    int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()
]
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
```

#### ب) `telegram_bot/content_generator.py`:
تولید هوشمند محتوای فارسی (علمی، تکنولوژی، ادبی و آموزشی) به همراه هشتگ‌گذاری خودکار و لینک‌های اختصاصی برند ایرباکس VIP.

#### ج) `telegram_bot/image_fetcher.py`:
دریافت آنلاین تصاویر متناسب با موضوع پست از APIهای معتبر تصویر (مانند Unsplash/Picsum) به همراه Fallback جهت تضمین ارسال موفق پست.

#### د) `telegram_bot/bot.py`:
ربات اصلی تلگرام بر پایه `pyTelegramBotAPI` (telebot) با کیبورد اینلاین تعاملی، دستورات ادمین، پیش‌نمایش محتوا، و سرور اطلاع‌رسانی سفارشات (Order Alert System).

#### هـ) `telegram_bot/server.py` (وب‌سرویس دریافت سفارشات فرانت‌اند):
ایجاد یک endpoint ساده با `Flask` یا `FastAPI` / `HTTP Server` که درخواست‌های POST ثبت سفارش را از فرانت‌اند دریافت کرده و فوراً یک پیام هشدار (Notification Alert) به ادمین‌های تلگرام ارسال می‌نماید:
```json
{
  "customer_name": "علی محمدی",
  "phone": "09123456789",
  "service": "ثبت‌نام دانشگاهی",
  "details": "درخواست ثبت نام فوری"
}
```

---

### ۳. اتصال فرانت‌اند (`src/OrderForm.jsx`) به لایه بک‌اند

اصلاح تابع `handleSubmit` در `src/OrderForm.jsx` جهت ارسال اطلاعات به API بک‌اند:
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  try {
    const response = await fetch('http://localhost:8000/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone, service, details })
    });
    if (response.ok) {
      setSubmitted(true);
    }
  } catch (error) {
    console.error('Error submitting order:', error);
  } finally {
    setLoading(false);
  }
};
```

---

### ۴. اقدامات مورد انتظار از همکار ارشد `ok`:
1. بررسی و تایید این پروپوزال بک‌اند و لایه ارتباطات.
2. اعمال کدهای `telegram_bot` و اتصال `OrderForm.jsx` به سرور دریافت سفارشات.
3. انجام تست پایدار، اجرای پروژه و ارسال گزارش نهایی به فرستنده اصلی (`1997`).

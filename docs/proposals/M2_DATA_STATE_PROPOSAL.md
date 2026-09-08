# پروپوزال جامع مدیریت وضعیت (State Management) و پایداری داده‌ها
## پروژه: AirboxVIP_Coffeenet (Vite + React)
**تدوین‌کننده:** M2 (کارمند ارشد - مهندسی داده و مدیریت وضعیت - تیم B)  
**مخاطب اجرایی:** ngocg (کارمند ارشد - تیم A)  
**شناسه پیگیری:** `TASK_ID: 9fb936bd-82cd-49d8-8137-8a71ab2ceb10`  
**فرستنده:** 1997  

---

### ۱. خلاصه ارزیابی معماری و جریان داده‌ها
در بررسی ساختار فعلی پروژه فرانت‌اند در مسیر `C:\Antigravity\Project\AirboxVIP_Coffeenet`:

1. **ناپایداری زبان (`LanguageContext.jsx`):**
   - ذخیره‌سازی وضعیت صرفاً در رم (`useState('fa')`). نیاز به Persistence در `localStorage` و به‌روزرسانی اتریبیوت‌های استاندارد `dir` و `lang` روی تگ `<html>`.
2. **فرم سفارشات غیرکنترل‌شده و بدون پایگاه ذخیره (`OrderForm.jsx`):**
   - عدم وجود فیلدهای ایمیل و توضیحات تکمیلی (که در `translations.js` آماده‌اند اما در فرم وجود ندارند).
   - عدم ذخیره‌سازی داده‌های فرم در State و نبود تاریخچه سفارشات محلی (Local Submission Queue / Storage).

---

### ۲. طرح تفصیلی تغییرات و کد اجرایی

#### الف) اصلاح `src/LanguageContext.jsx`:
- خواندن وضعیت اولیه از `localStorage.getItem('airbox_lang') || 'fa'`
- ذخیره تغییرات زبان در `localStorage.setItem('airbox_lang', lang)`
- تنظیم مستقیم `document.documentElement.lang = lang` و `document.documentElement.dir = (lang === 'fa' ? 'rtl' : 'ltr')`

#### ب) ارتقای `src/OrderForm.jsx`:
- کنترل‌شده کردن ورودی‌ها با فرم‌دیتا شامل:
  - `name`: نام و نام خانوادگی
  - `email`: آدرس ایمیل / راه ارتباطی
  - `service`: نوع خدمت انتخابی
  - `details`: توضیحات تکمیلی
  - `file`: فایل آپلودی
- ذخیره سابقه سفارش در `localStorage` تحت کلید `airbox_orders` با ساختار:
  ```json
  [
    {
      "id": "ORD-1723456789",
      "name": "...",
      "email": "...",
      "service": "...",
      "details": "...",
      "fileName": "...",
      "createdAt": "2026-08-09T18:00:00Z",
      "status": "received"
    }
  ]
  ```
- نمایش پیام موفقیت حاوی شماره پیگیری یکتا (Tracking ID) و دکمه ثبت سفارش جدید (Reset).

---

### ۳. برنامه تأیید و اعتبارسنجی:
- اجرای دستور `npm run build` در پوشه پروژه جهت تضمین عدم وجود خطای تایپ یا لینت.
- بررسی عملکرد ذخیره‌سازی در مرورگر و پایداری داده‌ها پس از رفرش.

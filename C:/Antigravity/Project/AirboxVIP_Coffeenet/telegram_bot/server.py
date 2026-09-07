import os
import requests
import html
from flask import Flask, request, jsonify
from flask_cors import CORS
import config
import database

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Make sure DB is initialized
database.init_db()

def send_telegram_notification(order_data):
    """Send notification to admin group or channel"""
    if config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or not config.TELEGRAM_BOT_TOKEN:
        print("Warning: Telegram bot token not set. Skipping notification.")
        return
        
    name = html.escape(str(order_data.get('name', '')))
    phone = html.escape(str(order_data.get('phone', '')))
    service = html.escape(str(order_data.get('service', '')))
    details = html.escape(str(order_data.get('details', '-')))
    
    text = (
        f"🚨 <b>سفارش جدید ثبت شد!</b>\n\n"
        f"👤 نام: {name}\n"
        f"📞 تماس: {phone}\n"
        f"🛠 نوع خدمت: {service}\n"
        f"📝 توضیحات: {details}\n"
    )
    
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Send to all admins
    if config.ADMIN_USER_IDS:
        for admin_id in config.ADMIN_USER_IDS:
            try:
                requests.post(url, json={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
            except Exception as e:
                print(f"Failed to send to admin {admin_id}: {e}")
    else:
        # Fallback to channel or default if no admins configured
        try:
            requests.post(url, json={
                "chat_id": config.TELEGRAM_CHANNEL_ID,
                "text": text,
                "parse_mode": "HTML"
            })
        except Exception as e:
            print(f"Failed to send notification: {e}")

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        service = data.get('service')
        details = data.get('details', '')
        
        if not name or not phone or not service:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
            
        # Save to DB
        order_id = database.add_order(name, phone, service, details)
        
        # Send Alert
        send_telegram_notification(data)
        
        return jsonify({"success": True, "order_id": order_id}), 201
    except Exception as e:
        print("Error processing order:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = config.SERVER_PORT
    print(f"Starting AirboxVIP Notification Server on port {port}...")
    app.run(host='0.0.0.0', port=port)

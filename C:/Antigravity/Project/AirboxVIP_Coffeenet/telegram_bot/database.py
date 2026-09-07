import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'airbox.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table 1: published_posts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            caption TEXT,
            image_url TEXT,
            message_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table 2: customer_orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            service_type TEXT,
            details TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_post(topic, caption, image_url, message_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO published_posts (topic, caption, image_url, message_id)
        VALUES (?, ?, ?, ?)
    ''', (topic, caption, image_url, message_id))
    conn.commit()
    conn.close()

def is_topic_recently_published(topic, hours=24):
    conn = get_connection()
    cursor = conn.cursor()
    time_threshold = datetime.datetime.now() - datetime.timedelta(hours=hours)
    cursor.execute('''
        SELECT COUNT(*) FROM published_posts 
        WHERE topic = ? AND created_at > ?
    ''', (topic, time_threshold.strftime('%Y-%m-%d %H:%M:%S')))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def add_order(customer_name, phone, service_type, details=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customer_orders (customer_name, phone, service_type, details)
        VALUES (?, ?, ?, ?)
    ''', (customer_name, phone, service_type, details))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

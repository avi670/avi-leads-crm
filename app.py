from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('leads.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # יצירת טבלה מורחבת
    conn.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  phone TEXT, 
                  status TEXT DEFAULT 'חדש', 
                  source TEXT DEFAULT 'מנואל',
                  product TEXT DEFAULT '-',
                  created_at TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM leads ORDER BY id DESC').fetchall()
    
    # חישוב סטטיסטיקות פשוטות
    stats = {
        'total': len(leads),
        'new': len([l for l in leads if l['status'] == 'חדש']),
        'in_progress': len([l for l in leads if l['status'] == 'בטיפול'])
    }
    
    conn.close()
    return render_template('index.html', leads=leads, stats=stats)

@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.get_json()
    if not data: return "No data", 400
    
    name = data.get('name', 'Unknown')
    phone = data.get('phone', 'Unknown')
    source = data.get('source', 'פייסבוק/מייק')
    product = data.get('product', '-')
    created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, phone, source, product, created_at) VALUES (?, ?, ?, ?, ?)',
                 (name, phone, source, product, created_at))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

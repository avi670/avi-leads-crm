from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# פונקציה ליצירת בסיס הנתונים - הפעם היא תרוץ תמיד
def init_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leads 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, status TEXT DEFAULT 'חדש')''')
    conn.commit()
    conn.close()

# קריאה לפונקציה מיד כשהקוד עולה
init_db()

@app.route('/')
def index():
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM leads ORDER BY id DESC')
        leads = cursor.fetchall()
        conn.close()
        return render_template('index.html', leads=leads)
    except Exception as e:
        return f"Error: {e}"

@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.json
    if not data:
        return "No data", 400
    
    name = data.get('name', 'Unknown')
    phone = data.get('phone', 'Unknown')
    
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO leads (name, phone) VALUES (?, ?)', (name, phone))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    # הגדרת פורט דינמי עבור Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

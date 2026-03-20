from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# פונקציה ליצירת בסיס הנתונים
def init_db():
    try:
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS leads 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, status TEXT DEFAULT 'חדש')''')
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")

# קריאה לפונקציה מיד כשהקובץ נטען - זה קריטי ל-Render!
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
        return f"יש בעיה בטעינת הטבלה: {e}", 500

@app.route('/webhook', methods=['POST'])
def receive_lead():
    try:
        data = request.get_json()
        if not data:
            return "No data received", 400
        
        name = data.get('name', 'Unknown')
        phone = data.get('phone', 'Unknown')
        
        conn = sqlite3.connect('leads.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO leads (name, phone) VALUES (?, ?)', (name, phone))
        conn.commit()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

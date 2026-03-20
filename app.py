from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# פונקציה ליצירת בסיס הנתונים
def init_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leads 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, status TEXT DEFAULT 'חדש')''')
    conn.commit()
    conn.close()

# דף הבית - מציג את הטבלה
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
        return f"שגיאה בטעינת הדף: {e}"

# כתובת לקבלת לידים חדשים
@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.json
    if not data:
        return "No data received", 400
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO leads (name, phone) VALUES (?, ?)', (data.get('name'), data.get('phone')))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

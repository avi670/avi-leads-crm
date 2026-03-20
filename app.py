from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import requests
import os

app = Flask(__name__)

# פונקציה ליצירת חיבור לבסיס הנתונים (מחזירה אובייקט עם שמות עמודות)
def get_db_connection():
    conn = sqlite3.connect('leads.db')
    conn.row_factory = sqlite3.Row  # קריטי כדי לקרוא לפי שם (כמו lead['name'])
    return conn

# פונקציה ליצירת בסיס הנתונים - חייבת לרוץ מיד כשהשרת עולה
def init_db():
    conn = get_db_connection()
    # יצירת טבלה מורחבת (שמנוע ה-CRM צריך)
    conn.execute('''CREATE TABLE IF NOT EXISTS leads 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      name TEXT, 
                      phone TEXT, 
                      status TEXT DEFAULT 'חדש', 
                      source TEXT DEFAULT 'מנואל',
                      product TEXT DEFAULT '-')''')
    conn.commit()
    conn.close()

# הפעלת בסיס הנתונים מיד עם עליית השרת
init_db()

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        # משיכת כל הלידים, המסודרים מהחדש לישן
        leads_raw = conn.execute('SELECT * FROM leads ORDER BY id DESC').fetchall()
        # המרת התוצאה הגולמית לרשימת מילונים של פייתון
        leads = [dict(ix) for ix in leads_raw]
        conn.close()
        return render_template('index.html', leads=leads)
    except Exception as e:
        return f"שגיאה חמורה בטעינת האתר: {e}"

# כתובת חדשה לקבלת לידים דרך הטופס באתר (עבור הכפתור הכחול)
@app.route('/add_lead_manual', methods=['POST'])
def add_lead_manual():
    try:
        # קבלת המידע מהטופס הרגיל ב-HTML
        name = request.form.get('name')
        phone = request.form.get('phone')
        source = request.form.get('source', 'מנואל')
        product = request.form.get('product', '-')

        if not name or not phone:
            return "שגיאה: חייבים שם וטלפון", 400

        conn = get_db_connection()
        conn.execute('INSERT INTO leads (name, phone, source, product) VALUES (?, ?, ?, ?)',
                     (name, phone, source, product))
        conn.commit()
        conn.close()
        # אחרי ההוספה, החזרת המשתמש לדף הבית
        return redirect('/')
    except Exception as e:
        return f"שגיאה בהוספת הליד: {e}", 500

# כתובת לקבלת לידים אוטומטיים (מ-Make/Webhooks)
@app.route('/webhook', methods=['POST'])
def receive_lead():
    try:
        # כאן אנחנו מצפים ל-JSON
        data = request.get_json()
        if not data: return "No data", 400
        conn = get_db_connection()
        conn.execute('INSERT INTO leads (name, phone, source, product) VALUES (?, ?, ?, ?)',
                     (data.get('name'), data.get('phone'), data.get('source', 'אוטומטי'), data.get('product', '-')))
        conn.commit()
        conn.close()
        return "OK", 200
    except Exception as e:
        return f"Webhook Error: {e}", 500

if __name__ == '__main__':
    # Render צריך את הפורט הזה
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

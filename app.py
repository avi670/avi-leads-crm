from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('leads.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT, status TEXT DEFAULT 'חדש', 
                  source TEXT DEFAULT 'מנואל', product TEXT DEFAULT '-')''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    leads_raw = conn.execute('SELECT * FROM leads ORDER BY id DESC').fetchall()
    leads = [dict(ix) for ix in leads_raw]
    
    # חישוב סטטיסטיקה
    total = len(leads)
    new = len([l for l in leads if l['status'] == 'חדש'])
    meetings = len([l for l in leads if l['status'] == 'נקבעה פגישה'])
    closed = len([l for l in leads if l['status'] == 'נסגר'])
    
    # חישוב אחוז המרה (נסגר מתוך סה"כ)
    conv_rate = round((closed / total * 100), 1) if total > 0 else 0
    
    stats = {
        'total': total,
        'new': new,
        'meetings': meetings,
        'closed': closed,
        'conv_rate': conv_rate
    }
    
    conn.close()
    return render_template('index.html', leads=leads, stats=stats)

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    lead_id = data.get('id')
    new_status = data.get('status')
    
    conn = get_db_connection()
    conn.execute('UPDATE leads SET status = ? WHERE id = ?', (new_status, lead_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/add_lead_manual', methods=['POST'])
def add_lead_manual():
    name = request.form.get('name')
    phone = request.form.get('phone')
    source = request.form.get('source', 'מנואל')
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, phone, source) VALUES (?, ?, ?)', (name, phone, source))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, phone, source) VALUES (?, ?, ?)',
                 (data.get('name'), data.get('phone'), data.get('source', 'אוטומטי')))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

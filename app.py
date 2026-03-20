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
    # יצירת הטבלה אם לא קיימת
    conn.execute('''CREATE TABLE IF NOT EXISTS leads 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, phone TEXT, status TEXT DEFAULT 'חדש', 
                  source TEXT DEFAULT 'מנואל', notes TEXT DEFAULT '')''')
    
    # בדיקה אם עמודת notes קיימת (למקרה שמעדכנים בסיס נתונים קיים)
    try:
        conn.execute('SELECT notes FROM leads LIMIT 1')
    except sqlite3.OperationalError:
        conn.execute('ALTER TABLE leads ADD COLUMN notes TEXT DEFAULT ""')
        
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    
    if search_query:
        query = "SELECT * FROM leads WHERE name LIKE ? OR phone LIKE ? OR source LIKE ? ORDER BY id DESC"
        leads_raw = conn.execute(query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        leads_raw = conn.execute('SELECT * FROM leads ORDER BY id DESC').fetchall()
        
    leads = [dict(ix) for ix in leads_raw]
    
    # סטטיסטיקות
    total = len(leads)
    closed = len([l for l in leads if l['status'] == 'נסגר'])
    conv_rate = round((closed / total * 100), 1) if total > 0 else 0
    
    stats = {
        'total': total,
        'new': len([l for l in leads if l['status'] == 'חדש']),
        'meetings': len([l for l in leads if l['status'] == 'נקבעה פגישה']),
        'closed': closed,
        'conv_rate': conv_rate
    }
    conn.close()
    return render_template('index.html', leads=leads, stats=stats, search_query=search_query)

@app.route('/update_lead', methods=['POST'])
def update_lead():
    data = request.get_json()
    lead_id = data.get('id')
    field = data.get('field') # status או notes
    value = data.get('value')
    
    conn = get_db_connection()
    if field == 'status':
        conn.execute('UPDATE leads SET status = ? WHERE id = ?', (value, lead_id))
    elif field == 'notes':
        conn.execute('UPDATE leads SET notes = ? WHERE id = ?', (value, lead_id))
    
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/add_lead_manual', methods=['POST'])
def add_lead_manual():
    name = request.form.get('name')
    phone = request.form.get('phone')
    source = request.form.get('source', 'מנואל')
    notes = request.form.get('notes', '')
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, phone, source, notes) VALUES (?, ?, ?, ?)', (name, phone, source, notes))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.get_json()
    # תמיכה בשדה 'source' מה-webhook (למשל מ-Make)
    source = data.get('source', 'קמפיין אוטומטי')
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, phone, source) VALUES (?, ?, ?)',
                 (data.get('name'), data.get('phone'), source))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

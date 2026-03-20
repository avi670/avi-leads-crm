from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import requests
import os

app = Flask(__name__)

# הגדרות Green API - שים כאן את המספרים שלך!
ID_INSTANCE = '7105325147' 
API_TOKEN_INSTANCE = '6af985b2e4404f4e8de86065dfb7f99bfa54ae1d405149a484'

# יצירת בסיס הנתונים (הטבלה של הלידים)
def init_db():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS leads 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, status TEXT DEFAULT 'חדש')''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads ORDER BY id DESC')
    leads = cursor.fetchall()
    conn.close()
    return render_template('index.html', leads=leads)

@app.route('/webhook', methods=['POST'])
def receive_lead():
    data = request.json
    conn = sqlite3.connect('leads.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO leads (name, phone) VALUES (?, ?)', (data['name'], data['phone']))
    conn.commit()
    conn.close()
    return "OK", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

# Database Schema and API for Sophia Inspections
# Component 3 of 4 - 25 RTC

import sqlite3

def init_db():
    conn = sqlite3.connect('sophia.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS inspections (miner TEXT, verdict TEXT, confidence REAL, ts INTEGER)')
    conn.commit()
    conn.close()

def save_inspection(miner, result):
    conn = sqlite3.connect('sophia.db')
    c = conn.cursor()
    c.execute('INSERT INTO inspections VALUES (?,?,?,?)', (miner, result['verdict'], result['confidence'], result['timestamp']))
    conn.commit()
    conn.close()

def get_status(miner_id):
    conn = sqlite3.connect('sophia.db')
    c = conn.cursor()
    c.execute('SELECT * FROM inspections WHERE miner=? ORDER BY ts DESC LIMIT 1', (miner_id,))
    row = c.fetchone()
    conn.close()
    return {"miner": miner_id, "latest": row}

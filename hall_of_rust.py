# Hall of Rust Flask API

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Initialize the SQLite database (if it doesn't exist)
try:
    conn = sqlite3.connect('hall_of_rust.db')
except Exception as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

cursor = conn.cursor()

# Create table if it doesn't exist
create_table_query = '''
CREATE TABLE IF NOT EXISTS hall_of_rust (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rtc_earned REAL DEFAULT 0.0,
    is_alive BOOLEAN DEFAULT True
)
'''
cursor.execute(create_table_query)
conn.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Missing name'}), 400
    
    cursor.execute('INSERT INTO hall_of_rust (name, rtc_earned) VALUES (?, ?)', (data['name'], 0.0))
    conn.commit()
    
    return jsonify({'success': 'Registered', 'id': cursor.lastrowid})

@app.route('/alive/<int:id>', methods=['PUT'])
def alive(id):
    data = request.get_json()
    if not data or 'is_alive' not in data:
        return jsonify({'error': 'Missing is_alive'}), 400
    
    cursor.execute('UPDATE hall_of_rust SET is_alive=? WHERE id=?', (data['is_alive'], id))
    conn.commit()
    
    return jsonify({'success': 'Updated'})

@app.route('/memorial/<int:id>', methods=['PUT'])
def memorial(id):
    data = request.get_json()
    if not data or 'eulogy' not in data:
        return jsonify({'error': 'Missing eulogy'}), 400
    
    # Sanitize the eulogy text
    sanitized_eulogy = sanitize_text(data['eulogy'])
    
    cursor.execute('UPDATE hall_of_rust SET eulogy=? WHERE id=?', (sanitized_eulogy, id))
    conn.commit()
    
    return jsonify({'success': 'Updated'})

@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    cursor.execute('SELECT name, rtc_earned FROM hall_of_rust ORDER BY rtc_earned DESC')
    results = cursor.fetchall()
    
    leaderboards = []
    for row in results:
        leaderboards.append({
            'name': row[0],
            'rtc_earned': row[1]
        })
    
    return jsonify(leaderboard)

if __name__ == '__main__':
    app.run(debug=True)
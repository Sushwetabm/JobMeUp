from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    # Table for questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            likes INTEGER DEFAULT 0,
            dislikes INTEGER DEFAULT 0
        )
    ''')
    # Table for replies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            reply TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database on app startup
init_db()

@app.route('/')
def index():
    return render_template('communication.html')

# Submit a question
@app.route('/submit_question', methods=['POST'])
def submit_question():
    question = request.form['question']
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO questions (question) VALUES (?)', (question,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Submit a reply
@app.route('/submit_reply/<int:question_id>', methods=['POST'])
def submit_reply(question_id):
    reply = request.form['reply']
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO replies (question_id, reply) VALUES (?, ?)', (question_id, reply))
    conn.commit()
    conn.close()
    return 'Reply submitted successfully!'

# Like or dislike a question
@app.route('/vote/<int:question_id>/<action>', methods=['POST'])
def vote(question_id, action):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    if action == 'like':
        cursor.execute('UPDATE questions SET likes = likes + 1 WHERE id = ?', (question_id,))
    elif action == 'dislike':
        cursor.execute('UPDATE questions SET dislikes = dislikes + 1 WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    return 'Vote submitted!'

# Fetch questions with their replies
@app.route('/get_questions_with_replies', methods=['GET'])
def get_questions_with_replies():
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions')
    questions = cursor.fetchall()
    
    result = []
    for question in questions:
        cursor.execute('SELECT * FROM replies WHERE question_id = ?', (question[0],))
        replies = cursor.fetchall()
        result.append({'question': question, 'replies': replies})
    
    conn.close()
    return jsonify(result)

# Delete a question (developer only)
@app.route('/delete_question/<int:id>', methods=['POST'])
def delete_question(id):
    conn = sqlite3.connect('questions.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM replies WHERE question_id = ?', (id,))
    cursor.execute('DELETE FROM questions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return 'Question deleted successfully!'

if __name__ == '__main__':
    app.run(debug=True)

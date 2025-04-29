from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key_here'

# Database connection helper
def get_db():
    conn = sqlite3.connect('hw13.db')
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

# ADD THIS DASHBOARD ROUTE
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    quizzes = conn.execute('SELECT * FROM quizzes').fetchall()
    conn.close()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db()
            conn.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)',
                        (request.form['first_name'], request.form['last_name']))
            conn.commit()
            flash('Student added successfully!')
            return redirect(url_for('dashboard'))
        except:
            flash('Error adding student!')
            conn.rollback()
        finally:
            conn.close()
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db()
            conn.execute('INSERT INTO quizzes (subject, num_questions, date) VALUES (?, ?, ?)',
                        (request.form['subject'], request.form['num_questions'], request.form['date']))
            conn.commit()
            flash('Quiz added successfully!')
            return redirect(url_for('dashboard'))
        except:
            flash('Error adding quiz!')
            conn.rollback()
        finally:
            conn.close()
    return render_template('add_quiz.html')

@app.route('/student/<int:student_id>')
def student_results(student_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    results = conn.execute('''
        SELECT quizzes.subject, quizzes.date, results.score 
        FROM results 
        JOIN quizzes ON results.quiz_id = quizzes.id 
        WHERE student_id = ?
    ''', (student_id,)).fetchall()
    conn.close()
    
    return render_template('student_results.html', student=student, results=results)

@app.route('/results/add', methods=['GET', 'POST'])
def add_result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db()
    if request.method == 'POST':
        try:
            conn.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)',
                        (request.form['student_id'], request.form['quiz_id'], request.form['score']))
            conn.commit()
            flash('Quiz result added successfully!')
            return redirect(url_for('dashboard'))
        except:
            flash('Error adding quiz result!')
            conn.rollback()
        finally:
            conn.close()
    else:
        students = conn.execute('SELECT id, first_name, last_name FROM students').fetchall()
        quizzes = conn.execute('SELECT id, subject FROM quizzes').fetchall()
        conn.close()
        return render_template('add_result.html', students=students, quizzes=quizzes)
    
    if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5001)


from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import pandas as pd
from fpdf import FPDF
from utils import generate_study_plan_ai  # Add to your imports
import os
import cohere
from flask import Flask, render_template, request, redirect, url_for
from utils import get_student_data, generate_study_plan_ai


app = Flask(__name__)
app.secret_key = 'SECRET_KEY'  # Change to a strong key!

# ------------------------ DATABASE SETUP ------------------------
def init_db():
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )''')

    # Create students table
    # Create students table (modify if necessary)
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        serial_number INTEGER PRIMARY KEY,
                        name TEXT,
                        roll_number TEXT UNIQUE,
                        subject1 INTEGER,
                        subject2 INTEGER,
                        subject3 INTEGER,
                        subject4 INTEGER,
                        subject5 INTEGER
                    )''')

    
    # Create a default user
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", 
                   ('admin', 'admin123'))

    conn.commit()
    conn.close()

init_db()

# ------------------------ LOGIN ------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        data = cursor.fetchone()
        conn.close()
        if data:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# ------------------------ LOGOUT ------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ------------------------ DASHBOARD ------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    keyword = request.args.get('search', '')
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    if keyword:
        cursor.execute("SELECT * FROM students WHERE name LIKE ? OR roll_number LIKE ?", 
                       (f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    student_data = students

    return render_template('dashboard.html', students=student_data, keyword=keyword)


# ------------------------ ADD STUDENT ------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        subject1 = int(request.form['subject1'])
        subject2 = int(request.form['subject2'])
        subject3 = int(request.form['subject3'])
        subject4 = int(request.form['subject4'])
        subject5 = int(request.form['subject5'])
        
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()

        # Get the next available serial number
        cursor.execute("SELECT MAX(serial_number) FROM students")
        max_serial_number = cursor.fetchone()[0]
        next_serial_number = max_serial_number + 1 if max_serial_number else 1

        # Insert student with the new serial number
        cursor.execute('''INSERT INTO students 
                          (serial_number, name, roll_number, subject1, subject2, subject3, subject4, subject5) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (next_serial_number, name, roll_number, subject1, subject2, subject3, subject4, subject5))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_student.html')

# ------------------------ EDIT STUDENT ------------------------
@app.route('/edit/<int:serial_number>', methods=['GET', 'POST'])
def edit_student(serial_number):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        updated_data = (
            request.form['name'],
            request.form['roll_number'],
            int(request.form['subject1']),
            int(request.form['subject2']),
            int(request.form['subject3']),
            int(request.form['subject4']),
            int(request.form['subject5']),
            serial_number  # Use serial_number instead of id
        )
        cursor.execute('''UPDATE students SET name=?, roll_number=?, subject1=?, subject2=?,
                          subject3=?, subject4=?, subject5=? WHERE serial_number=?''', updated_data)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    else:
        cursor.execute("SELECT * FROM students WHERE serial_number=?", (serial_number,))
        student = cursor.fetchone()
        conn.close()
        return render_template('edit_student.html', student=student)


# ------------------------ DELETE STUDENT ------------------------
@app.route('/delete/<int:serial_number>')
def delete_student(serial_number):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Connect to the database
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    
    # Delete the student by serial_number
    cursor.execute("DELETE FROM students WHERE serial_number=?", (serial_number,))
    
    # Reset serial_number for all students to ensure continuous sequence
    cursor.execute("UPDATE students SET serial_number = serial_number - 1 WHERE serial_number > ?", (serial_number,))
    
    conn.commit()
    conn.close()
    
    # Redirect back to the dashboard
    return redirect(url_for('dashboard'))

# ------------------------ EXPORT TO CSV ------------------------
@app.route('/export/csv')
def export_csv():
    conn = sqlite3.connect('student.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    df.to_csv('students.csv', index=False)
    conn.close()
    return send_file('students.csv', as_attachment=True)

# ------------------------ EXPORT TO XLSX ------------------------
@app.route('/export/xlsx')
def export_xlsx():
    conn = sqlite3.connect('student.db')
    df = pd.read_sql_query("SELECT * FROM students", conn)
    df.to_excel('students.xlsx', index=False)
    conn.close()
    return send_file('students.xlsx', as_attachment=True)

# ------------------------ EXPORT TO PDF ------------------------
@app.route('/export/pdf')
def export_pdf():
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Student Records", ln=True, align='C')

    for s in students:
        row = f"ID: {s[0]} | Name: {s[1]} | Roll: {s[2]} | Marks: {s[3:8]}"
        pdf.cell(200, 10, txt=row, ln=True)

    pdf.output("students.pdf")
    return send_file("students.pdf", as_attachment=True)

# ------------------------ STUDY PLAN GENERATOR ------------------------
# Initialize Cohere API Client
co = cohere.Client('OjrNKaz018zImi1PvWfvIDloG3Jhdlo8P1cIBryO')  # Replace with your API key
@app.route("/study_plan/<int:serial_number>")
def study_plan(serial_number):
    # Fetch student data from the database or student list
    student = get_student_data(serial_number)
    
    if student:
        # Generate the personalized study plan using Cohere's NLP API
        try:
            study_plan_text = generate_study_plan_ai(student)
            return render_template("study_plan.html", student=student, study_plan=study_plan_text)
        except Exception as e:
            print("Error generating study plan:", e)
            return render_template("study_plan.html", student=student, study_plan="Error generating study plan.")
    else:
        return redirect(url_for('dashboard'))

# Add other routes here (dashboard, add_student, etc.)

# ------------------------ RUN APP ------------------------
if __name__ == "__main__":
    app.run(debug=True)
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
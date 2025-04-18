import cohere
import os
import sqlite3

# Initialize Cohere API Client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))  # Replace with your Cohere API key

def generate_study_plan_ai(student):
    name = student[1]
    marks = student[3:8]
    subjects = ['DAA', 'SPM', 'CA', 'GT', 'CN']

    subject_marks = list(zip(subjects, marks))
    weak_subjects = [sub for sub, mark in subject_marks if mark < 60]
    strong_subjects = [sub for sub, mark in subject_marks if mark > 80]

    study_plan_prompt = f"""
    Create a personalized weekly study plan for a student named {name}.
    The student is studying: {', '.join(subjects)}.

    Subjects they are STRONG in: {', '.join(strong_subjects)}.
    Subjects they are WEAK in: {', '.join(weak_subjects)}.

    Focus more time on weak subjects with daily exercises.
    For strong subjects, suggest revision and deeper learning.
    Include weekly goals and a simple daily routine.
    """

    response = co.generate(
        model="command-r-plus",
        prompt=study_plan_prompt,
        max_tokens=300,
        temperature=0.7
    )

    return response.generations[0].text.strip()



def get_student_data(serial_number):
    # Connect to the SQLite database
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE serial_number=?", (serial_number,))
    student = cursor.fetchone()
    conn.close()

    if student is None:
        return None  # Return None if no student is found
    return student

import cohere
import os
import sqlite3

# Initialize Cohere API Client
co = cohere.Client(os.environ.get('COHERE_API_KEY'))  # Replace with your Cohere API key

def generate_study_plan_ai(student):  # Replace with your Cohere API key

    name = student[1]
    # Updated subjects list
    subjects = ['DAA', 'SPM', 'CA', 'GT', 'CN']

    study_plan_prompt = f"""
    Create a personalized study plan for a student named {name} who is studying the following subjects:
    {', '.join(subjects)}.
    The student needs improvement in SPM and GT and excels in DAA. Focus on daily practice for weak subjects and encourage deeper understanding in strong subjects.
    Provide a schedule for each subject with goals for each week.
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

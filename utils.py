import cohere

# Initialize Cohere API Client
co = cohere.Client('OjrNKaz018zImi1PvWfvIDloG3Jhdlo8P1cIBryO')  # Replace with your Cohere API key

def generate_study_plan_ai(student):
    import cohere
    co = cohere.Client('COHERE_API_KEY')  # Replace with your Cohere API key

    name = student[1]
    subjects = ['Math', 'Science', 'English', 'History', 'Geography']

    study_plan_prompt = f"""
    Create a personalized study plan for a student named {name} who is studying the following subjects:
    {', '.join(subjects)}.
    The student needs improvement in Science and History and excels in Math. Focus on daily practice for weak subjects and encourage deeper understanding in strong subjects.
    Provide a schedule for each subject with goals for each week.
    """

    response = co.generate(
        model="command-r-plus",
        prompt=study_plan_prompt,
        max_tokens=300,
        temperature=0.7
    )

    return response.generations[0].text.strip()


import sqlite3

def get_student_data(serial_number):
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE serial_number=?", (serial_number,))
    student = cursor.fetchone()
    conn.close()
    return student


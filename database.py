import sqlite3
import os
import hashlib
import uuid

DB_NAME = "exam_system.db"

def get_db_connection():
    """Establish connection to the SQLite database with Foreign Keys enabled."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password, salt=None):
    """Hash password using SHA-256 with a unique salt."""
    if not salt:
        salt = uuid.uuid4().hex
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def init_db():
    """Initialize database schemas and seed default administrative/student records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'student')),
        full_name TEXT NOT NULL
    )
    """)

    # Create Exams Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        duration_minutes INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create Questions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
        marks INTEGER DEFAULT 1,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
    )
    """)

    # Create Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        exam_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        total_marks INTEGER NOT NULL,
        percentage REAL NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
        FOREIGN KEY (exam_id) REFERENCES exams (id) ON DELETE CASCADE
    )
    """)

    conn.commit()

    # Seed Default Admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_admin, salt_admin = hash_password("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, role, full_name) VALUES (?, ?, ?, ?, ?)",
            ("admin", hashed_admin, salt_admin, "admin", "System Administrator")
        )

    # Seed Default Student if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'student'")
    if not cursor.fetchone():
        hashed_student, salt_student = hash_password("student123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, role, full_name) VALUES (?, ?, ?, ?, ?)",
            ("student", hashed_student, salt_student, "student", "Jane Doe")
        )

    # Seed an initial Sample Exam if no exams exist
    cursor.execute("SELECT * FROM exams")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO exams (title, description, duration_minutes) VALUES (?, ?, ?)",
            ("General Python MCQ Exam", "An introductory examination covering Python data structures, decorators, and basic loops.", 10)
        )
        exam_id = cursor.lastrowid
        
        sample_questions = [
            ("What is the correct syntax to output 'Hello World' in Python?", "print('Hello World')", "echo('Hello World')", "p('Hello World')", "console.log('Hello World')", "A", 2),
            ("Which of the following is an immutable data type in Python?", "List", "Dictionary", "Tuple", "Set", "C", 2),
            ("How do you start a comments section/line in Python?", "//", "/*", "#", "<!--", "C", 1),
            ("What does the 'len()' function do?", "Returns the data type of an object", "Returns the number of elements in an object", "Returns a list of keys", "Converts object to integer", "B", 1),
            ("Which keyword is used to create a function in Python?", "func", "define", "def", "function", "C", 2)
        ]
        
        for q in sample_questions:
            cursor.execute(
                "INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (exam_id, q[0], q[1], q[2], q[3], q[4], q[5], q[6])
            )

    conn.commit()
    conn.close()

# ----------------- Users CRUD Operations -----------------

def create_user(username, password_hash, salt, role, full_name):
    """Create a new user in the system."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt, role, full_name) VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, salt, role, full_name)
        )
        conn.commit()
        conn.close()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, f"Error creating user: {str(e)}"

def get_user(username):
    """Retrieve user record by username."""
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def get_all_students():
    """Retrieve all student accounts."""
    conn = get_db_connection()
    students = conn.execute("SELECT username, full_name FROM users WHERE role = 'student'").fetchall()
    conn.close()
    return students

def delete_user(username):
    """Delete a user from the system."""
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return True, "User deleted successfully."
    except Exception as e:
        return False, str(e)

# ----------------- Exams CRUD Operations -----------------

def create_exam(title, description, duration_minutes):
    """Create a new exam."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO exams (title, description, duration_minutes) VALUES (?, ?, ?)",
            (title, description, duration_minutes)
        )
        exam_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return exam_id
    except Exception:
        return None

def get_all_exams():
    """Retrieve all created exams with question counts."""
    conn = get_db_connection()
    exams = conn.execute("""
        SELECT e.id, e.title, e.description, e.duration_minutes, e.created_at,
               COUNT(q.id) AS question_count, COALESCE(SUM(q.marks), 0) AS total_marks 
        FROM exams e 
        LEFT JOIN questions q ON e.id = q.exam_id 
        GROUP BY e.id, e.title, e.description, e.duration_minutes, e.created_at
        ORDER BY e.created_at DESC
    """).fetchall()
    conn.close()
    return exams

def get_exam(exam_id):
    """Retrieve details of a single exam."""
    conn = get_db_connection()
    exam = conn.execute("SELECT * FROM exams WHERE id = ?", (exam_id,)).fetchone()
    conn.close()
    return exam

def delete_exam(exam_id):
    """Delete an exam and cascade delete questions/results."""
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# ----------------- Questions CRUD Operations -----------------

def add_question(exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks=1):
    """Add a question to a specific exam."""
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_exam_questions(exam_id):
    """Retrieve all questions for a specific exam."""
    conn = get_db_connection()
    questions = conn.execute("SELECT * FROM questions WHERE exam_id = ? ORDER BY id ASC", (exam_id,)).fetchall()
    conn.close()
    return questions

def delete_question(question_id):
    """Delete a single question."""
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

# ----------------- Results CRUD Operations -----------------

def save_result(username, exam_id, score, total_marks, percentage):
    """Save an exam attempt score."""
    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO results (username, exam_id, score, total_marks, percentage) VALUES (?, ?, ?, ?, ?)",
            (username, exam_id, score, total_marks, percentage)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_user_results(username):
    """Retrieve all results for a specific user."""
    conn = get_db_connection()
    results = conn.execute("""
        SELECT r.id, r.username, r.exam_id, r.score, r.total_marks, r.percentage, r.completed_at,
               e.title AS exam_title, e.duration_minutes
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.username = ?
        ORDER BY r.completed_at DESC
    """, (username,)).fetchall()
    conn.close()
    return results

def get_all_results():
    """Retrieve all results across the entire platform."""
    conn = get_db_connection()
    results = conn.execute("""
        SELECT r.id, r.username, r.exam_id, r.score, r.total_marks, r.percentage, r.completed_at,
               e.title AS exam_title, u.full_name
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        JOIN users u ON r.username = u.username
        ORDER BY r.completed_at DESC
    """).fetchall()
    conn.close()
    return results

# Initialize on import
init_db()

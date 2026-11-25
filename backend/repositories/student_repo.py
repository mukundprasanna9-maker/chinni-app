from backend.repositories.database import get_connection


def create_student(name: str, target_score: int = 235, user_id: int | None = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO students (name, target_score, user_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (name, target_score, user_id))
    conn.commit()
    student_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_student_by_id(student_id)


def get_student_by_id(student_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, name, target_score, created_at FROM students WHERE id = %s"
    cursor.execute(query, (student_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_students(user_id: int | None = None) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    if user_id is not None:
        query = "SELECT id, name, target_score, user_id, created_at FROM students WHERE user_id = %s ORDER BY id ASC"
        cursor.execute(query, (user_id,))
    else:
        # Admin / no filter — return all students
        query = "SELECT id, name, target_score, user_id, created_at FROM students ORDER BY id ASC"
        cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def update_student(student_id: int, name: str, target_score: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "UPDATE students SET name = %s, target_score = %s WHERE id = %s"
    cursor.execute(query, (name, target_score, student_id))
    conn.commit()
    cursor.close()
    conn.close()
    return get_student_by_id(student_id)


def delete_student(student_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM students WHERE id = %s"
    cursor.execute(query, (student_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted

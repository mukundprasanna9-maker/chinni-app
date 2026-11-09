from backend.repositories.database import get_connection


def create_study_plan(
    student_id: int,
    group_id: int | None,
    subject_id: int | None,
    target_date: str,
    planned_hours: float,
    notes: str = "",
) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        INSERT INTO study_plans (student_id, group_id, subject_id, target_date, planned_hours, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (student_id, group_id, subject_id, target_date, planned_hours, notes))
    conn.commit()
    plan_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_study_plan_by_id(plan_id)


def get_study_plan_by_id(plan_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sp.id, sp.student_id, sp.group_id, sp.subject_id, sp.target_date,
               sp.planned_hours, sp.actual_hours, sp.notes, sp.status, sp.created_at,
               s.name AS subject_name, sg.name AS group_name, sg.group_code
        FROM study_plans sp
        LEFT JOIN subjects s ON sp.subject_id = s.id
        LEFT JOIN subject_groups sg ON sp.group_id = sg.id
        WHERE sp.id = %s
    """
    cursor.execute(query, (plan_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_study_plans(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sp.id, sp.student_id, sp.group_id, sp.subject_id, sp.target_date,
               sp.planned_hours, sp.actual_hours, sp.notes, sp.status, sp.created_at,
               s.name AS subject_name, sg.name AS group_name, sg.group_code
        FROM study_plans sp
        LEFT JOIN subjects s ON sp.subject_id = s.id
        LEFT JOIN subject_groups sg ON sp.group_id = sg.id
        WHERE sp.student_id = %s
        ORDER BY sp.target_date DESC, sp.id DESC
    """
    cursor.execute(query, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def update_plan_actual_hours(plan_id: int, actual_hours: float, status: str = "COMPLETED") -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "UPDATE study_plans SET actual_hours = %s, status = %s WHERE id = %s"
    cursor.execute(query, (actual_hours, status, plan_id))
    conn.commit()
    cursor.close()
    conn.close()
    return get_study_plan_by_id(plan_id)


def create_focus_session(
    student_id: int,
    subject_id: int | None,
    group_id: int | None,
    duration_minutes: int,
    notes: str = "",
    adherence_status: str = "COMPLETED",
) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        INSERT INTO focus_sessions (student_id, subject_id, group_id, duration_minutes, notes, adherence_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        query,
        (student_id, subject_id, group_id, duration_minutes, notes, adherence_status),
    )
    conn.commit()
    session_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_focus_session_by_id(session_id)


def get_focus_session_by_id(session_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT fs.id, fs.student_id, fs.subject_id, fs.group_id,
               fs.duration_minutes, fs.adherence_status, fs.notes, fs.completed_at,
               s.name AS subject_name, sg.name AS group_name, sg.group_code
        FROM focus_sessions fs
        LEFT JOIN subjects s ON fs.subject_id = s.id
        LEFT JOIN subject_groups sg ON fs.group_id = sg.id
        WHERE fs.id = %s
    """
    cursor.execute(query, (session_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_focus_sessions(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT fs.id, fs.student_id, fs.subject_id, fs.group_id,
               fs.duration_minutes, fs.adherence_status, fs.notes, fs.completed_at,
               s.name AS subject_name, sg.name AS group_name, sg.group_code
        FROM focus_sessions fs
        LEFT JOIN subjects s ON fs.subject_id = s.id
        LEFT JOIN subject_groups sg ON fs.group_id = sg.id
        WHERE fs.student_id = %s
        ORDER BY fs.completed_at DESC
    """
    cursor.execute(query, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

from backend.repositories.database import get_connection


def create_track(student_id: int, name: str, target_score: int, max_score: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO tracks (student_id, name, target_score, max_score) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (student_id, name, target_score, max_score))
    conn.commit()
    track_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_track_by_id(track_id)


def get_track_by_id(track_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, student_id, name, target_score, max_score, created_at FROM tracks WHERE id = %s"
    cursor.execute(query, (track_id,))
    track = cursor.fetchone()
    cursor.close()
    conn.close()
    return track


def get_tracks_by_student(student_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, student_id, name, target_score, max_score, created_at FROM tracks WHERE student_id = %s ORDER BY id ASC"
    cursor.execute(query, (student_id,))
    tracks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tracks


def create_subject(track_id: int, name: str, code: str, max_marks: int, target_marks: int = 0) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "INSERT INTO subjects (track_id, name, code, max_marks, target_marks) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (track_id, name, code, max_marks, target_marks))
    conn.commit()
    subject_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_subject_by_id(subject_id)


def get_subject_by_id(subject_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, track_id, name, code, max_marks, target_marks FROM subjects WHERE id = %s"
    cursor.execute(query, (subject_id,))
    subject = cursor.fetchone()
    cursor.close()
    conn.close()
    return subject


def get_subjects_by_track(track_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, track_id, name, code, max_marks, target_marks FROM subjects WHERE track_id = %s ORDER BY id ASC"
    cursor.execute(query, (track_id,))
    subjects = cursor.fetchall()
    cursor.close()
    conn.close()
    return subjects


def create_group(
    subject_id: int,
    group_code: str,
    name: str,
    description: str = "",
    weight_percentage: float = 0.0,
) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        INSERT INTO subject_groups (subject_id, group_code, name, description, weight_percentage)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (subject_id, group_code, name, description, weight_percentage))
    conn.commit()
    group_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_group_by_id(group_id)


def get_group_by_id(group_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sg.id, sg.subject_id, sg.group_code, sg.name, sg.description, sg.weight_percentage,
               s.name AS subject_name, s.code AS subject_code, s.track_id
        FROM subject_groups sg
        JOIN subjects s ON sg.subject_id = s.id
        WHERE sg.id = %s
    """
    cursor.execute(query, (group_id,))
    group = cursor.fetchone()
    cursor.close()
    conn.close()
    return group


def get_groups_by_subject(subject_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT id, subject_id, group_code, name, description, weight_percentage
        FROM subject_groups
        WHERE subject_id = %s
        ORDER BY group_code ASC
    """
    cursor.execute(query, (subject_id,))
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return groups


def get_groups_by_track(track_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sg.id, sg.subject_id, sg.group_code, sg.name, sg.description, sg.weight_percentage,
               s.name AS subject_name, s.code AS subject_code
        FROM subject_groups sg
        JOIN subjects s ON sg.subject_id = s.id
        WHERE s.track_id = %s
        ORDER BY s.id ASC, sg.group_code ASC
    """
    cursor.execute(query, (track_id,))
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    return groups


def create_chapter(
    subject_id: int,
    chapter_code: str,
    name: str,
    topics: str = "",
    unit: str = "",
) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        INSERT INTO syllabus_chapters (subject_id, chapter_code, name, topics, unit)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (subject_id, chapter_code, name, topics, unit))
    conn.commit()
    chapter_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return get_chapter_by_id(chapter_id)


def get_chapter_by_id(chapter_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sc.id, sc.subject_id, sc.chapter_code, sc.name, sc.topics, sc.unit,
               s.name AS subject_name, s.code AS subject_code, s.track_id
        FROM syllabus_chapters sc
        JOIN subjects s ON sc.subject_id = s.id
        WHERE sc.id = %s
    """
    cursor.execute(query, (chapter_id,))
    chapter = cursor.fetchone()
    cursor.close()
    conn.close()
    return chapter


def get_chapters_by_subject(subject_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT id, subject_id, chapter_code, name, topics, unit
        FROM syllabus_chapters
        WHERE subject_id = %s
        ORDER BY id ASC
    """
    cursor.execute(query, (subject_id,))
    chapters = cursor.fetchall()
    cursor.close()
    conn.close()
    return chapters


def get_chapters_by_track(track_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sc.id, sc.subject_id, sc.chapter_code, sc.name, sc.topics, sc.unit,
               s.name AS subject_name, s.code AS subject_code
        FROM syllabus_chapters sc
        JOIN subjects s ON sc.subject_id = s.id
        WHERE s.track_id = %s
        ORDER BY s.id ASC, sc.id ASC
    """
    cursor.execute(query, (track_id,))
    chapters = cursor.fetchall()
    cursor.close()
    conn.close()
    return chapters

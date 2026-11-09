from backend.repositories.database import get_connection


def create_test(
    track_id: int,
    test_code: str,
    test_date: str,
    total_score: float,
    max_score: float,
    notes: str = "",
    subject_scores: list[dict] = None,
    group_scores: list[dict] = None,
) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            INSERT INTO tests (track_id, test_code, test_date, total_score, max_score, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (track_id, test_code, test_date, total_score, max_score, notes))
        test_id = cursor.lastrowid

        if subject_scores:
            sub_query = """
                INSERT INTO test_subject_scores (test_id, subject_id, score, max_score, accuracy_percent, time_spent_minutes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            for sub in subject_scores:
                cursor.execute(
                    sub_query,
                    (
                        test_id,
                        sub["subject_id"],
                        sub["score"],
                        sub.get("max_score", 100.0),
                        sub.get("accuracy_percent", 0.0),
                        sub.get("time_spent_minutes", 0),
                    ),
                )

        if group_scores:
            grp_query = """
                INSERT INTO test_group_scores (test_id, group_id, score, max_score)
                VALUES (%s, %s, %s, %s)
            """
            for grp in group_scores:
                cursor.execute(
                    grp_query,
                    (
                        test_id,
                        grp["group_id"],
                        grp["score"],
                        grp.get("max_score", 33.3),
                    ),
                )

        conn.commit()
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        raise e

    cursor.close()
    conn.close()
    return get_test_by_id(test_id)


def get_test_by_id(test_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT id, track_id, test_code, test_type, test_date, total_score, max_score, notes, created_at
        FROM tests
        WHERE id = %s
    """
    cursor.execute(query, (test_id,))
    test = cursor.fetchone()
    if not test:
        cursor.close()
        conn.close()
        return None

    # Fetch subject scores
    sub_query = """
        SELECT tss.id, tss.subject_id, s.name AS subject_name, s.code AS subject_code,
               tss.score, tss.max_score, tss.accuracy_percent, tss.time_spent_minutes
        FROM test_subject_scores tss
        JOIN subjects s ON tss.subject_id = s.id
        WHERE tss.test_id = %s
        ORDER BY s.id ASC
    """
    cursor.execute(sub_query, (test_id,))
    test["subject_scores"] = cursor.fetchall()

    # Fetch group scores
    grp_query = """
        SELECT tgs.id, tgs.group_id, sg.group_code, sg.name AS group_name,
               s.name AS subject_name, s.code AS subject_code,
               tgs.score, tgs.max_score
        FROM test_group_scores tgs
        JOIN subject_groups sg ON tgs.group_id = sg.id
        JOIN subjects s ON sg.subject_id = s.id
        WHERE tgs.test_id = %s
        ORDER BY s.id ASC, sg.group_code ASC
    """
    cursor.execute(grp_query, (test_id,))
    test["group_scores"] = cursor.fetchall()

    cursor.close()
    conn.close()
    return test


def get_tests_by_track(track_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT id, track_id, test_code, test_type, test_date, total_score, max_score, notes, created_at
        FROM tests
        WHERE track_id = %s
        ORDER BY test_date ASC, id ASC
    """
    cursor.execute(query, (track_id,))
    tests = cursor.fetchall()

    for test in tests:
        # Load subject breakdown for each test
        sub_query = """
            SELECT tss.subject_id, s.name AS subject_name, s.code AS subject_code,
                   tss.score, tss.max_score
            FROM test_subject_scores tss
            JOIN subjects s ON tss.subject_id = s.id
            WHERE tss.test_id = %s
            ORDER BY s.id ASC
        """
        cursor.execute(sub_query, (test["id"],))
        test["subject_scores"] = cursor.fetchall()

    cursor.close()
    conn.close()
    return tests


def get_all_group_scores_for_track(track_id: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT t.id AS test_id, t.test_code, t.test_date,
               s.id AS subject_id, s.name AS subject_name, s.code AS subject_code,
               sg.id AS group_id, sg.group_code, sg.name AS group_name,
               tgs.score, tgs.max_score
        FROM test_group_scores tgs
        JOIN tests t ON tgs.test_id = t.id
        JOIN subject_groups sg ON tgs.group_id = sg.id
        JOIN subjects s ON sg.subject_id = s.id
        WHERE t.track_id = %s
        ORDER BY t.test_date ASC, s.id ASC, sg.group_code ASC
    """
    cursor.execute(query, (track_id,))
    scores = cursor.fetchall()
    cursor.close()
    conn.close()
    return scores


def delete_test(test_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    query = "DELETE FROM tests WHERE id = %s"
    cursor.execute(query, (test_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted

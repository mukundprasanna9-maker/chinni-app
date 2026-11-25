"""Spend ranking business logic module.

Teaching rule:
Helps students answer: "Where should I spend my next 10 hours of study?"
Calculates which subject and group (G1, G2, G3) offers the highest marks return.
"""


def rank_groups_to_focus(all_group_scores: list[dict]) -> list[dict]:
    """Ranks subject groups (e.g. Maths G2 Calculus, Physics G1 Mechanics) by marks improvement potential.

    Formulas:
    1. Deficit = max_score - latest_score
    2. Improvement Potential Index = Deficit * (weight_percentage / 100.0)
       (If weight is not specified, defaults to equal 1/3 weight = 0.333)

    Returns a descending list of groups needing focus.
    """
    if not all_group_scores:
        return []

    # Map groups to their latest score
    latest_by_group = {}
    for entry in all_group_scores:
        gid = entry["group_id"]
        # Later tests in the ordered list overwrite earlier ones
        latest_by_group[gid] = entry

    rankings = []
    for gid, data in latest_by_group.items():
        score = float(data.get("score", 0.0))
        max_s = float(data.get("max_score", 33.3))
        weight = float(data.get("weight_percentage") if data.get("weight_percentage") is not None else 33.3)

        deficit = max(0.0, max_s - score)
        # Opportunity index scales deficit by weight
        opportunity_index = round(deficit * (weight / 100.0), 2)
        pct = round((score / max_s) * 100.0, 1) if max_s > 0 else 0.0

        if pct < 60.0:
            priority = "HIGH"
        elif pct < 75.0:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        rankings.append({
            "group_id": gid,
            "group_code": data.get("group_code", ""),
            "group_name": data.get("group_name", ""),
            "subject_name": data.get("subject_name", ""),
            "subject_code": data.get("subject_code", ""),
            "latest_score": score,
            "max_score": max_s,
            "deficit": round(deficit, 2),
            "percentage": pct,
            "opportunity_index": opportunity_index,
            "priority": priority,
        })

    # Sort descending by opportunity index, then by deficit
    rankings.sort(key=lambda x: (x["opportunity_index"], x["deficit"]), reverse=True)
    return rankings


def rank_subjects_to_focus(subjects: list[dict], test_records: list[dict]) -> list[dict]:
    """Ranks subjects (Maths, Physics, Chemistry) by performance gap.

    Formula:
    Deficit = target_marks - latest_score
    """
    if not subjects:
        return []

    # Extract latest test's subject scores if available
    latest_test = test_records[-1] if test_records else None
    latest_scores_by_sub = {}
    if latest_test and "subject_scores" in latest_test:
        for sub_score in latest_test["subject_scores"]:
            latest_scores_by_sub[sub_score["subject_id"]] = float(sub_score["score"])

    ranked = []
    for sub in subjects:
        sid = sub["id"]
        name = sub["name"]
        code = sub["code"]
        target = float(sub.get("target_marks") or 80.0)
        max_m = float(sub.get("max_marks") or 100.0)

        current = latest_scores_by_sub.get(sid, 0.0)
        gap = round(max(0.0, target - current), 2)
        pct = round((current / max_m) * 100.0, 1) if max_m > 0 else 0.0

        ranked.append({
            "subject_id": sid,
            "name": name,
            "code": code,
            "current_score": current,
            "target_score": target,
            "gap_to_target": gap,
            "percentage": pct,
        })

    ranked.sort(key=lambda x: x["gap_to_target"], reverse=True)
    return ranked


def rank_chapters_to_focus(
    chapter_test_records: list[dict],
    focus_sessions: list[dict] | None = None,
) -> list[dict]:
    """Ranks syllabus chapters by deficit and recent timer practice.

    For each chapter included in logged tests, averages the subject percentage
    achieved on tests covering that chapter, then gently credits any completed
    focus timer sessions on that chapter so neglected weak chapters float up
    naturally without prescribing rigid weekly hours.
    """
    if not chapter_test_records:
        return []

    logged_by_chapter = {}
    if focus_sessions:
        for sess in focus_sessions:
            cid = sess.get("chapter_id")
            if cid is not None:
                logged_by_chapter[cid] = logged_by_chapter.get(cid, 0) + int(sess.get("duration_minutes") or 0)

    by_chapter = {}
    for entry in chapter_test_records:
        cid = entry["chapter_id"]
        score = float(entry.get("score", 0.0))
        max_s = float(entry.get("max_score") or 100.0)
        pct = (score / max_s) * 100.0 if max_s > 0 else 0.0

        if cid not in by_chapter:
            by_chapter[cid] = {
                "chapter_id": cid,
                "chapter_code": entry.get("chapter_code", ""),
                "chapter_name": entry.get("chapter_name", ""),
                "subject_id": entry.get("subject_id"),
                "subject_name": entry.get("subject_name", ""),
                "subject_code": entry.get("subject_code", ""),
                "unit": entry.get("unit", ""),
                "pcts": [],
                "latest_score": score,
                "max_score": max_s,
            }
        by_chapter[cid]["pcts"].append(pct)
        by_chapter[cid]["latest_score"] = score
        by_chapter[cid]["max_score"] = max_s

    rankings = []
    for cid, data in by_chapter.items():
        tests_cnt = len(data["pcts"])
        avg_pct = round(sum(data["pcts"]) / tests_cnt, 1)
        deficit = round(max(0.0, 100.0 - avg_pct), 2)
        logged_mins = logged_by_chapter.get(cid, 0)

        # Gentle timer credit so practiced chapters make room for neglected ones
        effort_credit = min(deficit * 0.45, (logged_mins / 60.0) * 6.0)
        effective_deficit = max(1.0, deficit - effort_credit) if deficit > 0 else 1.0
        opportunity_index = round(effective_deficit * (1.0 + 0.1 * (tests_cnt - 1)), 2)

        if avg_pct < 60.0:
            priority = "HIGH"
            cadence_style = "Deep Rebuild" if logged_mins == 0 else "Focused Drill"
            suggested_minutes = 60 if avg_pct < 50.0 else 45
        elif avg_pct < 75.0:
            priority = "MEDIUM"
            cadence_style = "Timed Practice"
            suggested_minutes = 25 if logged_mins >= 45 else 45
        else:
            priority = "LOW"
            cadence_style = "Quick Refresh"
            suggested_minutes = 25

        test_word = "test" if tests_cnt == 1 else "tests"
        timer_note = (
            f"{logged_mins}m logged in timer" if logged_mins > 0 else "No timer blocks logged yet"
        )
        reason = f"Avg {avg_pct:.0f}% across {tests_cnt} {test_word}  •  {timer_note}"

        rankings.append({
            "group_id": cid,
            "chapter_id": cid,
            "group_code": data["chapter_code"],
            "group_name": data["chapter_name"],
            "chapter_code": data["chapter_code"],
            "chapter_name": data["chapter_name"],
            "subject_id": data["subject_id"],
            "subject_name": data["subject_name"],
            "subject_code": data["subject_code"],
            "latest_score": data["latest_score"],
            "max_score": data["max_score"],
            "deficit": deficit,
            "percentage": avg_pct,
            "opportunity_index": opportunity_index,
            "priority": priority,
            "tests_covered": tests_cnt,
            "recent_focus_minutes": logged_mins,
            "cadence_style": cadence_style,
            "suggested_minutes": suggested_minutes,
            "reason": reason,
        })

    rankings.sort(key=lambda x: (x["opportunity_index"], x["deficit"]), reverse=True)
    return rankings

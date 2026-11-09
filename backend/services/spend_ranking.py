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
        weight = float(data.get("weight_percentage") or 33.3)

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

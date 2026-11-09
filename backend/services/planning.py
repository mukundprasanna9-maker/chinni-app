"""Planning and adherence business logic module.

Teaching rule:
Computes study plan adherence metrics and guides how weekly study hours
should be distributed across subjects and groups.
"""


def calculate_adherence_percentage(planned_hours: float, actual_hours: float) -> float:
    """Formula: (actual_hours / planned_hours) * 100

    Measures percentage of planned study completed.
    Returns 100.0% if planned hours is zero.
    """
    if planned_hours <= 0:
        return 100.0
    return round((actual_hours / planned_hours) * 100.0, 1)


def allocate_study_hours(ranked_groups: list[dict], total_hours: float = 20.0) -> list[dict]:
    """Formula: group_hours = total_hours * (opportunity_index / sum_of_opportunity_indices)

    Allocates available study hours proportionally to the deficit and weight
    of the highest priority groups.
    """
    if not ranked_groups or total_hours <= 0:
        return []

    # Focus on top 5 groups with highest deficits
    top_groups = ranked_groups[:5]
    total_index = sum(float(g.get("opportunity_index", 1.0)) for g in top_groups)

    allocations = []
    for g in top_groups:
        idx = float(g.get("opportunity_index", 1.0))
        if total_index > 0:
            share = round((idx / total_index) * total_hours, 1)
        else:
            share = round(total_hours / len(top_groups), 1)

        allocations.append({
            "group_id": g["group_id"],
            "group_code": g.get("group_code", ""),
            "group_name": g.get("group_name", ""),
            "subject_name": g.get("subject_name", ""),
            "recommended_hours": share,
            "priority": g.get("priority", "MEDIUM"),
        })

    return allocations


def summarize_adherence(study_plans: list[dict]) -> dict:
    """Summarizes overall study plan adherence across all logged sessions.

    Formulas:
    - Total planned = sum(planned_hours)
    - Total actual = sum(actual_hours)
    - Overall adherence = (total_actual / total_planned) * 100
    - Status evaluation based on threshold:
        >= 80% -> 'ON TRACK'
        60% - 79% -> 'MODERATE'
        < 60% -> 'NEEDS ATTENTION'
    """
    if not study_plans:
        return {
            "total_plans": 0,
            "total_planned_hours": 0.0,
            "total_actual_hours": 0.0,
            "overall_adherence_percent": 100.0,
            "status": "NO PLANS",
        }

    total_planned = sum(float(p.get("planned_hours", 0.0)) for p in study_plans)
    total_actual = sum(float(p.get("actual_hours", 0.0)) for p in study_plans)

    adherence_pct = calculate_adherence_percentage(total_planned, total_actual)

    if adherence_pct >= 80.0:
        status = "ON TRACK"
    elif adherence_pct >= 60.0:
        status = "MODERATE"
    else:
        status = "NEEDS ATTENTION"

    return {
        "total_plans": len(study_plans),
        "total_planned_hours": round(total_planned, 1),
        "total_actual_hours": round(total_actual, 1),
        "overall_adherence_percent": adherence_pct,
        "status": status,
    }

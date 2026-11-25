"""Scoring business logic module.

Teaching rule: Every formula here is explicitly commented with its
mathematical definition and purpose so teammates can easily explain it in a viva.
"""


def calculate_percentage(score: float, max_score: float) -> float:
    """Formula: (score / max_score) * 100

    Calculates the percentage score achieved, capped at 100% and floored at 0%.
    """
    if max_score <= 0:
        return 0.0
    pct = (score / max_score) * 100.0
    return round(max(0.0, min(100.0, pct)), 2)


def calculate_gap_to_target(current_score: float, target_score: float) -> float:
    """Formula: target_score - current_score

    A positive gap indicates marks needed to reach target;
    A negative or zero gap indicates the target is already met or exceeded.
    """
    return round(target_score - current_score, 2)


def calculate_test_trend_delta(scores: list[float]) -> float:
    """Formula: recent_score - previous_score

    Measures momentum between consecutive test attempts (e.g. T3 - T2).
    Positive = improvement, Negative = regression.
    """
    if len(scores) < 2:
        return 0.0
    return round(scores[-1] - scores[-2], 2)


def calculate_subject_averages(tests: list[dict]) -> dict[str, dict]:
    """Formula: sum(scores_in_subject) / count(tests_with_subject)

    Aggregates test performance across subjects (Maths, Physics, Chemistry)
    to compute average score and average percentage for each subject.
    """
    subject_totals = {}

    for test in tests:
        for sub in test.get("subject_scores", []):
            code = sub.get("subject_code") or sub.get("subject_name", "UNKNOWN")
            score = float(sub.get("score", 0.0))
            max_s = float(sub.get("max_score", 100.0))

            if code not in subject_totals:
                subject_totals[code] = {
                    "name": sub.get("subject_name", code),
                    "total_score": 0.0,
                    "total_max": 0.0,
                    "count": 0,
                }
            subject_totals[code]["total_score"] += score
            subject_totals[code]["total_max"] += max_s
            subject_totals[code]["count"] += 1

    averages = {}
    for code, data in subject_totals.items():
        count = data["count"]
        avg_score = round(data["total_score"] / count, 2) if count > 0 else 0.0
        avg_max = round(data["total_max"] / count, 2) if count > 0 else 100.0
        averages[code] = {
            "name": data["name"],
            "avg_score": avg_score,
            "avg_max": avg_max,
            "avg_percentage": calculate_percentage(avg_score, avg_max),
            "test_count": count,
        }
    return averages


def aggregate_track_performance(
    tests: list[dict],
    target_score: float,
    track_max_score: float = 300.0,
    single_subject_mode: bool = False,
) -> dict:
    """Combines test records into an overarching scorecard.

    For standard multi-subject tracks (e.g. JEE Main out of 300), compares raw
    scores directly against target_score.
    For single-subject flexible-mark tracks (e.g. CBSE 8th Grade where unit tests
    may be out of 20, 40, or 80), normalizes scores to percentages so results
    across varying exam patterns compare accurately against target_percentage.
    """
    target_pct = calculate_percentage(target_score, track_max_score) if track_max_score > 0 else target_score

    if not tests:
        return {
            "test_count": 0,
            "latest_score": 0.0,
            "latest_max_score": 100.0 if single_subject_mode else track_max_score,
            "latest_percentage": 0.0,
            "highest_score": 0.0,
            "highest_percentage": 0.0,
            "average_score": 0.0,
            "average_percentage": 0.0,
            "target_percentage": target_pct,
            "gap_to_target": target_pct if single_subject_mode else target_score,
            "trend_delta": 0.0,
            "single_subject_mode": single_subject_mode,
            "subject_averages": {},
        }

    scores = [float(t.get("total_score", 0.0)) for t in tests]
    maxes = [float(t.get("max_score", 100.0) or 100.0) for t in tests]
    pcts = [calculate_percentage(s, m) for s, m in zip(scores, maxes)]

    latest_score = scores[-1]
    latest_max = maxes[-1]
    latest_pct = pcts[-1]
    highest_score = max(scores)
    highest_pct = max(pcts)
    avg_score = round(sum(scores) / len(scores), 2)
    avg_pct = round(sum(pcts) / len(pcts), 2)
    sub_avgs = calculate_subject_averages(tests)

    if single_subject_mode:
        gap = calculate_gap_to_target(latest_pct, target_pct)
        delta = calculate_test_trend_delta(pcts)
    else:
        gap = calculate_gap_to_target(latest_score, target_score)
        delta = calculate_test_trend_delta(scores)

    return {
        "test_count": len(tests),
        "latest_score": latest_score,
        "latest_max_score": latest_max,
        "latest_percentage": latest_pct,
        "highest_score": highest_score,
        "highest_percentage": highest_pct,
        "average_score": avg_score,
        "average_percentage": avg_pct,
        "target_percentage": target_pct,
        "gap_to_target": gap,
        "trend_delta": delta,
        "single_subject_mode": single_subject_mode,
        "subject_averages": sub_avgs,
    }

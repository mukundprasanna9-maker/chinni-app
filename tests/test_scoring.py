from backend.services.scoring import (
    calculate_percentage,
    calculate_gap_to_target,
    calculate_test_trend_delta,
    calculate_subject_averages,
    aggregate_track_performance,
)


def test_calculate_percentage():
    assert calculate_percentage(75.0, 100.0) == 75.0
    assert calculate_percentage(0.0, 100.0) == 0.0
    assert calculate_percentage(150.0, 100.0) == 100.0
    assert calculate_percentage(50.0, 0.0) == 0.0


def test_calculate_gap_to_target():
    assert calculate_gap_to_target(195.0, 235.0) == 40.0
    assert calculate_gap_to_target(240.0, 235.0) == -5.0
    assert calculate_gap_to_target(235.0, 235.0) == 0.0


def test_test_trend_delta():
    assert calculate_test_trend_delta([160.0, 185.0, 205.0]) == 20.0
    assert calculate_test_trend_delta([190.0, 180.0]) == -10.0
    assert calculate_test_trend_delta([190.0]) == 0.0
    assert calculate_test_trend_delta([]) == 0.0


def test_subject_averages_and_aggregation():
    sample_tests = [
        {
            "id": 1,
            "total_score": 162.0,
            "subject_scores": [
                {"subject_name": "Maths", "subject_code": "MATH", "score": 48.0, "max_score": 100.0},
                {"subject_name": "Physics", "subject_code": "PHY", "score": 54.0, "max_score": 100.0},
                {"subject_name": "Chemistry", "subject_code": "CHEM", "score": 60.0, "max_score": 100.0},
            ],
        },
        {
            "id": 2,
            "total_score": 204.0,
            "subject_scores": [
                {"subject_name": "Maths", "subject_code": "MATH", "score": 64.0, "max_score": 100.0},
                {"subject_name": "Physics", "subject_code": "PHY", "score": 68.0, "max_score": 100.0},
                {"subject_name": "Chemistry", "subject_code": "CHEM", "score": 72.0, "max_score": 100.0},
            ],
        },
    ]

    sub_avgs = calculate_subject_averages(sample_tests)
    assert "MATH" in sub_avgs
    assert sub_avgs["MATH"]["avg_score"] == 56.0
    assert sub_avgs["MATH"]["avg_percentage"] == 56.0
    assert sub_avgs["CHEM"]["avg_score"] == 66.0

    summary = aggregate_track_performance(sample_tests, target_score=235.0)
    assert summary["test_count"] == 2
    assert summary["latest_score"] == 204.0
    assert summary["highest_score"] == 204.0
    assert summary["average_score"] == 183.0
    assert summary["gap_to_target"] == 31.0
    assert summary["trend_delta"] == 42.0


def test_single_subject_flexible_marks_aggregation():
    # Single-subject exams with different max marks (18/20 = 90%, 64/80 = 80%)
    tests = [
        {
            "id": 1,
            "total_score": 18.0,
            "max_score": 20.0,
            "subject_scores": [
                {"subject_name": "Science", "subject_code": "SCI-8", "score": 18.0, "max_score": 20.0},
            ],
        },
        {
            "id": 2,
            "total_score": 64.0,
            "max_score": 80.0,
            "subject_scores": [
                {"subject_name": "Mathematics", "subject_code": "MATH-8", "score": 64.0, "max_score": 80.0},
            ],
        },
    ]
    summary = aggregate_track_performance(
        tests,
        target_score=85.0,
        track_max_score=100.0,
        single_subject_mode=True,
    )
    assert summary["single_subject_mode"] is True
    assert summary["latest_percentage"] == 80.0
    assert summary["average_percentage"] == 85.0
    assert summary["gap_to_target"] == 5.0
    assert summary["trend_delta"] == -10.0

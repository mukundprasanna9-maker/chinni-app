from backend.services.spend_ranking import rank_groups_to_focus, rank_subjects_to_focus
from backend.services.planning import (
    calculate_adherence_percentage,
    allocate_study_hours,
    summarize_adherence,
)


def test_spend_ranking_groups():
    group_history = [
        # G1 Calculus: score 14/33.3 -> deficit 19.3
        {
            "group_id": 1,
            "group_code": "G2",
            "group_name": "Calculus",
            "subject_name": "Mathematics",
            "score": 14.0,
            "max_score": 33.3,
            "weight_percentage": 33.3,
        },
        # G1 Physical Chem: score 28/33.3 -> deficit 5.3
        {
            "group_id": 2,
            "group_code": "G1",
            "group_name": "Physical Chemistry",
            "subject_name": "Chemistry",
            "score": 28.0,
            "max_score": 33.3,
            "weight_percentage": 33.3,
        },
    ]

    ranked = rank_groups_to_focus(group_history)
    assert len(ranked) == 2
    # Calculus should rank first due to higher deficit
    assert ranked[0]["group_name"] == "Calculus"
    assert ranked[0]["priority"] == "HIGH"
    assert ranked[1]["group_name"] == "Physical Chemistry"


def test_spend_ranking_subjects():
    subjects = [
        {"id": 1, "name": "Mathematics", "code": "MATH", "target_marks": 80.0, "max_marks": 100.0},
        {"id": 2, "name": "Physics", "code": "PHY", "target_marks": 80.0, "max_marks": 100.0},
    ]
    test_records = [
        {
            "id": 1,
            "subject_scores": [
                {"subject_id": 1, "score": 55.0},
                {"subject_id": 2, "score": 70.0},
            ],
        }
    ]

    ranked = rank_subjects_to_focus(subjects, test_records)
    assert len(ranked) == 2
    # Maths has gap of 25 (80-55), Physics has gap of 10 (80-70)
    assert ranked[0]["code"] == "MATH"
    assert ranked[0]["gap_to_target"] == 25.0


def test_study_hours_allocation():
    ranked_groups = [
        {"group_id": 1, "group_code": "G2", "group_name": "Calculus", "subject_name": "Maths", "opportunity_index": 6.0, "priority": "HIGH"},
        {"group_id": 2, "group_code": "G1", "group_name": "Mechanics", "subject_name": "Physics", "opportunity_index": 4.0, "priority": "HIGH"},
    ]

    allocations = allocate_study_hours(ranked_groups, total_hours=10.0)
    assert len(allocations) == 2
    # Calculus gets 60% of 10h = 6h; Mechanics gets 40% of 10h = 4h
    assert allocations[0]["recommended_hours"] == 6.0
    assert allocations[1]["recommended_hours"] == 4.0


def test_summarize_adherence():
    plans = [
        {"planned_hours": 4.0, "actual_hours": 3.5},
        {"planned_hours": 6.0, "actual_hours": 5.0},
    ]
    summary = summarize_adherence(plans)
    assert summary["total_planned_hours"] == 10.0
    assert summary["total_actual_hours"] == 8.5
    assert summary["overall_adherence_percent"] == 85.0
    assert summary["status"] == "ON TRACK"

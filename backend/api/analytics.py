from fastapi import APIRouter, HTTPException
from backend.repositories.track_repo import get_track_by_id, get_subjects_by_track
from backend.repositories.test_repo import (
    get_tests_by_track,
    get_test_by_id,
    get_all_group_scores_for_track,
)
from backend.repositories.plan_repo import get_study_plans
from backend.repositories.student_repo import get_student_by_id
from backend.services.scoring import aggregate_track_performance
from backend.services.spend_ranking import rank_groups_to_focus, rank_subjects_to_focus
from backend.services.planning import allocate_study_hours, summarize_adherence

router = APIRouter(tags=["Analytics & Trends"])


@router.get("/tracks/{track_id}/scorecard")
def get_track_scorecard(track_id: int):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    tests = get_tests_by_track(track_id)
    full_tests = [get_test_by_id(t["id"]) for t in tests]
    scorecard = aggregate_track_performance(full_tests, target_score=float(track["target_score"]))
    scorecard["track"] = track
    return scorecard


@router.get("/tracks/{track_id}/focus-rankings")
def get_focus_rankings(track_id: int, available_hours: float = 20.0):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    all_group_scores = get_all_group_scores_for_track(track_id)
    ranked_groups = rank_groups_to_focus(all_group_scores)
    allocations = allocate_study_hours(ranked_groups, total_hours=available_hours)
    return {
        "track_id": track_id,
        "track_name": track["name"],
        "ranked_groups": ranked_groups,
        "recommended_allocations": allocations,
    }


@router.get("/tracks/{track_id}/subject-rankings")
def get_subject_rankings(track_id: int):
    track = get_track_by_id(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    subjects = get_subjects_by_track(track_id)
    tests = get_tests_by_track(track_id)
    full_tests = [get_test_by_id(t["id"]) for t in tests]
    ranked = rank_subjects_to_focus(subjects, full_tests)
    return {"track_id": track_id, "ranked_subjects": ranked}


@router.get("/students/{student_id}/adherence")
def get_student_adherence(student_id: int):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    plans = get_study_plans(student_id)
    return summarize_adherence(plans)

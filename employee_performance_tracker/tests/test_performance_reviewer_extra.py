from datetime import datetime

from performance_reviewer import (
    submit_performance_review,
    get_performance_reviews_for_employee,
    get_reviews_by_date_range,
    get_reviews_by_reviewer,
    get_recent_reviews,
    update_performance_review,
    aggregate_strengths,
    aggregate_areas_for_improvement,
    get_top_goals,
    ensure_review_ids,
)


def test_reviewer_extra_paths(fake_mongo_collection, monkeypatch):
    collection = fake_mongo_collection
    ensure_review_ids(collection)
    # insert multiple docs including lists for strengths/goals
    submit_performance_review(collection=collection, employee_id=1, reviewer_name="Alice", overall_rating=4, review_date="2024-01-01", strengths="python, python", areas_for_improvement="comm", goals_for_next_period="g1,g2", comments="") 
    submit_performance_review(collection=collection, employee_id=1, reviewer_name="Bob", overall_rating=3, review_date="2024-02-01", strengths="sql", areas_for_improvement="", goals_for_next_period="g3", comments="")
    ensure_review_ids(collection)

    # reviewer/date-range/recent
    assert get_reviews_by_reviewer(collection=collection, reviewer_name="Alice")
    assert get_reviews_by_date_range(collection=collection, start_date="2024-01-01", end_date="2024-12-31")
    assert get_recent_reviews(collection=collection, limit=1)

    # aggregations
    strengths = aggregate_strengths(collection=collection, employee_id=1)
    assert strengths.get("python", 0) >= 1
    areas = aggregate_areas_for_improvement(collection=collection, employee_id=1)
    assert isinstance(areas, dict)
    goals = get_top_goals(collection=collection, employee_id=1, limit=2)
    assert isinstance(goals, list)

    # update comment with datetime review_date path
    docs = list(collection.find({"employee_id": 1}))
    assert docs
    review_id = docs[0]["review_id"]
    assert update_performance_review(collection=collection, review_id=str(review_id), review_date=datetime(2024, 3, 1))
    # update no-op path (no fields)
    assert update_performance_review(collection=collection, review_id=str(review_id)) is False
    # delete not found path (non-existing integer id)
    from performance_reviewer import delete_performance_review
    assert delete_performance_review(collection=collection, review_id="99999") is False
    # invalid date range returns []
    assert get_reviews_by_date_range(collection=collection, start_date="2024-12-31", end_date="2024-01-01") == []
    # case-insensitive reviewer search
    assert get_reviews_by_reviewer(collection=collection, reviewer_name="alice")



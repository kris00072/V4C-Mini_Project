from performance_reviewer import (
    submit_performance_review,
    get_performance_reviews_for_employee,
    get_average_rating_for_employee,
    delete_performance_review,
    ensure_review_ids,
    get_recent_reviews,
    get_reviews_by_reviewer,
    get_reviews_by_date_range,
    update_performance_review,
    aggregate_strengths,
    aggregate_areas_for_improvement,
    get_top_goals,
)


def test_submit_and_retrieve_reviews(fake_mongo_collection, monkeypatch):
    # Skip validation for unit test context
    monkeypatch.setattr("performance_reviewer.validate_review_data", lambda *a, **k: {})
    collection = fake_mongo_collection
    ensure_review_ids(collection)
    rid = submit_performance_review(
        collection=collection,
        employee_id=101,
        reviewer_name="Reviewer",
        overall_rating=4.5,
        review_date="2024-01-01",
        strengths="Focus, Teamwork",
        areas_for_improvement="",
        comments="Solid work",
        goals_for_next_period="",
    )
    assert rid is not None
    ensure_review_ids(collection)
    reviews = get_performance_reviews_for_employee(collection=collection, employee_id=101)
    assert len(reviews) == 1
    avg = get_average_rating_for_employee(collection=collection, employee_id=101)
    assert avg == 4.5
    # reviewer/date range/recent
    assert get_recent_reviews(collection=collection, limit=5)
    assert get_reviews_by_reviewer(collection=collection, reviewer_name="Reviewer")
    assert get_reviews_by_date_range(collection=collection, start_date="2024-01-01", end_date="2024-12-31")
    # aggregations
    strengths = aggregate_strengths(collection=collection, employee_id=101)
    assert strengths
    areas = aggregate_areas_for_improvement(collection=collection, employee_id=101)
    assert isinstance(areas, dict)
    goals = get_top_goals(collection=collection, employee_id=101, limit=5)
    assert isinstance(goals, list)


def test_delete_review_by_integer_id(fake_mongo_collection, monkeypatch):
    monkeypatch.setattr("performance_reviewer.validate_review_data", lambda *a, **k: {})
    collection = fake_mongo_collection
    ensure_review_ids(collection)
    submit_performance_review(
        collection=collection,
        employee_id=102,
        reviewer_name="R",
        overall_rating=3.0,
        review_date="2024-02-02",
        strengths="",
        areas_for_improvement="",
        comments="",
        goals_for_next_period="",
    )
    # migrate to ensure review_id present
    ensure_review_ids(collection)
    docs = list(collection.find({"employee_id": 102}))
    assert docs
    review_id = docs[0]["review_id"]
    # update pipeline
    assert update_performance_review(collection=collection, review_id=str(review_id), comments="Updated")
    ok = delete_performance_review(collection=collection, review_id=str(review_id))
    assert ok is True
    reviews = list(collection.find({"employee_id": 102}))
    assert len(reviews) == 0



from lessonforge.routing import MAX_RETRIES, MAX_ATTEMPTS, route_after_evaluation


def test_retry_limit_means_three_total_attempts():
    assert MAX_RETRIES == 2
    assert MAX_ATTEMPTS == 3


def test_failed_third_attempt_is_rejected():
    assert route_after_evaluation({"final_status": "IN_PROGRESS", "attempt_count": 3}) == "reject"


def test_failed_first_attempt_retries():
    assert route_after_evaluation({"final_status": "IN_PROGRESS", "attempt_count": 1}) == "retry"


def test_approved_lesson_routes_to_approve():
    assert route_after_evaluation({"final_status": "APPROVED", "attempt_count": 1}) == "approve"

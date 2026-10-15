MAX_RETRIES = 2
MAX_ATTEMPTS = MAX_RETRIES + 1


def route_after_evaluation(state: dict) -> str:
    if state.get("final_status") == "APPROVED":
        return "approve"
    if state.get("attempt_count", 0) >= MAX_ATTEMPTS:
        return "reject"
    return "retry"

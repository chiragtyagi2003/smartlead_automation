def prepare_payload(email_details, generated_reply):
    payload = {
        "email_stats_id": email_details["stats_id"],
        "email_body": generated_reply,
        "cc": "chiragtyagi2025@gmail.com",
        "bcc": "chirag.tyagi@qubit.capital",
        "add_signature": True,
        "to_first_name": "chirag",
        "to_last_name": "tyagi",
        "to_email": "tyagichirag2025@gmail.com"  # for testing purpose
    }
    return payload

def feedback_and_comparison(feedback_score, benchmark_score):
    return feedback_score >= benchmark_score

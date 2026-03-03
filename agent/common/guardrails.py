from agent.common.env import getenv_int, getenv_list_csv
def forbidden_phrases(): return getenv_list_csv("FORBIDDEN_PHRASES",["testimonial","animatopia"])
def max_weekly_wave(): return getenv_int("MAX_WEEKLY_WAVE",30)
def assert_no_forbidden(text):
    low=(text or "").lower()
    for p in forbidden_phrases():
        if p.lower() in low: raise ValueError(f"Forbidden: {p}")

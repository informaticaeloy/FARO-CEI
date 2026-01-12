# utils/time.py
from datetime import datetime

def utc_now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

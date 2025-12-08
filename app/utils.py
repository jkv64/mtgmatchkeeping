from datetime import datetime
from dateutil import parser

def parse_iso_or_none(s: str):
    if not s:
        return None
    if isinstance(s, datetime):
        return s
    return parser.isoparse(s)

import re

_TOKEN = re.compile(r"[\w\u0600-\u06FF]+", re.UNICODE)


def build_fts_query(raw: str) -> str:
    """Sanitize free-text input into a safe FTS5 MATCH expression with prefix matching."""
    if not raw:
        return ""
    tokens = _TOKEN.findall(raw)
    if not tokens:
        return ""
    return " AND ".join(f'"{t}"*' for t in tokens[:8])

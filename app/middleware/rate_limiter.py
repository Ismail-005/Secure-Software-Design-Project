from datetime import datetime, timedelta
from collections import defaultdict
from flask import current_app

_attempts: dict[str, list[datetime]] = defaultdict(list)

class RateLimiter:
    def record_attempt(self, key: str) -> None:
        now = datetime.utcnow()
        window = current_app.config['RATE_LIMIT_WINDOW']
        cutoff = now - timedelta(seconds=window)
        _attempts[key] = [t for t in _attempts[key] if t > cutoff]
        _attempts[key].append(now)

    def is_blocked(self, key: str) -> bool:
        now = datetime.utcnow()
        window = current_app.config['RATE_LIMIT_WINDOW']
        max_attempts = current_app.config['RATE_LIMIT_MAX']
        cutoff = now - timedelta(seconds=window)
        recent = [t for t in _attempts.get(key, []) if t > cutoff]
        return len(recent) >= max_attempts

    def reset(self, key: str) -> None:
        _attempts.pop(key, None)

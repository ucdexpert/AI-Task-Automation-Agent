"""
Rate limiter configuration
Separated from main.py to avoid circular imports
"""
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Create global limiter
limiter = Limiter(key_func=get_remote_address)



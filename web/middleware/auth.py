# web/middleware/auth.py
import os
import secrets
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

def _get_expected_key():
    key = os.getenv('ASTROFIN_API_KEY')
    if not key:
        logger.warning("ASTROFIN_API_KEY not set! Protected endpoints will fail closed.")
    return key

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        expected_key = _get_expected_key()
        if not expected_key:
            return jsonify({'error': 'Authentication not configured'}), 401

        provided_key = request.headers.get('X-API-Key')
        if not provided_key:
            return jsonify({'error': 'Missing X-API-Key header'}), 401

        # Constant-time comparison
        if not secrets.compare_digest(provided_key, expected_key):
            return jsonify({'error': 'Invalid API key'}), 403

        return f(*args, **kwargs)
    return decorated_function

"""
Supabase-backed request authentication.
Verifies the bearer token on every request against Supabase Auth; requires
SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment.
"""

import json
import os
import urllib.error
import urllib.request
from flask import jsonify, request

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')


def supabase_headers(extra=None):
    h = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json',
    }
    if extra:
        h.update(extra)
    return h


def http(url, method='GET', body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def get_caller_id(bearer_token):
    """Resolve the Supabase user_id from a user-issued JWT."""
    status, data = http(
        f'{SUPABASE_URL}/auth/v1/user',
        headers={
            'apikey': SERVICE_ROLE_KEY,
            'Authorization': f'Bearer {bearer_token}',
        }
    )
    if status == 200:
        return data.get('id')
    return None


def is_admin(user_id):
    """Check profiles table for admin role (runs with service role, bypasses RLS)."""
    url = f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=role'
    status, data = http(url, headers=supabase_headers())
    if status == 200 and data:
        return data[0].get('role') == 'admin'
    return False


def require_auth():
    """Returns (user_id, None) if the request carries a valid Supabase session,
    otherwise (None, error_response)."""
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        return None, (jsonify({'success': False, 'error': 'Supabase not configured on server'}), 503)

    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None, (jsonify({'success': False, 'error': 'Missing Authorization header'}), 401)
    token = auth[7:]
    user_id = get_caller_id(token)
    if not user_id:
        return None, (jsonify({'success': False, 'error': 'Invalid token'}), 401)
    return user_id, None


def require_admin():
    """Returns (user_id, None) or (None, error_response)."""
    user_id, err = require_auth()
    if err:
        return None, err
    if not is_admin(user_id):
        return None, (jsonify({'success': False, 'error': 'Forbidden — admin only'}), 403)
    return user_id, None

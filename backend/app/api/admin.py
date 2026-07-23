"""
Admin API endpoints
Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment.
"""

import json
import os
import urllib.error
import urllib.request
from flask import Blueprint, jsonify, request

admin_bp = Blueprint('admin', __name__)

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')


def _supabase_headers(extra=None):
    h = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json',
    }
    if extra:
        h.update(extra)
    return h


def _http(url, method='GET', body=None, headers=None):
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


def _get_caller_id(bearer_token):
    """Resolve the Supabase user_id from a user-issued JWT."""
    status, data = _http(
        f'{SUPABASE_URL}/auth/v1/user',
        headers={
            'apikey': SERVICE_ROLE_KEY,
            'Authorization': f'Bearer {bearer_token}',
        }
    )
    if status == 200:
        return data.get('id')
    return None


def _is_admin(user_id):
    """Check profiles table for admin role (runs with service role, bypasses RLS)."""
    url = f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{user_id}&select=role'
    status, data = _http(url, headers=_supabase_headers())
    if status == 200 and data:
        return data[0].get('role') == 'admin'
    return False


def _require_admin():
    """Returns (user_id, None) or (None, error_response)."""
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Bearer '):
        return None, (jsonify({'success': False, 'error': 'Missing Authorization header'}), 401)
    token = auth[7:]
    user_id = _get_caller_id(token)
    if not user_id:
        return None, (jsonify({'success': False, 'error': 'Invalid token'}), 401)
    if not _is_admin(user_id):
        return None, (jsonify({'success': False, 'error': 'Forbidden — admin only'}), 403)
    return user_id, None


@admin_bp.route('/admin/invite-user', methods=['POST'])
def invite_user():
    """Invite a new user by email. Admin-only."""
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        return jsonify({'success': False, 'error': 'Supabase not configured on server'}), 503

    _caller_id, err = _require_admin()
    if err:
        return err

    email = (request.json or {}).get('email', '').strip()
    if not email:
        return jsonify({'success': False, 'error': 'email is required'}), 400

    status, data = _http(
        f'{SUPABASE_URL}/auth/v1/invite',
        method='POST',
        body={'email': email},
        headers=_supabase_headers(),
    )

    if status in (200, 201):
        return jsonify({'success': True, 'message': f'Invitation sent to {email}'})

    msg = data.get('msg') or data.get('message') or data.get('error_description') or 'Invitation failed'
    return jsonify({'success': False, 'error': msg}), 400


@admin_bp.route('/admin/update-role', methods=['POST'])
def update_role():
    """Change a user's role. Admin-only."""
    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        return jsonify({'success': False, 'error': 'Supabase not configured on server'}), 503

    caller_id, err = _require_admin()
    if err:
        return err

    body = request.json or {}
    target_id = body.get('user_id', '').strip()
    new_role = body.get('role', '').strip()

    if not target_id or new_role not in ('admin', 'user'):
        return jsonify({'success': False, 'error': 'user_id and role (admin|user) are required'}), 400

    # Prevent demoting yourself
    if target_id == caller_id and new_role != 'admin':
        return jsonify({'success': False, 'error': 'Cannot demote yourself'}), 400

    status, data = _http(
        f'{SUPABASE_URL}/rest/v1/profiles?id=eq.{target_id}',
        method='PATCH',
        body={'role': new_role},
        headers=_supabase_headers({'Prefer': 'return=minimal'}),
    )

    if status in (200, 204):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': str(data)}), 400

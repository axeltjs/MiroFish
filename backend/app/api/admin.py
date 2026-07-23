"""
Admin API endpoints
Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in environment.
"""

from flask import Blueprint, jsonify, request

from ..utils.auth import SUPABASE_URL, SERVICE_ROLE_KEY, http as _http, supabase_headers as _supabase_headers
from ..utils.auth import require_admin as _require_admin

admin_bp = Blueprint('admin', __name__)


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

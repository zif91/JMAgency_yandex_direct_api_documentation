"""
Yandex Direct Multi-Account Panel with AI Audit Agent.
Supports multiple Yandex Direct accounts per user.
"""
import os
import json
import functools
import requests
from flask import (
    Flask, redirect, url_for, session, request,
    render_template, flash, jsonify, g
)
from dotenv import load_dotenv

import asyncio
import db
from yandex_api import YandexDirectAPI
from agent import YandexDirectAuditAgent, run_audit as run_agent_audit

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

# Yandex OAuth settings
YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/oauth/yandex/callback")

# Anthropic API for AI audit
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


# ============== CLI Commands ==============

@app.cli.command('init-db')
def init_db_command():
    """Initialize the database."""
    db.init_db()
    print('Database initialized.')


# ============== Authentication Decorators ==============

def login_required(f):
    """Decorator for routes that require authentication."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def api_auth_required(f):
    """Decorator for API routes that require API key authentication."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({"error": "Invalid Authorization header format. Expected 'Bearer <api_key>'"}), 401

        api_key = parts[1]
        user = db.get_user_by_api_key(api_key)
        if not user:
            return jsonify({"error": "Invalid API key"}), 401

        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def get_api_client(account_id: str = None) -> tuple:
    """
    Get YandexDirectAPI client for the specified account.
    If account_id is None, uses the first active account.

    Returns:
        (api_client, error_response) - api_client if success, error_response if failure
    """
    user_id = g.current_user['id']

    if account_id:
        account = db.get_yandex_account(account_id, user_id)
    else:
        accounts = db.get_yandex_accounts(user_id)
        active_accounts = [a for a in accounts if a.get('is_active')]
        account = active_accounts[0] if active_accounts else None

    if not account:
        return None, (jsonify({"error": "No Yandex account found"}), 404)

    api = YandexDirectAPI(
        token=account['yandex_token'],
        login=account['yandex_login']
    )
    return api, None


# ============== Web Routes ==============

@app.route('/')
def index():
    """Home page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('register.html')

        if password != password_confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')

        try:
            user = db.create_user(email, password)
            flash(f'Account created! Your API key: {user["api_key"]}', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = db.authenticate_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard."""
    user = db.get_user_by_id(session['user_id'])
    accounts = db.get_yandex_accounts(session['user_id'])
    return render_template('dashboard.html', user=user, accounts=accounts)


@app.route('/accounts')
@login_required
def accounts():
    """Manage Yandex accounts."""
    user = db.get_user_by_id(session['user_id'])
    yandex_accounts = db.get_yandex_accounts(session['user_id'])
    return render_template('accounts.html', user=user, accounts=yandex_accounts)


@app.route('/accounts/add')
@login_required
def add_account():
    """Start OAuth flow to add a new Yandex account."""
    if not YANDEX_CLIENT_ID:
        flash('Yandex OAuth is not configured.', 'error')
        return redirect(url_for('accounts'))

    # Store account name in session for after OAuth
    account_name = request.args.get('name', 'My Account')
    session['pending_account_name'] = account_name

    oauth_url = (
        f"https://oauth.yandex.ru/authorize?response_type=code"
        f"&client_id={YANDEX_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(oauth_url)


@app.route('/oauth/yandex/callback')
@login_required
def yandex_callback():
    """Handle Yandex OAuth callback."""
    code = request.args.get('code')
    if not code:
        flash('OAuth failed: No authorization code received.', 'error')
        return redirect(url_for('accounts'))

    # Exchange code for token
    token_url = "https://oauth.yandex.ru/token"
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': YANDEX_CLIENT_ID,
        'client_secret': YANDEX_CLIENT_SECRET
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        access_token = token_info['access_token']

        # Get user info from Yandex
        info_url = "https://login.yandex.ru/info"
        headers = {'Authorization': f'OAuth {access_token}'}
        info_response = requests.get(info_url, headers=headers)
        info_response.raise_for_status()
        user_info = info_response.json()
        yandex_login = user_info['login']

        # Save the account
        account_name = session.pop('pending_account_name', yandex_login)
        db.add_yandex_account(
            user_id=session['user_id'],
            account_name=account_name,
            yandex_login=yandex_login,
            yandex_token=access_token
        )

        flash(f'Successfully added Yandex account: {yandex_login}', 'success')

    except requests.exceptions.RequestException as e:
        flash(f'OAuth error: {e}', 'error')

    return redirect(url_for('accounts'))


@app.route('/accounts/<account_id>/delete', methods=['POST'])
@login_required
def delete_account(account_id):
    """Delete a Yandex account."""
    if db.delete_yandex_account(account_id, session['user_id']):
        flash('Account deleted.', 'success')
    else:
        flash('Failed to delete account.', 'error')
    return redirect(url_for('accounts'))


@app.route('/accounts/<account_id>/toggle', methods=['POST'])
@login_required
def toggle_account(account_id):
    """Toggle account active status."""
    is_active = request.form.get('is_active') == '1'
    db.toggle_yandex_account(account_id, session['user_id'], is_active)
    return redirect(url_for('accounts'))


@app.route('/audit')
@login_required
def audit_page():
    """Audit page."""
    accounts = db.get_yandex_accounts(session['user_id'])
    history = db.get_audit_history(session['user_id'], limit=20)
    return render_template('audit.html', accounts=accounts, history=history)


@app.route('/audit/run', methods=['POST'])
@login_required
def run_audit():
    """Run audit for selected account using Claude Agent SDK."""
    account_id = request.form.get('account_id')
    audit_type = request.form.get('audit_type', 'full')

    account = db.get_yandex_account(account_id, session['user_id'])
    if not account:
        flash('Account not found.', 'error')
        return redirect(url_for('audit_page'))

    # Create audit record
    audit_id = db.create_audit(session['user_id'], account_id, audit_type)
    db.update_audit_status(audit_id, 'running')

    try:
        # Create agent with Claude Agent SDK
        agent = YandexDirectAuditAgent(
            yandex_token=account['yandex_token'],
            yandex_login=account['yandex_login'],
            account_name=account['account_name'],
            anthropic_api_key=ANTHROPIC_API_KEY
        )

        # Run async audit
        result = asyncio.run(agent.run_audit())

        db.update_audit_status(audit_id, 'completed', result.to_json())
        flash('Audit completed successfully!', 'success')

    except Exception as e:
        db.update_audit_status(audit_id, 'failed', json.dumps({"error": str(e)}))
        flash(f'Audit failed: {e}', 'error')

    return redirect(url_for('audit_result', audit_id=audit_id))


@app.route('/audit/<audit_id>')
@login_required
def audit_result(audit_id):
    """View audit result."""
    audit = db.get_audit(audit_id, session['user_id'])
    if not audit:
        flash('Audit not found.', 'error')
        return redirect(url_for('audit_page'))

    result = None
    if audit['result']:
        try:
            result = json.loads(audit['result'])
        except json.JSONDecodeError:
            result = {"error": "Failed to parse result"}

    return render_template('audit_result.html', audit=audit, result=result)


@app.route('/settings')
@login_required
def settings():
    """User settings page."""
    user = db.get_user_by_id(session['user_id'])
    return render_template('settings.html', user=user)


@app.route('/settings/regenerate-api-key', methods=['POST'])
@login_required
def regenerate_api_key():
    """Regenerate API key."""
    new_key = db.regenerate_api_key(session['user_id'])
    flash(f'New API key generated: {new_key}', 'success')
    return redirect(url_for('settings'))


# ============== API Routes ==============

@app.route('/api/accounts', methods=['GET'])
@api_auth_required
def api_get_accounts():
    """Get all Yandex accounts for the user."""
    accounts = db.get_yandex_accounts(g.current_user['id'])
    return jsonify({"accounts": accounts})


@app.route('/api/campaigns', methods=['GET'])
@api_auth_required
def api_get_campaigns():
    """Get campaigns from Yandex Direct."""
    account_id = request.args.get('account_id')
    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        campaigns = api.get_campaigns()
        return jsonify(campaigns)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/adgroups', methods=['POST'])
@api_auth_required
def api_get_adgroups():
    """Get ad groups from Yandex Direct."""
    data = request.get_json() or {}
    account_id = data.get('account_id')
    campaign_ids = data.get('campaign_ids')

    if not campaign_ids:
        return jsonify({"error": "campaign_ids is required"}), 400

    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        adgroups = api.get_adgroups(campaign_ids=campaign_ids)
        return jsonify(adgroups)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ads', methods=['POST'])
@api_auth_required
def api_get_ads():
    """Get ads from Yandex Direct."""
    data = request.get_json() or {}
    account_id = data.get('account_id')
    adgroup_ids = data.get('adgroup_ids')
    campaign_ids = data.get('campaign_ids')

    if not adgroup_ids and not campaign_ids:
        return jsonify({"error": "adgroup_ids or campaign_ids is required"}), 400

    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        ads = api.get_ads(adgroup_ids=adgroup_ids, campaign_ids=campaign_ids)
        return jsonify(ads)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/keywords', methods=['POST'])
@api_auth_required
def api_get_keywords():
    """Get keywords from Yandex Direct."""
    data = request.get_json() or {}
    account_id = data.get('account_id')
    adgroup_ids = data.get('adgroup_ids')
    campaign_ids = data.get('campaign_ids')

    if not adgroup_ids and not campaign_ids:
        return jsonify({"error": "adgroup_ids or campaign_ids is required"}), 400

    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        keywords = api.get_keywords(adgroup_ids=adgroup_ids, campaign_ids=campaign_ids)
        return jsonify(keywords)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/bids', methods=['GET'])
@api_auth_required
def api_get_bids():
    """Get bids from Yandex Direct."""
    account_id = request.args.get('account_id')
    campaign_ids = request.args.getlist('campaign_ids')

    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        if campaign_ids:
            campaign_ids = [int(c) for c in campaign_ids]
        bids = api.get_bids(campaign_ids=campaign_ids if campaign_ids else None)
        return jsonify(bids)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/reports', methods=['POST'])
@api_auth_required
def api_get_report():
    """Get report from Yandex Direct."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Report definition is required"}), 400

    account_id = data.pop('account_id', None)
    api, error = get_api_client(account_id)
    if error:
        return error

    try:
        report = api.get_report(report_definition=data)
        return report, 200, {'Content-Type': 'text/tab-separated-values; charset=utf-8'}
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/audit', methods=['POST'])
@api_auth_required
def api_run_audit():
    """Run audit via API using Claude Agent SDK."""
    data = request.get_json() or {}
    account_id = data.get('account_id')

    if not account_id:
        return jsonify({"error": "account_id is required"}), 400

    account = db.get_yandex_account(account_id, g.current_user['id'])
    if not account:
        return jsonify({"error": "Account not found"}), 404

    try:
        result = asyncio.run(run_agent_audit(
            yandex_token=account['yandex_token'],
            yandex_login=account['yandex_login'],
            account_name=account['account_name'],
            anthropic_api_key=ANTHROPIC_API_KEY
        ))
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/audit/history', methods=['GET'])
@api_auth_required
def api_audit_history():
    """Get audit history via API."""
    limit = request.args.get('limit', 50, type=int)
    history = db.get_audit_history(g.current_user['id'], limit=limit)
    return jsonify({"history": history})


# ============== Error Handlers ==============

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not found"}), 404
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('error.html', error="Server error"), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

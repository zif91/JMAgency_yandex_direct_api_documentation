"""
Database module with multi-account support.
Supports multiple Yandex Direct accounts per user.
"""
import sqlite3
import secrets
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


DATABASE_PATH = 'database.db'


def get_db_connection():
    """Get database connection with Row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database with users and yandex_accounts tables."""
    conn = get_db_connection()

    # Users table - main user accounts
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    # Yandex accounts table - multiple accounts per user
    conn.execute('''
        CREATE TABLE IF NOT EXISTS yandex_accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            yandex_login TEXT NOT NULL,
            yandex_token TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Audit history table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS audit_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            yandex_account_id TEXT NOT NULL,
            audit_type TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (yandex_account_id) REFERENCES yandex_accounts(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# ============== User Management ==============

def create_user(email: str, password: str) -> dict:
    """
    Create a new user account.

    Returns:
        dict with user info including api_key
    """
    user_id = str(uuid.uuid4())
    api_key = secrets.token_urlsafe(32)
    password_hash = generate_password_hash(password)
    now = datetime.utcnow().isoformat()

    conn = get_db_connection()
    try:
        conn.execute(
            '''INSERT INTO users (id, email, password_hash, api_key, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, email, password_hash, api_key, now, now)
        )
        conn.commit()
        return {
            'id': user_id,
            'email': email,
            'api_key': api_key,
            'created_at': now
        }
    except sqlite3.IntegrityError:
        raise ValueError("User with this email already exists")
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> dict | None:
    """
    Authenticate user by email and password.

    Returns:
        User dict if valid, None otherwise
    """
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?', (email,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Get user by ID."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_api_key(api_key: str) -> dict | None:
    """Get user by API key."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE api_key = ?', (api_key,)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def regenerate_api_key(user_id: str) -> str:
    """Regenerate API key for user."""
    new_api_key = secrets.token_urlsafe(32)
    now = datetime.utcnow().isoformat()

    conn = get_db_connection()
    conn.execute(
        'UPDATE users SET api_key = ?, updated_at = ? WHERE id = ?',
        (new_api_key, now, user_id)
    )
    conn.commit()
    conn.close()
    return new_api_key


# ============== Yandex Account Management ==============

def add_yandex_account(user_id: str, account_name: str,
                       yandex_login: str, yandex_token: str) -> dict:
    """
    Add a new Yandex Direct account for user.

    Returns:
        dict with account info
    """
    account_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO yandex_accounts
           (id, user_id, account_name, yandex_login, yandex_token, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (account_id, user_id, account_name, yandex_login, yandex_token, now, now)
    )
    conn.commit()
    conn.close()

    return {
        'id': account_id,
        'user_id': user_id,
        'account_name': account_name,
        'yandex_login': yandex_login,
        'created_at': now
    }


def get_yandex_accounts(user_id: str) -> list:
    """Get all Yandex accounts for user."""
    conn = get_db_connection()
    accounts = conn.execute(
        '''SELECT id, account_name, yandex_login, is_active, created_at
           FROM yandex_accounts
           WHERE user_id = ?
           ORDER BY created_at DESC''',
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(acc) for acc in accounts]


def get_yandex_account(account_id: str, user_id: str = None) -> dict | None:
    """
    Get Yandex account by ID.
    If user_id provided, validates ownership.
    """
    conn = get_db_connection()
    if user_id:
        account = conn.execute(
            'SELECT * FROM yandex_accounts WHERE id = ? AND user_id = ?',
            (account_id, user_id)
        ).fetchone()
    else:
        account = conn.execute(
            'SELECT * FROM yandex_accounts WHERE id = ?',
            (account_id,)
        ).fetchone()
    conn.close()
    return dict(account) if account else None


def update_yandex_account(account_id: str, user_id: str,
                          account_name: str = None, yandex_token: str = None) -> bool:
    """Update Yandex account details."""
    updates = []
    params = []

    if account_name:
        updates.append('account_name = ?')
        params.append(account_name)
    if yandex_token:
        updates.append('yandex_token = ?')
        params.append(yandex_token)

    if not updates:
        return False

    updates.append('updated_at = ?')
    params.append(datetime.utcnow().isoformat())
    params.extend([account_id, user_id])

    conn = get_db_connection()
    result = conn.execute(
        f'UPDATE yandex_accounts SET {", ".join(updates)} WHERE id = ? AND user_id = ?',
        params
    )
    conn.commit()
    conn.close()
    return result.rowcount > 0


def delete_yandex_account(account_id: str, user_id: str) -> bool:
    """Delete Yandex account."""
    conn = get_db_connection()
    result = conn.execute(
        'DELETE FROM yandex_accounts WHERE id = ? AND user_id = ?',
        (account_id, user_id)
    )
    conn.commit()
    conn.close()
    return result.rowcount > 0


def toggle_yandex_account(account_id: str, user_id: str, is_active: bool) -> bool:
    """Toggle Yandex account active status."""
    now = datetime.utcnow().isoformat()
    conn = get_db_connection()
    result = conn.execute(
        'UPDATE yandex_accounts SET is_active = ?, updated_at = ? WHERE id = ? AND user_id = ?',
        (1 if is_active else 0, now, account_id, user_id)
    )
    conn.commit()
    conn.close()
    return result.rowcount > 0


# ============== Audit History ==============

def create_audit(user_id: str, yandex_account_id: str, audit_type: str) -> str:
    """Create a new audit record."""
    audit_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    conn = get_db_connection()
    conn.execute(
        '''INSERT INTO audit_history
           (id, user_id, yandex_account_id, audit_type, status, created_at)
           VALUES (?, ?, ?, ?, 'pending', ?)''',
        (audit_id, user_id, yandex_account_id, audit_type, now)
    )
    conn.commit()
    conn.close()
    return audit_id


def update_audit_status(audit_id: str, status: str, result: str = None) -> bool:
    """Update audit status and result."""
    now = datetime.utcnow().isoformat()
    conn = get_db_connection()

    if result:
        conn.execute(
            'UPDATE audit_history SET status = ?, result = ?, completed_at = ? WHERE id = ?',
            (status, result, now, audit_id)
        )
    else:
        conn.execute(
            'UPDATE audit_history SET status = ? WHERE id = ?',
            (status, audit_id)
        )

    conn.commit()
    conn.close()
    return True


def get_audit_history(user_id: str, limit: int = 50) -> list:
    """Get audit history for user."""
    conn = get_db_connection()
    audits = conn.execute(
        '''SELECT ah.*, ya.account_name, ya.yandex_login
           FROM audit_history ah
           JOIN yandex_accounts ya ON ah.yandex_account_id = ya.id
           WHERE ah.user_id = ?
           ORDER BY ah.created_at DESC
           LIMIT ?''',
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [dict(audit) for audit in audits]


def get_audit(audit_id: str, user_id: str = None) -> dict | None:
    """Get audit by ID."""
    conn = get_db_connection()
    if user_id:
        audit = conn.execute(
            'SELECT * FROM audit_history WHERE id = ? AND user_id = ?',
            (audit_id, user_id)
        ).fetchone()
    else:
        audit = conn.execute(
            'SELECT * FROM audit_history WHERE id = ?',
            (audit_id,)
        ).fetchone()
    conn.close()
    return dict(audit) if audit else None

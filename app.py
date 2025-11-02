import os
import sys
import logging
import requests
from flask import Flask, redirect, url_for, session, request, render_template, flash, jsonify
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Import with error handling
try:
    import db
    from yandex_api import YandexDirectAPI
    logger.info("Successfully imported db and yandex_api modules")
except Exception as e:
    logger.error(f"Failed to import modules: {e}", exc_info=True)
    raise

app = Flask(__name__)
# Use environment variable for secret key or generate a stable one
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-' + os.getenv('RAILWAY_ENVIRONMENT', 'local'))

YANDEX_CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
YANDEX_CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")
# Use Railway public URL or fallback to localhost
REDIRECT_URI = os.getenv("REDIRECT_URI", 'http://localhost:5000/redirect')

logger.info(f"App configured with REDIRECT_URI: {REDIRECT_URI}")
logger.info(f"YANDEX_CLIENT_ID configured: {bool(YANDEX_CLIENT_ID)}")

@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    db.init_db()
    print('Initialized the database.')

# Initialize database on startup if it doesn't exist
def init_db_if_needed():
    """Initialize database if it doesn't exist"""
    try:
        import os.path
        if not os.path.isfile('database.db'):
            logger.info('Database not found, initializing...')
            db.init_db()
            logger.info('Database initialized successfully')
        else:
            logger.info('Database already exists')
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise

# Use before_first_request to initialize DB only once
@app.before_request
def before_first_request():
    """Initialize on first request"""
    if not hasattr(app, '_db_initialized'):
        init_db_if_needed()
        app._db_initialized = True

@app.route('/')
def index():
    try:
        logger.info("Index route called")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        return f"Error: {str(e)}", 500

@app.route('/favicon.ico')
def favicon():
    """Return 204 No Content for favicon to avoid 502 errors"""
    return '', 204

@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

@app.route('/login')
def login():
    if not YANDEX_CLIENT_ID or YANDEX_CLIENT_ID == 'YOUR_CLIENT_ID':
        flash('YANDEX_CLIENT_ID is not set in .env file. Please create an app on Yandex.OAuth and set the credentials.', 'error')
        return render_template('index.html')

    yandex_oauth_url = (
        f"https://oauth.yandex.ru/authorize?response_type=code"
        f"&client_id={YANDEX_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(yandex_oauth_url)

@app.route('/redirect')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided.", 400

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

        info_url = "https://login.yandex.ru/info"
        headers = {'Authorization': f'OAuth {access_token}'}
        info_response = requests.get(info_url, headers=headers)
        info_response.raise_for_status()
        user_info = info_response.json()
        yandex_login = user_info['login']

        secret_code = db.save_token(yandex_login, access_token)

        flash(f"Successfully authenticated as {yandex_login}. Your secret code is: {secret_code}", 'success')
        return redirect(url_for('index'))

    except requests.exceptions.RequestException as e:
        return f"Error during authentication: {e}", 500

# --- API Endpoints ---

def _get_api_client_from_request():
    """Helper function to authenticate and get an API client."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, (jsonify({"error": "Authorization header is missing"}), 401)

    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return None, (jsonify({"error": "Invalid Authorization header format. Expected 'Bearer <token>'"}), 401)

    secret_code = parts[1]
    user = db.get_user_by_secret_code(secret_code)

    if not user:
        return None, (jsonify({"error": "Invalid secret code"}), 401)

    api = YandexDirectAPI(token=user['yandex_token'], login=user['yandex_login'])
    return api, None

def _handle_api_exception(e):
    """Helper function to format API exceptions."""
    error_message = f"Yandex API request failed: {e}"
    if e.response is not None:
            try:
                error_details = e.response.json()
                error_message = error_details.get('error', {}).get('error_detail', error_message)
            except ValueError:
                pass # response is not json
    return jsonify({"error": error_message}), 500

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns_api():
    api, error_response = _get_api_client_from_request()
    if error_response:
        return error_response

    try:
        campaigns = api.get_campaigns()
        return jsonify(campaigns)
    except requests.exceptions.RequestException as e:
        return _handle_api_exception(e)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/adgroups', methods=['POST'])
def get_adgroups_api():
    api, error_response = _get_api_client_from_request()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'campaign_ids' not in data:
        return jsonify({"error": "Missing 'campaign_ids' in request body"}), 400

    try:
        adgroups = api.get_adgroups(campaign_ids=data['campaign_ids'])
        return jsonify(adgroups)
    except requests.exceptions.RequestException as e:
        return _handle_api_exception(e)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/ads', methods=['POST'])
def get_ads_api():
    api, error_response = _get_api_client_from_request()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'adgroup_ids' not in data:
        return jsonify({"error": "Missing 'adgroup_ids' in request body"}), 400

    try:
        ads = api.get_ads(adgroup_ids=data['adgroup_ids'])
        return jsonify(ads)
    except requests.exceptions.RequestException as e:
        return _handle_api_exception(e)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/keywords', methods=['POST'])
def get_keywords_api():
    api, error_response = _get_api_client_from_request()
    if error_response:
        return error_response

    data = request.get_json()
    if not data or 'adgroup_ids' not in data:
        return jsonify({"error": "Missing 'adgroup_ids' in request body"}), 400

    try:
        keywords = api.get_keywords(adgroup_ids=data['adgroup_ids'])
        return jsonify(keywords)
    except requests.exceptions.RequestException as e:
        return _handle_api_exception(e)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

@app.route('/api/reports', methods=['POST'])
def get_reports_api():
    api, error_response = _get_api_client_from_request()
    if error_response:
        return error_response

    report_definition = request.get_json()
    if not report_definition:
        return jsonify({"error": "Missing report definition in request body"}), 400

    try:
        report_data = api.get_report(report_definition=report_definition)
        return report_data, 200, {'Content-Type': 'text/tab-separated-values; charset=utf-8'}
    except requests.exceptions.RequestException as e:
        return _handle_api_exception(e)
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    # Railway provides PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask development server on port {port}")
    # Listen on all interfaces for Railway
    app.run(host='0.0.0.0', port=port, debug=False)

# Log application startup
logger.info("Flask application module loaded successfully")
logger.info(f"Python version: {sys.version}")
logger.info(f"Flask app name: {app.name}")

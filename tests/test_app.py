import pytest
from app import app as flask_app
import db
from yandex_api import YandexDirectAPI

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.init_db()
        yield client

@pytest.fixture
def auth_headers():
    """Provides valid authorization headers."""
    return {'Authorization': 'Bearer valid-secret-code'}

@pytest.fixture
def mock_user_db(mocker):
    """Mocks the database call to get a user."""
    mock_user = {
        'id': 1,
        'yandex_login': 'testuser',
        'yandex_token': 'fake-yandex-token',
        'secret_code': 'valid-secret-code'
    }
    mocker.patch('db.get_user_by_secret_code', return_value=mock_user)

def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Login with Yandex" in response.data

def test_login_redirect(client):
    """Test the login route redirects to Yandex OAuth."""
    response = client.get('/login')
    assert response.status_code == 302
    assert 'oauth.yandex.ru/authorize' in response.location

def test_api_no_auth(client):
    """Test API endpoints without an auth header."""
    endpoints = ['/api/campaigns', '/api/adgroups', '/api/ads', '/api/keywords', '/api/reports']
    for endpoint in endpoints:
        if endpoint == '/api/campaigns':
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={}) # Send json to avoid 415
        assert response.status_code == 401
        json_data = response.get_json()
        assert "Authorization header is missing" in json_data['error']

def test_api_invalid_token(client):
    """Test API endpoints with an invalid secret code."""
    headers = {'Authorization': 'Bearer invalid-token'}
    endpoints = ['/api/campaigns', '/api/adgroups', '/api/ads', '/api/keywords', '/api/reports']
    for endpoint in endpoints:
        if endpoint == '/api/campaigns':
            response = client.get(endpoint, headers=headers)
        else:
            response = client.post(endpoint, headers=headers, json={}) # Send json to avoid 415
        assert response.status_code == 401
        json_data = response.get_json()
        assert "Invalid secret code" in json_data['error']

def test_api_campaigns_valid(client, mocker, auth_headers, mock_user_db):
    """Test the campaigns API with a valid secret code."""
    mock_response = {"result": {"Campaigns": [{"Id": 1, "Name": "Test"}]}}
    mocker.patch.object(YandexDirectAPI, 'get_campaigns', return_value=mock_response)

    response = client.get('/api/campaigns', headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == mock_response
    YandexDirectAPI.get_campaigns.assert_called_once()

def test_api_adgroups_valid(client, mocker, auth_headers, mock_user_db):
    """Test the adgroups API with valid input."""
    mock_response = {"result": {"AdGroups": [{"Id": 1, "Name": "AdGroup"}]}}
    mocker.patch.object(YandexDirectAPI, 'get_adgroups', return_value=mock_response)

    response = client.post('/api/adgroups', headers=auth_headers, json={'campaign_ids': [123]})

    assert response.status_code == 200
    assert response.get_json() == mock_response
    YandexDirectAPI.get_adgroups.assert_called_once_with(campaign_ids=[123])

def test_api_post_endpoints_invalid_body(client, auth_headers, mock_user_db):
    """Test POST API endpoints with an invalid or missing body."""
    endpoints = {
        '/api/adgroups': 'campaign_ids',
        '/api/ads': 'adgroup_ids',
        '/api/keywords': 'adgroup_ids',
        '/api/reports': 'report definition' # Special case for reports
    }
    for endpoint, id_field in endpoints.items():
        # Test with empty json body
        response = client.post(endpoint, headers=auth_headers, json={})
        assert response.status_code == 400
        json_data = response.get_json()
        if endpoint == '/api/reports':
            assert "Missing report definition" in json_data['error']
        else:
            assert f"Missing '{id_field}'" in json_data['error']

        # Test with None json body
        response = client.post(endpoint, headers=auth_headers, content_type='application/json', data=None)
        assert response.status_code == 400

def test_api_ads_valid(client, mocker, auth_headers, mock_user_db):
    """Test the ads API with valid input."""
    mock_response = {"result": {"Ads": [{"Id": 1, "Type": "TEXT_AD"}]}}
    mocker.patch.object(YandexDirectAPI, 'get_ads', return_value=mock_response)

    response = client.post('/api/ads', headers=auth_headers, json={'adgroup_ids': [456]})

    assert response.status_code == 200
    assert response.get_json() == mock_response
    YandexDirectAPI.get_ads.assert_called_once_with(adgroup_ids=[456])

def test_api_keywords_valid(client, mocker, auth_headers, mock_user_db):
    """Test the keywords API with valid input."""
    mock_response = {"result": {"Keywords": [{"Id": 1, "Keyword": "test"}]}}
    mocker.patch.object(YandexDirectAPI, 'get_keywords', return_value=mock_response)

    response = client.post('/api/keywords', headers=auth_headers, json={'adgroup_ids': [789]})

    assert response.status_code == 200
    assert response.get_json() == mock_response
    YandexDirectAPI.get_keywords.assert_called_once_with(adgroup_ids=[789])

def test_api_reports_valid(client, mocker, auth_headers, mock_user_db):
    """Test the reports API with a valid report definition."""
    mock_report_def = {"ReportName": "Test Report", "ReportType": "CUSTOM_REPORT", "DateRangeType": "TODAY"}
    mock_response_text = "Date\tCampaign\tClicks\n2025-08-07\tTest\t10"
    mocker.patch.object(YandexDirectAPI, 'get_report', return_value=mock_response_text)

    response = client.post('/api/reports', headers=auth_headers, json=mock_report_def)

    assert response.status_code == 200
    assert response.data.decode('utf-8') == mock_response_text
    assert 'text/tab-separated-values' in response.content_type
    YandexDirectAPI.get_report.assert_called_once_with(report_definition=mock_report_def)

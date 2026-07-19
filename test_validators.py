import pytest
from app.api import app
from app.validators import parse_int_param, parse_enum_param, parse_ts_param

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_parse_int_param(client):
    response = client.get('/api/feed?limit=abc')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid limit: invalid literal for int() with base 10: 'abc'"}

    response = client.get('/api/feed?limit=-1')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid limit: limit must be between 1 and 100"}

    response = client.get('/api/feed?limit=150')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid limit: limit must be between 1 and 100"}

    response = client.get('/api/feed?limit=10')
    assert response.status_code == 200

def test_parse_enum_param(client):
    response = client.get('/api/feed?category=invalid')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid category: invalid is not one of ['news','sports', 'entertainment']"}

    response = client.get('/api/feed?category=sports')
    assert response.status_code == 200

def test_parse_ts_param(client):
    response = client.get('/api/feed?since=abc')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid since: abc does not match format %Y-%m-%d"}

    response = client.get('/api/feed?since=2023-01-01')
    assert response.status_code == 200

def test_api_feed(client):
    response = client.get('/api/feed?limit=10&offset=0&page=1&since=2023-01-01&before=2023-01-02&category=sports&sort=desc')
    assert response.status_code == 200

def test_api_trending(client):
    response = client.get('/api/trending?limit=10&days=7&since=2023-01-01')
    assert response.status_code == 200

def test_api_videos(client):
    response = client.get('/api/videos?page=1')
    assert response.status_code == 200

def test_api_related_videos(client):
    response = client.get('/api/videos/123/related?limit=10')
    assert response.status_code == 200
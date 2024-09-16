import pytest
from database import SessionLocal, init_db
from app import app
import json
import os

@pytest.fixture(scope='module', autouse=True)
def setup_database():
    init_db() 
    yield

@pytest.fixture
def client():
    """Создаем тестового клиента для приложения Flask."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:test@localhost/test_db')
    client = app.test_client()
    yield client

def test_ping(client):
    """Тестируем доступность сервера."""
    response = client.get('/api/ping')
    assert response.status_code == 200
    assert response.data == b'ok'

def test_create_and_edit_tender(client):
    tender_data = {
        "name": "Tender 1",
        "description": "Description of tender",
        "serviceType": "Construction",
        "organizationId": 1,
        "creatorUserId": 1
    }
    create_response = client.post('/api/tenders/new', data=json.dumps(tender_data), content_type='application/json')
    assert create_response.status_code == 200
    tender_id = create_response.get_json()['id']

    # Edit tender
    tender_edit_data = {
        "name": "Updated Tender",
        "description": "Updated description"
    }
    edit_response = client.patch(f'/api/tenders/{tender_id}/edit', data=json.dumps(tender_edit_data), content_type='application/json')
    assert edit_response.status_code == 200


def test_publish_tender(client):
    """Тестируем публикацию тендера."""
    response = client.post('/api/tenders/1/publish')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Tender published"

def test_close_tender(client):
    """Тестируем закрытие тендера."""
    response = client.post('/api/tenders/1/close')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Tender closed"

def test_rollback_tender(client):
    """Тестируем откат версии тендера."""
    response = client.put('/api/tenders/1/rollback/1')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "rolled back" in json_data['message']

def test_create_bid(client):
    org_data = {
        "name": "Test Organization",
        "description": "An organization for testing",
        "type": "Construction"
    }
    client.post('/api/organizations/new', data=json.dumps(org_data), content_type='application/json')
    
    tender_data = {
        "name": "Test Tender",
        "description": "Test tender description",
        "serviceType": "Construction",
        "organizationId": 1,
        "creatorUserId": 1
    }
    client.post('/api/tenders/new', data=json.dumps(tender_data), content_type='application/json')
    
    bid_data = {
        "name": "Test Bid",
        "description": "A bid for testing",
        "tenderId": 1,
        "organizationId": 1
    }
    response = client.post('/api/bids/new', data=json.dumps(bid_data), content_type='application/json')
    assert response.status_code == 200


def test_edit_bid(client):
    """Тестируем редактирование предложения."""
    bid_edit_data = {
        "name": "Обновленное Предложение",
        "description": "Обновленное описание"
    }
    response = client.patch('/api/bids/1/edit', data=json.dumps(bid_edit_data), content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['name'] == "Обновленное Предложение"
    assert json_data['description'] == "Обновленное описание"

def test_publish_bid(client):
    """Тестируем публикацию предложения."""
    response = client.post('/api/bids/1/publish')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Bid published"

def test_rollback_bid(client):
    """Тестируем откат версии предложения."""
    response = client.put('/api/bids/1/rollback/1')
    assert response.status_code == 200
    json_data = response.get_json()
    assert "rolled back" in json_data['message']

def test_decision_bid_accept(client):
    """Тестируем согласование предложения."""
    decision_data = {
        "decision": "accept"
    }
    response = client.post('/api/bids/1/decision', data=json.dumps(decision_data), content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Bid accepted"

def test_decision_bid_reject(client):
    """Тестируем отклонение предложения."""
    decision_data = {
        "decision": "reject"
    }
    response = client.post('/api/bids/1/decision', data=json.dumps(decision_data), content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Bid rejected"


from fastapi.testclient import TestClient
from app.main import create_app
import pytest

@pytest.fixture
def client():
    with TestClient(create_app()) as c:
        yield c

def test_health(client):
    assert client.get('/health').json() == {'status': 'ok'}

def test_create_ticket(client):
    r = client.post('/tickets', json={'name': 'Maria'})
    assert r.status_code == 201
    assert r.json()['status'] == 'esperando'

def test_create_preferred(client):
    r = client.post('/tickets', json={'name':'Rita','priority':'preferencial'})
    assert r.json()['priority'] == 'preferencial'

def test_blank_name(client):
    assert client.post('/tickets', json={'name':' '}).status_code == 422

def test_empty_name(client):
    assert client.post('/tickets', json={'name':''}).status_code == 422

def test_invalid_priority(client):
    assert client.post('/tickets', json={'name':'Luiz','priority':'super'}).status_code == 422

def test_get_missing(client):
    assert client.get('/tickets/99').status_code == 404

def test_finish_missing(client):
    assert client.post('/tickets/99/finish').status_code == 404

def test_next_empty(client):
    assert client.post('/tickets/next').status_code == 409

def test_full_flow(client):
    first = client.post('/tickets', json={'name': 'A'}).json()['id']
    second = client.post('/tickets', json={'name': 'B', 'priority': 'preferencial'}).json()['id']
    assert len(client.get('/tickets').json()) == 2
    assert len(client.get('/tickets?status=esperando').json()) == 2
    assert client.get(f'/tickets/{first}').status_code == 200
    assert client.post('/tickets/next').json()['id'] == second
    assert client.post(f'/tickets/{first}/finish').status_code == 409
    assert client.post(f'/tickets/{second}/finish').json()['status'] == 'concluido'
    assert client.post('/tickets/next').json()['id'] == first

def test_invalid_status_filter(client):
    assert client.get('/tickets?status=invalid').status_code == 422

def test_isolated_test_client_state(client):
    assert client.get('/tickets').json() == []

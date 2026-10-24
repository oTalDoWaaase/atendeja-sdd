from fastapi.testclient import TestClient
from app.main import STATIC_DIR, create_app
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

def test_name_padded_to_max_length_accepted(client):
    # Regressão: a API rejeitava o nome antes de remover espaços, divergindo do domínio.
    r = client.post('/tickets', json={'name': '  ' + 'x' * 80 + '  '})
    assert r.status_code == 201
    assert r.json()['name'] == 'x' * 80

def test_name_too_long_after_trim(client):
    assert client.post('/tickets', json={'name': ' ' + 'x' * 81 + ' '}).status_code == 422

def test_name_is_trimmed(client):
    assert client.post('/tickets', json={'name': '  Ana  '}).json()['name'] == 'Ana'

def test_missing_name(client):
    assert client.post('/tickets', json={'priority': 'normal'}).status_code == 422

def test_not_found_detail_message(client):
    # Regressão: str(KeyError) incluía aspas extras na mensagem.
    assert client.get('/tickets/99').json() == {'detail': 'Senha não encontrada.'}
    assert client.post('/tickets/99/finish').json() == {'detail': 'Senha não encontrada.'}

def test_next_empty_detail(client):
    assert client.post('/tickets/next').json() == {'detail': 'Não há senhas aguardando.'}

def test_finish_waiting_conflict_detail(client):
    ticket_id = client.post('/tickets', json={'name': 'A'}).json()['id']
    r = client.post(f'/tickets/{ticket_id}/finish')
    assert r.status_code == 409
    assert r.json() == {'detail': 'Apenas senhas chamadas podem ser concluídas.'}

def test_queue_empty(client):
    r = client.get('/queue')
    assert r.status_code == 200
    assert r.json() == []

def test_queue_order_and_excludes_non_waiting(client):
    n1 = client.post('/tickets', json={'name': 'N1'}).json()['id']
    p1 = client.post('/tickets', json={'name': 'P1', 'priority': 'preferencial'}).json()['id']
    n2 = client.post('/tickets', json={'name': 'N2'}).json()['id']
    p2 = client.post('/tickets', json={'name': 'P2', 'priority': 'preferencial'}).json()['id']
    assert [t['id'] for t in client.get('/queue').json()] == [p1, p2, n1, n2]
    assert client.post('/tickets/next').json()['id'] == p1
    queue = client.get('/queue').json()
    assert [t['id'] for t in queue] == [p2, n1, n2]
    assert all(t['status'] == 'esperando' for t in queue)

def test_original_contract_routes_preserved(client):
    paths = client.get('/openapi.json').json()['paths']
    expected = {
        '/health': {'get'}, '/tickets': {'get', 'post'}, '/tickets/{ticket_id}': {'get'},
        '/tickets/next': {'post'}, '/tickets/{ticket_id}/finish': {'post'}, '/queue': {'get'},
    }
    for path, methods in expected.items():
        assert methods <= set(paths[path]), path

def test_ticket_output_fields(client):
    body = client.post('/tickets', json={'name': 'Ana'}).json()
    assert set(body) == {'id', 'name', 'priority', 'status', 'created_at'}

def test_web_interface_served(client):
    r = client.get('/')
    assert r.status_code == 200
    assert r.headers['content-type'].startswith('text/html')
    assert 'AtendeJá' in r.text
    assert "default-src 'self'" in r.headers['content-security-policy']
    assert r.headers['x-content-type-options'] == 'nosniff'

@pytest.mark.parametrize('asset, content_type', [('app.js', 'javascript'), ('styles.css', 'text/css')])
def test_static_assets_served(client, asset, content_type):
    r = client.get(f'/static/{asset}')
    assert r.status_code == 200
    assert content_type in r.headers['content-type']

def test_static_missing_asset(client):
    assert client.get('/static/nao-existe.js').status_code == 404

def test_web_interface_does_not_inject_html():
    # Guarda contra XSS: nomes de clientes devem ser renderizados apenas via textContent.
    source = (STATIC_DIR / 'app.js').read_text(encoding='utf-8')
    for sink in ('innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval('):
        assert sink not in source

def test_web_interface_uses_only_existing_routes():
    source = (STATIC_DIR / 'app.js').read_text(encoding='utf-8')
    for route in ("'/tickets'", "'/queue'", "'/tickets/next'", '/finish'):
        assert route in source

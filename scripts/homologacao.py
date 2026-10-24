"""Roteiro de homologação da API contra um servidor em execução.

Uso: python scripts/homologacao.py [URL_BASE]   (padrão: http://127.0.0.1:8000)
Requer um servidor recém-iniciado (fila vazia). Sai com código 1 se algum cenário falhar.
"""
import sys
from concurrent.futures import ThreadPoolExecutor

import httpx

EXPECTED_VERSION = '1.0.0'


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def h01_health(client):
    r = client.get('/health')
    check(r.status_code == 200 and r.json() == {'status': 'ok'}, f'health: {r.status_code} {r.text}')


def h02_painel(client):
    r = client.get('/')
    check(r.status_code == 200 and 'AtendeJá' in r.text, f'painel: {r.status_code}')
    check("default-src 'self'" in r.headers.get('content-security-policy', ''), 'CSP ausente')
    for asset in ('/static/app.js', '/static/styles.css'):
        check(client.get(asset).status_code == 200, f'{asset} indisponível')


def h03_validacao(client):
    invalid = [{'name': ''}, {'name': '   '}, {'name': 'x' * 81}, {'name': 'Ana', 'priority': 'vip'}, {}]
    for payload in invalid:
        r = client.post('/tickets', json=payload)
        check(r.status_code == 422, f'{payload!r} deveria ser 422, veio {r.status_code}')
    check(client.get('/tickets').json() == [], 'entrada inválida não pode criar senha')


def h04_fila_e_prioridade(client):
    names = [('N1', 'normal'), ('P1', 'preferencial'), ('N2', 'normal'), ('P2', 'preferencial')]
    ids = {name: client.post('/tickets', json={'name': name, 'priority': p}).json()['id'] for name, p in names}
    expected = [ids['P1'], ids['P2'], ids['N1'], ids['N2']]
    check([t['id'] for t in client.get('/queue').json()] == expected, 'ordem de GET /queue')
    called = [client.post('/tickets/next').json()['id'] for _ in expected]
    check(called == expected, f'ordem de chamada {called} != {expected}')
    check(client.post('/tickets/next').status_code == 409, 'fila vazia deveria retornar 409')


def h05_transicoes(client):
    ticket = client.post('/tickets', json={'name': 'Transição'}).json()
    check(client.post(f"/tickets/{ticket['id']}/finish").status_code == 409, 'concluir senha em espera')
    check(client.post('/tickets/next').json()['id'] == ticket['id'], 'chamada')
    check(client.post(f"/tickets/{ticket['id']}/finish").json()['status'] == 'concluido', 'conclusão')
    check(client.post(f"/tickets/{ticket['id']}/finish").status_code == 409, 'concluir duas vezes')
    check(client.post('/tickets/999999/finish').status_code == 404, 'concluir inexistente')
    check(client.get('/tickets/999999').status_code == 404, 'consultar inexistente')


def h06_filtros(client):
    by_status = {s: len(client.get('/tickets', params={'status': s}).json())
                 for s in ('esperando', 'chamado', 'concluido')}
    check(sum(by_status.values()) == len(client.get('/tickets').json()), f'filtros inconsistentes {by_status}')
    check(client.get('/tickets', params={'status': 'x'}).status_code == 422, 'filtro inválido')


def h07_concorrencia(client, total=60, workers=12):
    for i in range(total):
        client.post('/tickets', json={'name': f'Concorrente {i}'})

    def call(_):
        return client.post('/tickets/next')

    with ThreadPoolExecutor(max_workers=workers) as pool:
        responses = list(pool.map(call, range(total + workers)))
    called = [r.json()['id'] for r in responses if r.status_code == 200]
    conflicts = sum(r.status_code == 409 for r in responses)
    check(len(called) == total and len(set(called)) == total, f'{len(called)} chamadas, {len(set(called))} únicas')
    check(conflicts == workers, f'esperados {workers} conflitos 409, vieram {conflicts}')


def h08_contrato_e_versao(client):
    spec = client.get('/openapi.json').json()
    check(spec['info']['version'] == EXPECTED_VERSION, f"versão {spec['info']['version']}")
    for path in ('/health', '/tickets', '/tickets/{ticket_id}', '/tickets/next',
                 '/tickets/{ticket_id}/finish', '/queue'):
        check(path in spec['paths'], f'rota ausente: {path}')


SCENARIOS = [h01_health, h02_painel, h03_validacao, h04_fila_e_prioridade,
             h05_transicoes, h06_filtros, h07_concorrencia, h08_contrato_e_versao]


def run(client):
    """Executa todos os cenários em ordem e devolve [(nome, erro ou None)]."""
    results = []
    for scenario in SCENARIOS:
        try:
            scenario(client)
            results.append((scenario.__name__, None))
        except Exception as error:  # registra a falha e segue para os demais cenários
            results.append((scenario.__name__, f'{type(error).__name__}: {error}'))
    return results


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8000'
    with httpx.Client(base_url=base_url, timeout=10) as client:
        results = run(client)
    for name, error in results:
        print(f"{'PASS' if error is None else 'FAIL'}  {name}" + (f'  -> {error}' if error else ''))
    failed = sum(error is not None for _, error in results)
    print(f'\n{len(results) - failed}/{len(results)} cenários aprovados em {base_url}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())

"""Executa o roteiro de homologação (scripts/homologacao.py) em processo, para que não fique desatualizado."""
from fastapi.testclient import TestClient
from app.main import create_app
from scripts.homologacao import SCENARIOS, run

def test_homologation_script_passes_in_process():
    with TestClient(create_app()) as client:
        results = run(client)
    assert [name for name, _ in results] == [s.__name__ for s in SCENARIOS]
    assert [(name, error) for name, error in results if error] == []

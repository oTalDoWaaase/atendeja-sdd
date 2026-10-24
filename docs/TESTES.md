# Evidências de testes

Comando (o mesmo do CI): `python -m pytest -v --junitxml=test-results.xml`

## Execução v1.1 — 24/10/2026 (refinamento)
Ambiente: container Linux de nuvem do Claude Code, executado pelo agente de IA. Versões instaladas a partir de `requirements.txt`: fastapi 0.162.0, starlette 1.10.0, pydantic 2.14.1, pytest 9.1.1, httpx 0.28.1, uvicorn 0.54.0.

| Execução | Resultado |
|---|---|
| Python 3.12.3 (mesma versão-alvo do CI), gera `test-results.xml` | **53 passed, 1 warning in 0.76s** |
| Python 3.13.17 | 53 passed |
| Testes de concorrência repetidos 25 vezes | 25/25 com 2 passed |
| Testes de regressão R1–R3 contra o código original (`main`) | **4 failed** (esperado: provam que detectam os defeitos) |
| `docker compose run --build --rm tests` | **Não executado**: daemon Docker indisponível neste ambiente |
| GitHub Actions | **Não verificado**: a branch ainda não foi publicada |

Aviso único da execução: `StarletteDeprecationWarning` sobre usar `httpx` com `starlette.testclient`, vindo da versão do Starlette instalada; não afeta os resultados.

Distribuição: 24 testes de domínio (`tests/test_domain.py`) e 29 de API/painel (`tests/test_api.py`). Base v1.0: 29 testes, todos mantidos sem alteração.

## Verificação manual ponta a ponta do painel (fora do CI)
Roteiro executado com Chromium (Playwright pré-instalado no ambiente, **não** adicionado ao projeto) contra `uvicorn app.main:app`:
- Submeter nome vazio exibe erro no formulário sem chamar a API.
- Cadastro de N, P, N, P resultou na fila `P-002 P-004 N-001 N-003`, igual à regra RF04.
- Nome `<img src=x onerror=alert(1)>` exibido como texto; nenhum elemento `<img>` criado.
- Chamar duas vezes, concluir uma: contadores `2/0/1/1` (aguardando/preferenciais/em atendimento/concluídos).
- Com a fila vazia, o botão "Chamar próximo" fica desabilitado.
- Largura de 375 px em modo escuro: sem rolagem horizontal.
- Nenhum erro no console do navegador.

Capturas: [desktop](img/painel-desktop.png), [celular, modo escuro](img/painel-celular-escuro.png). O script do roteiro não foi versionado, para não adicionar dependência de Node/Playwright ao projeto.

## Limitações da evidência
- Resultados obtidos no ambiente de preparação; não comprovam execução no GitHub Actions nem no computador do aluno. Repetir localmente e conferir o CI após publicar a branch.
- Cobertura de linhas/branches não foi medida (exigiria a dependência `pytest-cov`).
- Os testes de concorrência reduzem o intervalo de troca de threads para expor corridas; são fortes evidências, mas não uma prova formal de ausência de corrida.
- Usabilidade e acessibilidade com tecnologias assistivas não foram testadas com pessoas.

## Histórico
- v1.0 (Entrega 2), 24/10/2026: 29 passed in 0.60s, registrado na entrega original.
- v1.1, 24/10/2026: ver acima. Defeitos e regressões em [REFINAMENTOS.md](REFINAMENTOS.md).

# AtendeJá — Gerenciamento de Fila de Atendimento

Projeto acadêmico individual: API REST e painel web que criam senhas, ordenam atendimentos por prioridade (preferencial antes de normal, FIFO dentro de cada prioridade), chamam o próximo cliente e concluem atendimentos.

**Versão:** 1.0.0 (release em homologação, ainda não publicada). **Testes:** 57, com 100% de cobertura de linhas e ramos em `app/`. Detalhes em [docs/HOMOLOGACAO.md](docs/HOMOLOGACAO.md).

![Painel AtendeJá no desktop](docs/img/painel-desktop.png)

## Tecnologias
Python 3.12+, FastAPI, Uvicorn, Pydantic 2; pytest, pytest-cov e HTTPX para testes; Docker e GitHub Actions. O painel usa HTML, CSS e JavaScript puros servidos pela própria API, sem etapa de build.

## Requisitos de ambiente
| Opção | Precisa de |
|---|---|
| Com Docker | Docker Engine com Compose v2 (`docker compose`) |
| Sem Docker | Python 3.12 ou superior e `pip` |

A aplicação não usa variáveis de ambiente, banco de dados nem serviços externos. Porta padrão: **8000**.

## Opção 1 — Docker
```bash
# API + painel em http://127.0.0.1:8000/
docker compose up --build api

# Suíte de testes com cobertura dentro do container
docker compose run --build --rm tests
```
O `Dockerfile` tem dois estágios. `runtime` só contém as dependências de execução e roda como o usuário não-root `atendeja`. `test` acrescenta as ferramentas de teste. Para parar: `Ctrl+C` ou `docker compose down`.

## Opção 2 — Sem Docker
```bash
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# Linux/macOS:         source .venv/bin/activate

# Só para executar:
python -m pip install -r requirements.txt
# Para executar e testar (inclui o anterior):
python -m pip install -r requirements-dev.txt

python -m uvicorn app.main:app --reload
```
- Painel: http://127.0.0.1:8000/
- Documentação interativa da API (Swagger): http://127.0.0.1:8000/docs

Execute com **um único worker** (não use `--workers N`): a fila fica na memória do processo.

## Testes e cobertura
```bash
python -m pytest -v                                    # suíte completa
python -m pytest --cov                                 # + cobertura no terminal (mínimo 95%)
python -m pytest --cov --cov-report=term-missing \
  --cov-report=xml --cov-report=html \
  --junitxml=test-results.xml                          # relatórios como no CI
```
Relatórios gerados: `coverage.xml`, `htmlcov/index.html` (abra no navegador) e `test-results.xml`. Eles são ignorados pelo Git. A evidência congelada da homologação está em [`docs/evidencias/`](docs/evidencias/). A configuração fica em `pyproject.toml`.

| Arquivo de teste | Testes | Foco |
|---|---|---|
| `tests/test_domain.py` | 24 | Regras, estados, prioridade, concorrência |
| `tests/test_api.py` | 32 | Contratos HTTP, erros, painel e cabeçalhos |
| `tests/test_homologacao.py` | 1 | Executa o roteiro de homologação em processo |

### Homologação contra um servidor em execução
Com a API no ar e a fila vazia (servidor recém-iniciado, local ou Docker):
```bash
python scripts/homologacao.py                   # padrão: http://127.0.0.1:8000
python scripts/homologacao.py http://host:porta
```
Saída esperada: `8/8 cenários aprovados`. O código de saída é 1 se algum cenário falhar.

## Integração contínua
`.github/workflows/ci.yml` roda em push para `main`, `develop` e `feature/**`, e em PRs para `main`/`develop`. Ele instala `requirements-dev.txt`, executa a suíte com cobertura e falha se a cobertura ficar abaixo de 95%. Publica os artefatos `teste-junit` (JUnit) e `cobertura` (`coverage.xml` + `htmlcov/`) e um resumo da cobertura na página do job.

## Uso rápido da API
```bash
curl -X POST http://127.0.0.1:8000/tickets -H 'Content-Type: application/json' -d '{"name":"Ana","priority":"preferencial"}'
curl http://127.0.0.1:8000/queue
curl -X POST http://127.0.0.1:8000/tickets/next
curl -X POST http://127.0.0.1:8000/tickets/1/finish
```

| Método e rota | Resposta |
|---|---|
| `POST /tickets` | 201 senha; 422 entrada inválida |
| `GET /tickets?status=` | 200 lista (filtro opcional: `esperando`, `chamado`, `concluido`) |
| `GET /tickets/{id}` | 200 senha; 404 inexistente |
| `POST /tickets/next` | 200 senha chamada; 409 fila vazia |
| `POST /tickets/{id}/finish` | 200 concluída; 404 inexistente; 409 transição inválida |
| `GET /queue` | 200 senhas em espera na ordem de chamada |
| `GET /health` | 200 `{"status":"ok"}` |

Contratos completos, regras de negócio e arquitetura: [docs/SDD.md](docs/SDD.md).

## Estrutura
```
app/
  __init__.py        versão (1.0.0)
  domain.py          regras de negócio: fila, prioridade, estados, lock
  main.py            camada HTTP (FastAPI), painel e cabeçalhos de segurança
  static/            painel web (index.html, styles.css, app.js)
tests/               testes de domínio, API e homologação
scripts/homologacao.py   roteiro de homologação contra servidor real
docs/                SDD, ADRs, testes, homologação, retrospectiva, release
pyproject.toml       configuração do pytest e da cobertura
requirements.txt     dependências de execução
requirements-dev.txt dependências de teste
```

## Documentação
- [SDD As-Built](docs/SDD.md): especificação definitiva
- [ADRs](docs/DECISOES.md): decisões de arquitetura
- [Homologação](docs/HOMOLOGACAO.md): cenários, evidências, limitações e checklist
- [Registro de testes](docs/TESTES.md) e [refinamentos](docs/REFINAMENTOS.md)
- [Análise técnico-ética de IA](docs/IA-ETICA.md) e [retrospectiva](docs/RETROSPECTIVA.md)
- [Notas da release v1.0.0 (rascunho)](docs/RELEASE-v1.0.0.md)
- [Regras para agentes](AGENTS.md)

## Governança
Fluxo: `main` estável, `develop` para integração e `feature/*` para mudanças, com Pull Requests e checks de CI. O projeto é individual; não se atribuem revisões a colaboradores inexistentes. O desenvolvimento teve apoio de IA (ChatGPT na Entrega 2; Claude Code no refinamento e na Entrega 3), descrito em [IA-ETICA](docs/IA-ETICA.md). Aprovações de PR e da release dependem de homologação humana.

## Limites de produção e segurança
- Sem autenticação, autorização ou rate limit: qualquer pessoa que alcance a porta pode operar a fila.
- Sem armazenamento persistente: reiniciar apaga a fila.
- Sem política de dados pessoais: use apenas nomes fictícios.
- O painel mitiga XSS (renderização como texto e Content-Security-Policy), e a imagem Docker roda sem root, mas isso não substitui uma revisão de segurança.

Não utilize com dados reais de clientes nem exponha publicamente até implementar as proteções necessárias.

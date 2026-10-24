# Homologação — AtendeJá 1.0.0

Registro do que foi **realmente executado** para a Entrega 3, com evidências versionadas em [`evidencias/`](evidencias/). Todas as execuções foram feitas em 24/10/2026 pelo agente de IA (Claude Code), num container Linux de nuvem, na branch `feature/entrega-final`. **Nenhuma etapa foi executada ou aprovada por pessoa até o momento.**

## Ambiente de execução
| Item | Valor |
|---|---|
| SO | Linux (container de nuvem do Claude Code) |
| Python | 3.12.3 (mesma versão-alvo do CI) |
| Pacotes | fastapi 0.162.0, starlette 1.10.0, pydantic 2.14.1, uvicorn 0.54.0, pytest 9.1.1, pytest-cov 7.1.0 (coverage 7.17.0), httpx 0.28.1. Lista completa: [`versoes-ambiente.txt`](evidencias/versoes-ambiente.txt) |
| Docker | Engine 29.9.2, imagem base `python:3.12-slim` |
| Navegador | Chromium headless via Playwright pré-instalado no ambiente (não é dependência do projeto) |

**Ajuste do ambiente, não do projeto:** a rede deste ambiente passa por um proxy TLS com certificado próprio. Para o `pip` funcionar dentro do `docker build`, a imagem local `python:3.12-slim` foi estendida com esse certificado (`PIP_CERT`) e marcada com a mesma tag. O `Dockerfile` do projeto foi construído **sem alterações**. Num ambiente comum, esse ajuste é desnecessário.

## Resultados
### A. Testes automatizados e cobertura
| # | Cenário | Comando | Resultado | Evidência |
|---|---|---|---|---|
| A1 | Suíte da v1.1 antes de qualquer mudança | `python -m pytest -q` | 53 passed | (saída no terminal; nenhum teste falhou) |
| A2 | Cobertura da v1.1 (linha de base) | `pytest --cov=app --cov-branch` | 99%: `app/main.py` linhas 52–53 sem teste | (saída no terminal) |
| A3 | Suíte final com cobertura | `python -m pytest -v --junitxml=test-results.xml --cov --cov-report=term-missing --cov-report=xml --cov-report=html` | **57 passed; 100% de linhas e ramos** em `app/` (129 instruções, 10 ramos) | [`pytest-cobertura.txt`](evidencias/pytest-cobertura.txt), [`coverage.xml`](evidencias/coverage.xml), [`test-results.xml`](evidencias/test-results.xml) |
| A4 | Passos do CI simulados numa cópia limpa (venv novo, `requirements-dev.txt`) | Mesmos comandos de `ci.yml` | 57 passed, 100%; gerou `coverage.xml`, `htmlcov/`, `test-results.xml` e o resumo | — |
| A5 | Validação estática do workflow | `actionlint 1.7.7` | Nenhum problema | — |

Cobertura dos módulos críticos (A3):

| Módulo | Papel | Instruções | Ramos | Cobertura |
|---|---|---|---|---|
| `app/domain.py` | Regras de fila, prioridade, estados, lock | 63 | 10 | **100%** |
| `app/main.py` | Contratos HTTP e mapeamento de erros | 65 | 0 | **100%** |
| `app/__init__.py` | Versão | 1 | 0 | 100% |

A cobertura mede só o Python de `app/`. O JavaScript do painel (`app/static/app.js`) **não** tem medição de cobertura; ele é verificado pelos cenários E. O relatório HTML (`htmlcov/`) não é versionado: é gerado localmente e publicado pelo CI no artefato `cobertura`.

### B. Homologação da API contra servidor real (`scripts/homologacao.py`)
Cenários: `h01_health`, `h02_painel` (HTML, CSP, estáticos), `h03_validacao` (5 entradas inválidas → 422, nenhuma senha criada), `h04_fila_e_prioridade` (`GET /queue` e ordem de chamada P1, P2, N1, N2; 409 com fila vazia), `h05_transicoes` (409/200/409/404), `h06_filtros`, `h07_concorrencia` (60 senhas, 72 chamadas em 12 threads → 60 únicas + 12 conflitos 409), `h08_contrato_e_versao`.

| # | Alvo | Resultado | Evidência |
|---|---|---|---|
| B1 | Container (`docker compose up api`, imagem `runtime`) | **8/8 aprovados** | [`homologacao-docker.txt`](evidencias/homologacao-docker.txt) |
| B2 | Sem Docker (`uvicorn app.main:app`, Python 3.12.3) | **8/8 aprovados** | [`homologacao-local.txt`](evidencias/homologacao-local.txt) |
| B3 | Mesmo roteiro em processo, dentro do pytest | Aprovado (`test_homologation_script_passes_in_process`) | A3 |

### C. Painel no navegador (roteiro manual automatizado com Playwright)
Executado contra o container Docker. Script usado: [`roteiro-navegador.js`](evidencias/roteiro-navegador.js) (requer Node e Playwright, que **não** fazem parte do projeto). Resultado: **12/12** ([`painel-navegador.txt`](evidencias/painel-navegador.txt)).

| # | Cenário | Resultado |
|---|---|---|
| E01 | Painel carrega e indica "Conectado" | PASS |
| E02 | Nome vazio mostra erro sem chamar a API | PASS |
| E03 | Fila exibida em ordem de chamada (`P-002 P-004 N-001 N-003`) | PASS |
| E04 | Nome `<img src=x onerror=alert(1)>` exibido como texto | PASS |
| E05 | "Próximo da fila" correto | PASS |
| E06 | Chamar duas vezes | PASS |
| E07 | Concluir atualiza indicadores (`2/0/1/1`) | PASS |
| E08 | Senha criada por outro cliente aparece sozinha (polling) | PASS |
| E09 | Botão "Chamar próximo" desabilitado com fila vazia | PASS |
| E10 | Cadastro apenas com teclado | PASS |
| E11 | 375 px em modo escuro sem rolagem horizontal | PASS |
| E12 | Nenhum erro no console | PASS |

Capturas geradas nesta execução: [desktop](img/painel-desktop.png), [celular escuro](img/painel-celular-escuro.png).

### D. Docker e execução
| # | Cenário | Resultado | Evidência |
|---|---|---|---|
| D1 | `docker compose run --build --rm tests` | **Falhou na 1ª tentativa**: o usuário não-root não conseguia gravar `.coverage` em `/app` (`SQLITE_CANTOPEN`). Corrigido com `ENV COVERAGE_FILE=/tmp/.coverage`; depois, **57 passed, 100%** | Esta tabela |
| D2 | `docker compose up api` + `/health` | 200 | B1 |
| D3 | Imagem `runtime`: usuário e pacotes | `uid=10001(atendeja)`; `pytest`, `httpx` e `pytest_cov` ausentes; `fastapi` presente | Esta tabela |
| D4 | Reinício do container apaga a fila (limitação esperada) | 65 senhas antes, 0 depois | B1 |
| D5 | Cabeçalhos de segurança em `GET /` | CSP, `nosniff` e `no-referrer` presentes; `HEAD /` → 405 (registrado como limitação) | B1 |

### E. Auditoria de higiene
| Verificação | Ferramenta | Achado | Ação |
|---|---|---|---|
| Imports e variáveis sem uso | `pyflakes` | Nenhum | — |
| Código morto | `vulture --min-confidence 60` | Só os handlers de rota (falsos positivos: o FastAPI os registra por decorator) | — |
| Ramo suspeito de código morto | Investigação manual | O `except ValueError` de `POST /tickets` é alcançável (`"\x1f"` passa no Pydantic e falha no domínio) | Mantido e coberto por teste |
| Segredos e credenciais | `grep` por padrões de chave, token, senha e chave privada nos arquivos versionados | Nenhum | — |
| Vulnerabilidades conhecidas | `pip-audit` nas versões instaladas | Nenhuma conhecida | — |
| Dependências desnecessárias | Revisão de `requirements.txt` | `pytest` e `httpx` iam para a imagem de produção | Separados em `requirements-dev.txt` |
| Arquivos gerados versionados | `git ls-files` | `test-results.xml` na raiz | Removido do Git e ignorado; evidência congelada em `docs/evidencias/` |
| Contexto do Docker | Revisão | Sem `.dockerignore` (risco de copiar `__pycache__`) | `.dockerignore` criado |
| Execução como root | Revisão do `Dockerfile` | Container rodava como root | Usuário `atendeja` (UID 10001) |
| Dados pessoais | Revisão | Testes e evidências usam nomes fictícios | — |

Ferramentas de auditoria (pyflakes, vulture, pip-audit, actionlint) foram usadas num ambiente separado e **não** foram adicionadas ao projeto.

## O que NÃO foi verificado
- **GitHub Actions real:** o workflow foi validado com `actionlint` e simulado localmente, mas não rodou no GitHub, porque o repositório não tem remoto configurado neste ambiente.
- **Windows/macOS:** as instruções do README para PowerShell não foram executadas.
- **Usabilidade e acessibilidade com pessoas**, leitores de tela e auditoria WCAG formal.
- **Carga e desempenho** além do cenário de 72 chamadas concorrentes.
- **Segurança:** não houve teste de intrusão; a auditoria foi estática e de dependências.
- **Conformidade legal** da regra de prioridade (RN08).
- **Revisão humana** do código, do PR e da release.

## Observações e riscos remanescentes
1. Aviso `StarletteDeprecationWarning` em todas as execuções: o `TestClient` do Starlette 1.10 indica que o suporte a `httpx` será substituído. Como as dependências são declaradas por faixa, uma versão futura do Starlette pode quebrar os testes. Recomendação para decisão humana: fixar versões (arquivo de constraints) para a release.
2. Nomes invisíveis ou com caractere de controle são aceitos (SDD, limitação 5).
3. `HEAD /` → 405.

## Checklist de homologação humana
Itens a marcar **pela pessoa responsável**; nenhum foi marcado pelo agente.

- [ ] Ler o diff do PR `feature/entrega-final` → `develop` (inclui os commits da v1.1, ainda não revisados)
- [ ] Rodar localmente `python -m pip install -r requirements-dev.txt` e `python -m pytest --cov`: esperado 57 passed e 100%
- [ ] Rodar `docker compose run --build --rm tests` e `docker compose up --build api` no próprio computador
- [ ] Com a API no ar e a fila vazia, rodar `python scripts/homologacao.py`: esperado 8/8
- [ ] Abrir http://127.0.0.1:8000/ e repetir manualmente E02–E10 (cadastrar, chamar, concluir, fila vazia)
- [ ] Testar o painel num celular real e com navegação por teclado
- [ ] Confirmar o CI verde no GitHub Actions e baixar os artefatos `teste-junit` e `cobertura`
- [ ] Decidir sobre as mudanças observáveis de erro (SDD §6)
- [ ] Decidir sobre a prioridade estrita (RN08), nomes invisíveis (limitação 5) e fixação de versões (risco 1)
- [ ] Aprovar o PR e fazer o merge em `develop`, depois em `main`
- [ ] Autorizar a criação da tag `v1.0.0` e a publicação da release ([RELEASE-v1.0.0.md](RELEASE-v1.0.0.md))

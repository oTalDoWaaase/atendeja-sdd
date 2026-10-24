# Registro de decisões de arquitetura (ADRs)

## ADR-001 API FastAPI e regras isoladas
Status: aceita. API HTTP com OpenAPI automática; regras ficam em classe QueueService para possibilitar testes unitários independentes. Trade-off: mais duas camadas num projeto pequeno.

## ADR-002 Persistência em memória para MVP
Status: aceita somente para protótipo acadêmico. Reduz complexidade de configuração e permite harness rápido. Risco conhecido: dados perdidos em reinício e inadequação a múltiplos workers.

## ADR-003 Prioridade preferencial estrita e FIFO
Status: aceita para cenário didático especificado no SDD. Consequência: senhas normais podem sofrer espera indefinida quando a demanda preferencial for alta. Evolução recomendada: política de justiça de fila com parametrização e validação legal.

## ADR-004 Testes locais + CI
Status: aceita. pytest cobre lógica, bordas e contratos REST. GitHub Actions valida cada push/PR. Revisão humana continua necessária; testes não substituem auditoria.

## Evolução de especificação
- Versão inicial: apenas fila FIFO.
- Versão atual: regra de prioridade e validação de transição de estados, explicitadas no SDD para evitar ambiguidades.
- Nota: este é um registro de decisão da construção da versão atual, não um histórico verificado de reuniões anteriores.

## ADR-005 Painel web estático servido pelo FastAPI (v1.1)
Status: aceita tecnicamente neste refinamento; **homologação humana pendente**. HTML, CSS e JavaScript puros em `app/static/`, servidos pela mesma aplicação (`/` e `/static`). Motivos: nenhuma dependência nova, nenhuma etapa de build, mesma origem (sem CORS) e mesmo container Docker. O painel consome somente a API pública, de modo que os contratos continuam sendo a única interface das regras. Trade-off: sem framework de componentes nem teste de navegador no CI; a interface é coberta por testes HTTP e por um roteiro ponta a ponta manual. Atualização por polling a cada 5 s (pausada com a aba oculta), mais simples que WebSocket e suficiente para o volume previsto.

## ADR-006 Lock de processo em QueueService (v1.1)
Status: aceita. O FastAPI executa endpoints `def` num pool de threads; sem sincronização, duas requisições simultâneas a `POST /tickets/next` podiam chamar a mesma senha e `POST /tickets` podia repetir ids (reproduzido; ver REFINAMENTOS R1). Um `threading.Lock` torna cada operação atômica. Limite: protege apenas um processo; múltiplos workers exigiriam armazenamento compartilhado com transações (fora do escopo, ver ADR-002).

## ADR-007 Normalizar o nome antes de validar o tamanho (v1.1)
Status: aceita. A API validava 1–80 caracteres sobre o texto bruto, e o domínio validava após `strip()`. Agora o modelo de entrada usa `StringConstraints(strip_whitespace=True, min_length=1, max_length=80)`, alinhado ao domínio, que mantém sua própria validação como defesa. Consequência: o `detail` do 422 para nome em branco passa a ser a lista padrão do FastAPI; o código 422 do contrato é preservado.

## ADR-008 Ordem de chamada exposta por GET /queue (v1.1)
Status: aceita. Em vez de o painel reordenar a lista em JavaScript (duplicando a regra de prioridade), o domínio expõe `waiting_queue()`, que usa a mesma função de ordenação de `call_next()`. Rota nova e somente de leitura; nenhum contrato existente foi alterado. Um teste garante que a sequência de `call_next()` é idêntica a `waiting_queue()`.

## ADR-009 Dependências separadas e Docker em estágios (1.0.0)
Status: aceita tecnicamente; **homologação humana pendente**. `requirements.txt` passa a conter só o necessário para executar (fastapi, uvicorn, pydantic); `requirements-dev.txt` inclui o anterior e acrescenta pytest, pytest-cov e httpx. O `Dockerfile` tem o estágio `runtime` (usuário não-root `atendeja`, sem ferramentas de teste) e o estágio `test` (estende o `runtime`). O `docker-compose.yml` aponta `api` para `runtime` e `tests` para `test`. Motivo: menor superfície de ataque e higiene da imagem de produção. Consequências: o CI e o README instalam `requirements-dev.txt`; na imagem de testes, `COVERAGE_FILE=/tmp/.coverage`, porque `/app` não é gravável pelo usuário não-root (falha encontrada na homologação, D1).

## ADR-010 Cobertura com pytest-cov e limite mínimo de 95% (1.0.0)
Status: aceita. A configuração fica em `pyproject.toml` (`source = app`, cobertura de ramos, `fail_under = 95`), para que terminal, Docker e CI usem as mesmas regras com `pytest --cov`. O limite fica abaixo dos 100% medidos para não punir refatorações pequenas, mas impede regressões grandes. Limite: o JavaScript do painel não é medido.

## ADR-011 Versionamento semântico, release 1.0.0 (1.0.0)
Status: proposta; **depende de autorização humana para publicar**. "v1.0" e "v1.1" eram versões do documento SDD. A primeira release estável usa SemVer `1.0.0`, definida em `app/__init__.py` e exposta em `/openapi.json` (verificado por teste). A tag `v1.0.0` só será criada depois do checklist de homologação.

## ADR-012 Relatórios gerados fora do Git; evidência congelada em docs/evidencias (1.0.0)
Status: aceita. `test-results.xml`, `coverage.xml`, `.coverage` e `htmlcov/` são ignorados na raiz, pois são gerados a cada execução e publicados como artefatos do CI. Para a avaliação acadêmica, a execução de homologação de 24/10/2026 fica congelada em `docs/evidencias/` (saídas de terminal, JUnit, `coverage.xml`, versões instaladas). O HTML de cobertura não é versionado por ser volumoso e reproduzível.

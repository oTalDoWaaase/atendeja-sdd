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

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

# SDD — AtendeJá v1.1

> Histórico: v1.0 (Entrega 2) — API REST. v1.1 (este refinamento) — interface web, rota `GET /queue`, correções de concorrência e validação. Detalhes em [REFINAMENTOS.md](REFINAMENTOS.md).

## Problema e solução
Pequenos estabelecimentos precisam organizar senhas de atendimento com prioridades, rastreamento de estado e ordenação previsível. O AtendeJá expõe uma API REST de gestão de fila e um painel web servido pela própria aplicação, sem exigir serviço externo.

## Atores
Atendente que cadastra clientes e chama a próxima senha. Operador que conclui atendimentos. Ambos podem usar o painel web (`/`) ou a API diretamente.

## Requisitos funcionais
- RF01 Criar senha informando nome de 1–80 caracteres e prioridade normal/preferencial. Espaços nas bordas são removidos **antes** de validar o tamanho (v1.1: regra aplicada igualmente na API e no domínio).
- RF02 Listar senhas, opcionalmente filtradas por estado.
- RF03 Consultar uma senha por identificador.
- RF04 Chamar a próxima senha respeitando preferencial antes de normal e FIFO dentro da mesma prioridade. Cada senha em espera é chamada no máximo uma vez, mesmo com requisições simultâneas (v1.1).
- RF05 Concluir apenas senhas no estado chamado.
- RF06 Oferecer verificação de disponibilidade /health.
- RF07 (v1.1) Consultar a fila de espera na ordem exata em que será chamada (`GET /queue`). A ordenação é a mesma função usada por RF04, para que painel e regra nunca divirjam.
- RF08 (v1.1) Painel web responsivo para: cadastrar senha, visualizar a fila em ordem de chamada e a próxima senha, chamar o próximo, listar atendimentos em andamento e concluí-los, e ver os concluídos recentes.

## Requisitos não funcionais
- RNF01 API documentada automaticamente em /docs.
- RNF02 Componentes de regra separados do framework HTTP.
- RNF03 Reprodutibilidade por Python/requirements e Docker.
- RNF04 Suíte pytest e CI com resultado JUnit.
- RNF05 Sem armazenar dados sensíveis reais neste protótipo.
- RNF06 (v1.1) Operações de fila atômicas dentro de um processo (lock em `QueueService`), pois o FastAPI executa endpoints síncronos em várias threads.
- RNF07 (v1.1) Painel sem dependências de build nem CDN: HTML, CSS e JavaScript estáticos servidos pela aplicação. Funciona de 320 px a desktop, respeita modo escuro e `prefers-reduced-motion`.
- RNF08 (v1.1) Segurança mínima do painel: nomes renderizados apenas como texto (`textContent`, nunca `innerHTML`); a página `/` envia `Content-Security-Policy: default-src 'self'`, `X-Content-Type-Options: nosniff` e `Referrer-Policy: no-referrer`.

## Contratos
Contratos v1.0 preservados sem alteração de rota, método, código de status ou campos de resposta:
- POST /tickets: {"name":"Ana","priority":"normal"} -> 201 objeto senha; 422 entrada inválida.
- GET /tickets?status=esperando -> 200 lista.
- GET /tickets/{id} -> 200 objeto; 404 inexistente.
- POST /tickets/next -> 200 senha chamada; 409 fila vazia.
- POST /tickets/{id}/finish -> 200 concluída; 404 inexistente; 409 transição inválida.
- GET /health -> 200 {"status":"ok"}.

Objeto senha: `{"id": int, "name": str, "priority": "normal"|"preferencial", "status": "esperando"|"chamado"|"concluido", "created_at": ISO-8601 UTC}`.

Acréscimos v1.1 (somente adições):
- GET /queue -> 200 lista de senhas `esperando`, ordenada como RF04.
- GET / -> 200 painel HTML (fora do esquema OpenAPI). GET /static/{arquivo} -> CSS/JS do painel; 404 inexistente.

Mudanças observáveis em erros (status preservados):
- 404 de `GET /tickets/{id}` e `POST /tickets/{id}/finish`: `detail` passou de `"'Senha não encontrada.'"` (aspas extras, defeito) para `"Senha não encontrada."`.
- 422 por nome em branco: `detail` passou a ser a lista de validação padrão do FastAPI (antes: texto do domínio). O código 422 é o contrato; o formato do `detail` não era especificado.
- Nome com espaços nas bordas e até 80 caracteres úteis: antes 422 (defeito), agora 201.

## Modelo de estado
esperando -> chamado -> concluido. Não há regressão de estado nem cancelamento.

## Decomposição
- `app/domain.py`: entidades, transições, ordem de chamada (`_call_order`, `waiting_queue`, `call_next`) e lock de concorrência.
- `app/main.py`: modelos de entrada/saída, HTTP, tratamento de erros, rota do painel e cabeçalhos de segurança.
- `app/static/`: painel web (`index.html`, `styles.css`, `app.js`), que consome apenas a API pública na mesma origem e se atualiza a cada 5 s com a aba visível.
- `tests/`: testes de domínio (incluindo concorrência) e integração HTTP (incluindo painel e contratos).
- A instância da fila pertence à aplicação criada por `create_app()`.

## Limitações e mudanças candidatas
- Persistência volátil: reiniciar o processo apaga a fila. O lock só vale dentro de **um** processo; com vários workers (`uvicorn --workers N`), cada um teria uma fila diferente. Execute com um único worker.
- Sem autenticação, autorização, rate limiting, CSRF ou trilha de auditoria: qualquer pessoa que alcance a porta pode criar, chamar e concluir senhas. Não expor fora de rede controlada.
- Sem política de dados pessoais (LGPD): nomes ficam em memória e aparecem no painel. Usar apenas dados fictícios.
- Prioridade preferencial estrita pode causar starvation dos normais (ADR-003; comportamento fixado pelo teste `test_strict_priority_keeps_normal_waiting`).
- O contrato não registra horário de chamada/conclusão; por isso o painel lista concluídos por número de senha, não por horário de conclusão.
- O painel é validado por testes HTTP no CI e por um roteiro ponta a ponta executado manualmente (ver [TESTES.md](TESTES.md)); não há teste automatizado de navegador no CI.

## Decisões que exigem homologação humana
1. Aceitar as mudanças observáveis em mensagens de erro listadas em "Contratos".
2. Manter ou substituir a prioridade preferencial estrita (exige análise legal, ex.: Lei nº 10.048/2000, e de equidade).
3. Validar usabilidade e acessibilidade do painel com usuários reais (não realizado).
4. Definir autenticação, persistência e política de dados antes de qualquer uso fora do ambiente acadêmico.

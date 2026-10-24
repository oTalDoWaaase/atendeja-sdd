# SDD — AtendeJá v1.0

## Problema e solução
Pequenos estabelecimentos precisam organizar senhas de atendimento com prioridades, rastreamento de estado e ordenação previsível. O AtendeJá expõe API REST de gestão de fila, sem exigir serviço externo.

## Atores
Atendente que cadastra clientes e chama a próxima senha. Operador que conclui atendimentos.

## Requisitos funcionais
- RF01 Criar senha informando nome de 1–80 caracteres e prioridade normal/preferencial.
- RF02 Listar senhas, opcionalmente filtradas por estado.
- RF03 Consultar uma senha por identificador.
- RF04 Chamar a próxima senha respeitando preferencial antes de normal e FIFO dentro da mesma prioridade.
- RF05 Concluir apenas senhas no estado chamado.
- RF06 Oferecer verificação de disponibilidade /health.

## Requisitos não funcionais
- RNF01 API documentada automaticamente em /docs.
- RNF02 Componentes de regra separados do framework HTTP.
- RNF03 Reprodutibilidade por Python/requirements e Docker.
- RNF04 Suíte pytest e CI com resultado JUnit.
- RNF05 Sem armazenar dados sensíveis reais neste protótipo.

## Contratos
- POST /tickets: {"name":"Ana","priority":"normal"} -> 201 objeto senha; 422 entrada inválida.
- GET /tickets?status=esperando -> 200 lista.
- GET /tickets/{id} -> 200 objeto; 404 inexistente.
- POST /tickets/next -> 200 senha chamada; 409 fila vazia.
- POST /tickets/{id}/finish -> 200 concluída; 404 inexistente; 409 transição inválida.
- GET /health -> 200 {"status":"ok"}.

## Modelo de estado
esperando -> chamado -> concluido. Não há regressão de estado.

## Decomposição
`app/domain.py`: entidades, transições e seleção da fila. `app/main.py`: modelos de entrada/saída, HTTP e tratamento de erros. `tests/`: testes de domínio e integração HTTP. A instância da fila pertence à aplicação criada por `create_app()`.

## Limitações e mudanças candidatas
Persistência é volátil; reiniciar o processo apaga filas. Não há autenticação, rate limiting, interface web, ou políticas de dados pessoais prontas para produção. Antes de publicar em produção: implementar autenticação, persistência e regras legais de atendimento preferencial; o algoritmo atual prioriza todos os preferenciais estritamente e pode causar starvation dos normais.

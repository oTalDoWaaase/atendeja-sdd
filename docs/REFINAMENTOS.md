# Registro de refinamentos — v1.0 → v1.1

Refinamento feito na branch `feature/interface-web-e-refinamentos`, a partir do código da Entrega 2, com o apoio do Claude Code (agente de IA). Cada defeito abaixo foi **reproduzido antes da correção** e recebeu teste de regressão. Os quatro testes de regressão foram executados contra o código original da `main` e **falharam** (4 failed), e passam no código corrigido. Nenhuma revisão humana foi realizada até aqui: ver "Pendências de homologação".

| # | Tipo | Problema encontrado | Evidência antes da correção | Correção | Teste de regressão |
|---|------|---------------------|-----------------------------|----------|--------------------|
| R1 | Erro lógico (concorrência) | Endpoints síncronos rodam em várias threads; `call_next()` lia a fila e mudava o estado sem sincronização, então a mesma senha podia ser chamada por dois atendentes. `create()` também podia repetir ids. | Script com 16 threads × 30 rodadas: 2745 chamadas duplicadas. Com o lock: 0. | `threading.Lock` em todas as operações de `QueueService` (ADR-006). | `test_concurrent_call_next_never_repeats_ticket`, `test_concurrent_create_unique_ids` |
| R2 | Caso de borda (validação) | API rejeitava com 422 o nome `"  " + 80 caracteres + "  "`, que o domínio aceitaria após `strip()`. As duas camadas divergiam da regra RF01. | `POST /tickets` → 422 `string_too_long`. | Remoção de espaços antes de validar, no modelo Pydantic (ADR-007). | `test_name_padded_to_max_length_accepted`, `test_name_too_long_after_trim` |
| R3 | Defeito de mensagem | `str(KeyError(msg))` devolve a mensagem entre aspas; os 404 respondiam `"'Senha não encontrada.'"`. | `GET /tickets/99` → `{"detail": "'Senha não encontrada.'"}`. | Uso de `error.args[0]`. | `test_not_found_detail_message` |
| R4 | Lacuna funcional | Não havia interface web (limitação declarada no SDD v1.0) nem forma de consultar a ordem de chamada sem duplicar a regra no cliente. | — | Painel em `app/static/` (ADR-005) e `GET /queue` (ADR-008). | `test_queue_*`, `test_web_interface_*`, `test_static_*`, `test_waiting_queue_*` |
| R5 | Comportamento caracterizado (não alterado) | Prioridade estrita pode deixar uma senha normal esperando indefinidamente (ADR-003). Mudar exige decisão humana e análise legal. | — | Nenhuma: regra preservada. | `test_strict_priority_keeps_normal_waiting` fixa o comportamento atual |

## Outras verificações adicionadas
- Contratos v1.0 preservados: `test_original_contract_routes_preserved` (rotas e métodos no OpenAPI) e `test_ticket_output_fields` (campos da resposta).
- Mensagens de 409 fixadas (`test_next_empty_detail`, `test_finish_waiting_conflict_detail`), nome ausente (`test_missing_name`), `finish` de senha inexistente no domínio, nome com exatamente 80 caracteres.
- Segurança do painel: cabeçalhos CSP/nosniff em `/` e verificação estática de que `app.js` não usa `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` nem `eval`.

## Erro cometido pela IA durante o refinamento
Na primeira versão de `waiting_queue()`, a anotação `-> list[Ticket]` falhou ao importar (`TypeError: 'function' object is not subscriptable`), porque dentro da classe o nome `list` já se refere ao método `QueueService.list`. O erro só apareceu ao executar o código e foi corrigido com `from __future__ import annotations`. O episódio está registrado como exemplo de que código gerado precisa ser executado e testado, não apenas lido.

## Pendências de homologação humana
1. Revisar o diff e aprovar o Pull Request (nenhuma revisão humana ocorreu até o momento).
2. Aceitar as mudanças observáveis nas mensagens de erro (SDD, seção "Contratos").
3. Avaliar o painel com usuários reais (usabilidade e acessibilidade com leitor de tela não foram testadas).
4. Decidir sobre a política de prioridade (R5) com base legal.
5. Confirmar a execução do CI no GitHub Actions após publicar a branch (não verificado neste ambiente).

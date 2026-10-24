# Evidências de testes

Comando: `python -m pytest -q --junitxml=test-results.xml`

Execução local de referência em 24/10/2026: **29 passed in 0.60s** (29/29 aprovados). Evidência reproduzível: arquivo `test-results.xml` e suíte versionada.

Testes cobrem casos normais e de borda, validação de nomes, erros HTTP, fila vazia, prioridade, FIFO, isolamento e estados.

## Limitações da evidência
O resultado é de execução no ambiente de preparação, não comprova execução no GitHub Actions ou computador do aluno. Não foi medida cobertura de linhas/branches. Repetir localmente e conferir o CI após publicação.

## Refinamento / erros lógicos
A especificação atual estabelece prioridade preferencial antes de normal e FIFO por categoria. A validação impede finalizar senha ainda em espera ou já concluída. Não foi documentado um erro histórico de produção nem um ciclo de review por terceiros, pois não ocorreram.

# Instruções para agentes de IA
- Leia docs/SDD.md antes de alterar código.
- Preserve as regras de prioridade preferencial e FIFO na mesma classe.
- Nunca afirme que testes passaram sem executar `python -m pytest -v`.
- Teste casos de borda, erros HTTP e isolamento entre testes.
- Não introduza autenticação falsa ou persistência sem documentar impacto e testes.
- Não exponha credenciais, dados pessoais reais ou segredos no repositório.
- Crie branches feature/*, Pull Requests e revisão humana antes do merge.
- Atualize docs/DECISOES.md e docs/TESTES.md com decisões e evidências verificáveis.

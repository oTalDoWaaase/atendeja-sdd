# Análise técnico-ética de IA

## Escopo e método
Projeto criado com assistência de ChatGPT para geração inicial de código, testes e documentação. Não se afirma que ferramentas não utilizadas tenham sido testadas. Comparação abaixo é qualitativa, baseada no tipo de fluxo oferecido pelas ferramentas, e não em benchmark deste projeto.

| Ferramenta | Potencial ponto forte | Limitação / risco | Uso neste projeto |
|---|---|---|---|
| ChatGPT | Decomposição de requisitos, geração e análise de casos de teste | Pode gerar código incompleto e conclusões excessivamente confiantes | Geração inicial assistida |
| Codex | Edição orientada a repositório, execução e iteração sobre testes | Alterações amplas ou destrutivas sem revisão cuidadosa | Opcional: registrar somente se usado |
| Claude Code | Exploração de base de código, edição e revisão iterativa | Pode consumir contexto, errar dependências e suposições | Não utilizado nesta versão inicial |
| Cursor | Edição contextual dentro da IDE | Sugestões locais incorretas e dependência de configurações | Não utilizado nesta versão inicial |

## Segurança, privacidade e governança
- Alucinação: IA pode sugerir rota ou comportamento não previsto no SDD. Mitigação: contratos explícitos + testes automatizados + verificação manual.
- Código inseguro: faltam autenticação, controles de acesso e persistência segura; não expor API a usuários reais antes de corrigi-los.
- Exposição de dados: não enviar nomes reais, credenciais nem informação sensível a prompts públicos. Usar dados fictícios nos testes.
- Propriedade intelectual: conferir licenças de dependências e originalidade de material gerado. Revisar trechos antes de distribuição.
- Homologação humana: a responsabilidade final por código, testes, requisitos e decisões permanece com o desenvolvedor.
- Viés e equidade: prioridade preferencial estrita pode prejudicar fila normal; estudar conformidade com regras de atendimento, acessibilidade e starvation.

## Aprendizados e limites
O maior ganho do apoio de IA foi acelerar o primeiro ciclo SDD -> código -> testes. O maior risco foi confundir código gerado com código validado. O CI serve como evidência repetível, mas não demonstra ausência de vulnerabilidades nem satisfação integral dos usuários. Toda conclusão deve estar vinculada ao log real de execução.

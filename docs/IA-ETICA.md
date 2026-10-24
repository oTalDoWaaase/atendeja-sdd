# Análise técnico-ética de IA

## Escopo e método
Projeto criado com assistência de ChatGPT para geração inicial de código, testes e documentação (v1.0). O refinamento v1.1 (painel web, correções e documentação) foi feito com o Claude Code, agente que lê o repositório, executa comandos e edita arquivos. Não se afirma que ferramentas não utilizadas tenham sido testadas. Comparação abaixo é qualitativa, baseada no tipo de fluxo oferecido pelas ferramentas, e não em benchmark deste projeto.

| Ferramenta | Potencial ponto forte | Limitação / risco | Uso neste projeto |
|---|---|---|---|
| ChatGPT | Decomposição de requisitos, geração e análise de casos de teste | Pode gerar código incompleto e conclusões excessivamente confiantes | Geração inicial assistida |
| Codex | Edição orientada a repositório, execução e iteração sobre testes | Alterações amplas ou destrutivas sem revisão cuidadosa | Opcional: registrar somente se usado |
| Claude Code | Exploração de base de código, edição e revisão iterativa | Pode consumir contexto, errar dependências e suposições | Não usado na v1.0; usado no refinamento v1.1 (ver seção abaixo) |
| Cursor | Edição contextual dentro da IDE | Sugestões locais incorretas e dependência de configurações | Não utilizado nesta versão inicial |

## Segurança, privacidade e governança
- Alucinação: IA pode sugerir rota ou comportamento não previsto no SDD. Mitigação: contratos explícitos + testes automatizados + verificação manual.
- Código inseguro: faltam autenticação, controles de acesso e persistência segura; não expor API a usuários reais antes de corrigi-los.
- Exposição de dados: não enviar nomes reais, credenciais nem informação sensível a prompts públicos. Usar dados fictícios nos testes.
- Propriedade intelectual: conferir licenças de dependências e originalidade de material gerado. Revisar trechos antes de distribuição.
- Homologação humana: a responsabilidade final por código, testes, requisitos e decisões permanece com o desenvolvedor.
- Viés e equidade: prioridade preferencial estrita pode prejudicar fila normal; estudar conformidade com regras de atendimento, acessibilidade e starvation.

## Análise crítica do uso de IA no refinamento v1.1
O que funcionou, verificado por execução:
- Encontrar defeitos que a suíte v1.0 não cobria: corrida em `call_next` (2745 chamadas duplicadas num script de estresse), divergência na validação do nome entre API e domínio, e aspas extras nos 404. Cada um foi reproduzido antes da correção, e o teste de regressão falhou contra o código original.
- Gerar o painel sem dependências novas e conferi-lo num navegador real (roteiro em TESTES.md).

Onde a IA errou ou exige cautela:
- Introduziu um erro de importação (`list[Ticket]` sombreado pelo método `list`), percebido apenas ao executar o código. Ler código gerado não basta.
- Um agente com permissão de executar comandos pode alterar muitos arquivos de uma vez. Mitigação adotada: branch `feature/*` separada, commits pequenos, contratos fixados por testes e diff para revisão humana.
- Testes escritos pelo mesmo agente que escreveu o código podem compartilhar os mesmos pontos cegos. Por isso a revisão humana do PR não é dispensável.
- Os testes de concorrência dependem de forçar trocas de thread; dão boa evidência, mas não provam ausência de corrida.

O que a IA **não** fez e não deve ser declarado como feito: revisão humana, aprovação de PR, execução no GitHub Actions, execução em Docker (daemon indisponível), testes com usuários, análise jurídica da prioridade.

## Limites de segurança vigentes (v1.1)
| Controle | Situação |
|---|---|
| Autenticação/autorização | Ausente: qualquer cliente da rede pode criar, chamar e concluir senhas |
| Rate limiting / proteção contra abuso | Ausente |
| CSRF | Ausente (sem sessão/cookies; relevante assim que houver autenticação) |
| XSS no painel | Mitigado: renderização via `textContent`, CSP `default-src 'self'` em `/`, teste estático contra `innerHTML` |
| Persistência e auditoria | Ausentes: dados em memória, sem trilha de quem chamou/concluiu |
| Dados pessoais | Nomes em memória e na tela; sem política de retenção. Usar apenas dados fictícios |
| Escala | Lock válido para um processo; não usar múltiplos workers |

## Aprendizados e limites
O maior ganho do apoio de IA foi acelerar o primeiro ciclo SDD -> código -> testes. O maior risco foi confundir código gerado com código validado. O CI serve como evidência repetível, mas não demonstra ausência de vulnerabilidades nem satisfação integral dos usuários. Toda conclusão deve estar vinculada ao log real de execução.

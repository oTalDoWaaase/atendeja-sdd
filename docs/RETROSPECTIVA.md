# Retrospectiva — agentes de IA no desenvolvimento individual do AtendeJá

Escopo: as três entregas do projeto. Entrega 2 (API v1.0) foi feita com assistência do ChatGPT; o refinamento v1.1 e a Entrega 3 foram feitos com o Claude Code, um agente que lê o repositório, executa comandos e edita arquivos. Os fatos citados abaixo estão registrados em [REFINAMENTOS.md](REFINAMENTOS.md), [HOMOLOGACAO.md](HOMOLOGACAO.md) e no histórico do Git. As avaliações são deste projeto e não pretendem valer como comparação geral entre ferramentas.

## Linha do tempo
| Etapa | Ferramenta | Resultado verificável |
|---|---|---|
| Entrega 2 — API v1.0 | ChatGPT (geração assistida) | 29 testes; SDD, ADRs e CI iniciais |
| Refinamento v1.1 | Claude Code | Painel web, `GET /queue`, 3 defeitos corrigidos com regressão; 53 testes |
| Entrega 3 — 1.0.0 | Claude Code | Cobertura de 100%, Docker em estágios e não-root, CI com cobertura, homologação em container e sem Docker; 57 testes |

## O que funcionou
1. **Executar em vez de supor.** O agente que roda comandos encontrou defeitos que a leitura do código não mostrava: a corrida em `call_next` (2745 chamadas duplicadas num script de estresse), as aspas extras no 404 e, nesta entrega, a falha de permissão do `.coverage` no container não-root. Esta última só apareceu porque o Docker foi de fato executado.
2. **Regressão antes da correção.** Reproduzir o defeito e confirmar que o teste falha no código antigo (4 falhas contra a `main`) deu evidência concreta, em vez de "agora parece certo".
3. **A cobertura apontou uma suposição errada.** As linhas 52–53 de `app/main.py` pareciam código morto. A investigação mostrou que são alcançáveis (`"\x1f"`), e isso virou teste em vez de remoção.
4. **Documentação ligada ao código.** O SDD As-Built cita, para cada regra, a função e os testes, e cada nome de teste citado foi conferido automaticamente.
5. **Velocidade.** Painel, testes, Docker, CI e documentação couberam em poucas sessões de trabalho individual.

## O que deu errado ou exigiu correção
| Situação | Causa | Como foi percebido |
|---|---|---|
| `list[Ticket]` quebrou a importação (v1.1) | O método `QueueService.list` sombreava o tipo `list` | Execução do código |
| Lacuna visual entre os painéis do desktop (v1.1) | Grade CSS com a barra lateral ocupando 3 linhas | Captura de tela, não teste |
| `.coverage` sem permissão no container (Entrega 3) | O usuário não-root, que acabara de ser adicionado, não escrevia em `/app` | `docker compose run tests` |
| `curl -I /` → 405 | `HEAD` não é aceito por rotas `GET` do FastAPI | Execução; registrado como limitação |
| `pkill -f` encerrou o próprio shell do agente | O padrão coincidia com a própria linha de comando | Erro operacional do agente, sem impacto no código |

Lição: código gerado e afirmações do próprio agente precisam ser confirmados por execução. Cada erro acima teria passado despercebido numa revisão apenas textual.

## Limitações do uso de agentes
- **Mesmo autor para código e testes.** Os testes escritos pelo agente podem ter os mesmos pontos cegos do código que ele escreveu. A cobertura de 100% mede linhas executadas, não a adequação das asserções.
- **Ambiente diferente do usuário.** As validações rodaram num container Linux de nuvem com proxy TLS, o que exigiu um ajuste local na imagem base. Nada foi executado em Windows nem no GitHub Actions.
- **Decisões que não cabem ao agente:** prioridade legal (RN08), aceitar mudanças observáveis de contrato, política de dados pessoais, publicação da release. O agente registrou essas decisões, mas não as tomou.
- **Risco de alteração ampla.** Um agente com permissão de escrita mexe em muitos arquivos de uma vez. Mitigações usadas: branches `feature/*`, commits temáticos, contratos fixados por teste e PR para revisão.
- **Contexto e memória.** O agente não acessou o cofre de notas pessoal do autor (fora do container), então decisões anteriores só valem se estiverem no repositório. Isso reforçou a importância de ADRs e registros versionados.
- **Avaliação subjetiva.** Qualidade visual e usabilidade do painel foram julgadas por capturas de tela e roteiro automatizado, não por pessoas.

## Benefícios para o desenvolvimento individual
- Funciona como um "segundo par de olhos" que executa: encontra casos de borda e falhas de ambiente que um desenvolvedor sozinho tende a não testar.
- Reduz o custo de tarefas de disciplina, como testes de regressão, ADRs, evidências e checklists, que costumam ser sacrificadas em projetos individuais.
- Gera artefatos auditáveis (logs de execução, relatórios de cobertura, JUnit) que tornam as afirmações verificáveis por terceiros.

## O que eu faria diferente
1. Exigir, desde a Entrega 2, que toda afirmação de "teste passou" venha com o log anexado.
2. Configurar cobertura e Docker não-root no início, não no fim.
3. Fixar versões das dependências antes da primeira release (ver risco 1 em HOMOLOGACAO).
4. Pedir revisão de uma pessoa (colega ou orientador) em pelo menos um PR, já que o projeto é individual.
5. Incluir um teste de navegador no CI, se o custo de adicionar Node/Playwright for aceito.

## Responsabilidade
A autoria e a responsabilidade final sobre código, testes, decisões e publicação são do desenvolvedor. O agente produziu e verificou artefatos, mas **não aprovou nada**: a aprovação do PR e da release está pendente no [checklist de homologação](HOMOLOGACAO.md#checklist-de-homologação-humana).

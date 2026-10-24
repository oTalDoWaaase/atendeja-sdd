# AtendeJá v1.0.0 — rascunho das notas de release

> **Rascunho. Não publicado.** A tag `v1.0.0` e a release no GitHub só devem ser criadas após a aprovação humana do [checklist de homologação](HOMOLOGACAO.md#checklist-de-homologação-humana).

Primeira versão estável do AtendeJá: API REST e painel web para gerenciar senhas de atendimento com prioridade preferencial.

## Destaques
- **Painel web responsivo** em `/`: cadastrar senhas, ver a fila em ordem de chamada, chamar o próximo e concluir atendimentos; modo escuro e atualização automática.
- **API REST** documentada em `/docs`: `POST /tickets`, `GET /tickets`, `GET /tickets/{id}`, `POST /tickets/next`, `POST /tickets/{id}/finish`, `GET /queue`, `GET /health`.
- **Regras:** preferenciais antes de normais, FIFO dentro da mesma prioridade, estados `esperando → chamado → concluido`.
- **Consistência sob concorrência:** uma senha nunca é chamada duas vezes.

## Mudanças desde a Entrega 2 (API v1.0)
### Adicionado
- Painel web (`app/static/`) servido pela própria API, com cabeçalhos de segurança (CSP, `nosniff`, `no-referrer`).
- `GET /queue`: fila de espera na ordem exata de chamada.
- `scripts/homologacao.py`: 8 cenários de homologação contra um servidor real.
- Cobertura de testes com pytest-cov (terminal, XML e HTML) e limite mínimo de 95% no CI.
- Artefato `cobertura` no GitHub Actions e resumo da cobertura no job.

### Corrigido
- Mesma senha podia ser chamada duas vezes sob requisições simultâneas, e ids podiam se repetir.
- Nome com espaços nas bordas e até 80 caracteres úteis era rejeitado pela API.
- Mensagem do 404 vinha com aspas extras.

### Alterado
- Dependências separadas em `requirements.txt` (execução) e `requirements-dev.txt` (testes).
- `Dockerfile` em estágios (`runtime` e `test`), com usuário não-root e sem ferramentas de teste na imagem de execução; `.dockerignore` adicionado.
- `test-results.xml` deixou de ser versionado na raiz (evidência congelada em `docs/evidencias/`).

### Compatibilidade
Todas as rotas, métodos, códigos de status e campos de resposta da v1.0 foram mantidos. Mudanças observáveis apenas no texto de alguns erros (detalhes no SDD §6).

## Qualidade
- 57 testes automatizados; 100% de cobertura de linhas e ramos em `app/` (Python 3.12.3).
- Homologação: 8/8 cenários de API em Docker e sem Docker; 12/12 cenários no navegador.
- Evidências: `docs/evidencias/` e [HOMOLOGACAO.md](HOMOLOGACAO.md).

## Limitações conhecidas
- Dados em memória: reiniciar apaga a fila. Use um único worker.
- Sem autenticação, rate limiting ou política de dados pessoais. **Não use com dados reais nem exponha publicamente.**
- Prioridade estrita pode atrasar indefinidamente as senhas normais.

## Instalação
```bash
docker compose up --build api        # http://127.0.0.1:8000/
# ou, sem Docker:
python -m pip install -r requirements.txt
python -m uvicorn app.main:app
```

---
### Como publicar (somente após autorização)
```bash
git checkout main && git pull
git tag -a v1.0.0 -m "AtendeJá v1.0.0"
git push origin v1.0.0
gh release create v1.0.0 --title "AtendeJá v1.0.0" --notes-file docs/RELEASE-v1.0.0.md
```
Antes de publicar, remova deste arquivo o aviso de rascunho e esta seção.

# Laboratório 05 — GraphQL vs REST (GitHub)

## Guia de Instalação

### Pré‑requisitos

- Python 3.10+ instalado.
- Um token pessoal do GitHub (PAT) para evitar rate limiting.

### Passos

- Criar e ativar ambiente virtual:
  - macOS/Linux:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
  - Windows (PowerShell):
    - `python -m venv .venv`
    - `.venv\Scripts\Activate.ps1`
- Instalar dependência:
  - `pip install requests`
- Configurar o token do GitHub:
  - Edite `app/main.py` e defina `GITHUB_TOKEN` em `app/main.py:16` com seu PAT.
  - Não versione o token. Use um token com escopos mínimos (acesso público).

## Execução

- Rodar o experimento:
  - `python app/main.py`
- Saída:
  - Um arquivo `resultados_github_exp.csv` é gerado na raiz com colunas `Treatment`, `Latency_ms`, `Size_bytes`.

Comparação controlada entre consultas REST e GraphQL na API pública do GitHub, medindo latência (ms) e tamanho do payload (bytes) em cenários simples e complexos.

## Hipóteses

- H01: A diferença na velocidade de resposta entre GraphQL e REST é nula.
- HA1: Consultas GraphQL respondem significativamente mais rápido que REST.
- H02: A diferença no tamanho da resposta (bytes) entre GraphQL e REST é nula.
- HA2: Respostas GraphQL têm tamanho significativamente menor que REST.

## Variáveis Dependentes

- Tempo de Resposta (ms): tempo do envio até a resposta completa (RQ1).
- Tamanho da Resposta (bytes): tamanho do payload retornado (RQ2).

## Variáveis Independentes

- Tipo de API (fator): REST vs GraphQL.
- Complexidade da Consulta (subfator): Simples vs Complexa (profundidade/over‑fetching).

## Tratamentos

| Tratamento           | Tipo de API | Dados solicitados (exemplo)                        | Objetivo                                            |
| -------------------- | ----------- | -------------------------------------------------- | --------------------------------------------------- |
| T1: REST Simples     | REST        | Nome, Estrelas, Data de Criação                    | Under‑fetching forçado (REST tende a retornar mais) |
| T2: GraphQL Simples  | GraphQL     | Nome, Estrelas, Data de Criação                    | Exact‑fetching (ideal)                              |
| T3: REST Complexo    | REST        | Repo + 10 commits + 10 issues (múltiplas chamadas) | Simular under‑fetching e múltiplos round‑trips      |
| T4: GraphQL Complexo | GraphQL     | Repo + 10 commits + 10 issues (uma chamada)        | Consolidar dados em uma única requisição            |

## Objetos Experimentais

- API: GitHub Public API (REST e GraphQL).
- Repositório alvo: `facebook/react` ou `torvalds/linux` (alto volume de dados).
- Ambiente: máquina cliente com internet estável executando scripts Python.

## Tipo de Projeto Experimental

- Tipo: Quase‑Fatorial (2 fatores: Tipo de API e Complexidade).
- Delineamento: medidas repetidas (Within‑Subject). Cada tratamento medido N vezes.
- Aleatorização: ordem T1–T4 é aleatorizada por repetição para mitigar cache/rede.

## Quantidade de Medições

- Repetições: N = 50 por tratamento.
- Total: 4 tratamentos × 50 = 200 medições.

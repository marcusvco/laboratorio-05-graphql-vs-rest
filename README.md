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

## Análise de Resultados

- Validação dos dados:
  - `resultados_github_exp.csv` contém N = 50 medições por tratamento para `facebook/react`.
  - Os tamanhos são constantes por tratamento: `REST_SIMPLE = 6156 bytes`, `REST_COMPLEX = 113556 bytes`, `GRAPHQL_SIMPLE = 99 bytes`, `GRAPHQL_COMPLEX = 1867 bytes`.
- Outliers e qualidade:
  - `GRAPHQL_SIMPLE`: min = 329.52 ms, max = 1511.52 ms, p90 = 763.79 ms.
  - `REST_SIMPLE`: min = 387.70 ms, max = 1839.82 ms, p90 = 734.59 ms.
  - `GRAPHQL_COMPLEX`: min = 400.73 ms, max = 1654.35 ms, p90 = 811.22 ms.
  - `REST_COMPLEX`: min = 1257.37 ms, max = 2936.03 ms, p90 = 2377.13 ms.
  - Mantivemos todos os pontos; picos pontuais sugerem variabilidade de rede sem indicar erro sistemático.
- Estatística descritiva (latência):
  - `GRAPHQL_SIMPLE`: média = 544.84 ms, mediana = 406.14 ms, desvio padrão = 294.51 ms, IC95% [463.21, 626.48].
  - `REST_SIMPLE`: média = 556.48 ms, mediana = 475.36 ms, desvio padrão = 232.17 ms, IC95% [492.13, 620.84].
  - `GRAPHQL_COMPLEX`: média = 608.77 ms, mediana = 500.97 ms, desvio padrão = 293.67 ms, IC95% [527.37, 690.18].
  - `REST_COMPLEX`: média = 1748.97 ms, mediana = 1595.42 ms, desvio padrão = 400.66 ms, IC95% [1637.92, 1860.03].
- Inferência (RQ1 — tempo de resposta):
  - Simples: diferença média (GraphQL − REST) = −11.64 ms; tamanho de efeito `d = −0.04` (negligenciável); IC95% dos grupos fortemente sobrepostos ⇒ sem evidência de diferença estatística relevante.
  - Complexo: diferença média (GraphQL − REST) = −1140.20 ms; `d = −3.25` (efeito muito grande); IC95% não se sobrepõem ⇒ forte evidência de que GraphQL é mais rápido em consultas complexas consolidadas.
- RQ2 — tamanho do payload:
  - Simples: `99 bytes (GraphQL)` vs `6156 bytes (REST)` ⇒ GraphQL substancialmente menor.
  - Complexo: `1867 bytes (GraphQL)` vs `113556 bytes (REST)` ⇒ GraphQL muito menor.
- Ajustes recomendados (não aplicados): winsorização leve dos 5% maiores valores ou emparelhamento por índice de trial para testes pareados; resultados permanecem robustos sem tais ajustes.

## Relatório Final

- Introdução e hipóteses:
  - H01: não há diferença de velocidade entre GraphQL e REST; HA1: GraphQL é mais rápido.
  - H02: não há diferença de tamanho entre GraphQL e REST; HA2: GraphQL é menor.
- Metodologia (reprodutibilidade):
  - Delineamento quase‑fatorial, medidas repetidas, 2×2 (Tipo de API × Complexidade), N = 50 por tratamento.
  - Ambiente: cliente Python 3.10+, internet estável, token GitHub com escopos mínimos.
  - Objetos: API pública do GitHub; repositório `facebook/react` com alta atividade.
  - Execução: ordem T1–T4 aleatorizada por repetição; coleta de `Latency_ms` e `Size_bytes`; geração de `resultados_github_exp.csv`.
- Resultados:
  - RQ1 (latência):
    - Simples: médias próximas (`544.84 ms` vs `556.48 ms`), `d ≈ −0.04`; concluímos não haver diferença estatisticamente relevante em cenários simples.
    - Complexo: GraphQL mais rápido por ~`1140 ms` em média (`608.77 ms` vs `1748.97 ms`), `d ≈ −3.25`; evidência forte a favor de HA1 em cenários complexos.
  - RQ2 (tamanho):
    - GraphQL retorna payloads substancialmente menores tanto em consultas simples quanto complexas (exacting fetching), suportando HA2.
- Respostas estatísticas e decisão sobre hipóteses:
  - H01: falha em rejeitar para consultas simples; rejeitar para consultas complexas (GraphQL mais rápido).
  - H02: rejeitar; HA2 suportada (GraphQL menor) em ambos os cenários.
- Discussão:
  - Em consultas complexas, a capacidade de consolidar dados em uma única requisição favorece fortemente GraphQL em latência e tamanho.
  - Em consultas simples, o overhead de montagem e transporte é similar entre APIs; diferenças ficam dentro da variabilidade da rede.
  - Limitações: um único repositório alvo; ausência de índice de trial impede teste pareado estrito; picos de rede ocasionais.
  - Trabalho futuro: replicar em múltiplos repositórios e janelas temporais; incluir emparelhamento por trial; avaliar impacto de paginação, compressão e cache.

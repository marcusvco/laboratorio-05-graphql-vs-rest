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


## 1. Introdução

A arquitetura REST tem sido o padrão dominante para APIs Web, baseando-se em endpoints pré-definidos para manipulação de recursos. Entretanto, a emergência do GraphQL, proposto pelo Facebook, oferece uma alternativa baseada em grafos e schemas, prometendo maior flexibilidade ao cliente.

Embora muitos sistemas realizem a migração para GraphQL, nem sempre os benefícios quantitativos (desempenho e eficiência de dados) são claros em comparação a uma implementação REST bem estabelecida.

O objetivo deste experimento é avaliar quantitativamente essas diferenças através da API pública do GitHub, respondendo às seguintes perguntas de pesquisa:

* **RQ1:** Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?
* **RQ2:** Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

### Hipóteses

Para responder às perguntas de pesquisa, definimos as seguintes hipóteses nula ($H_0$) e alternativa ($H_A$):

#### RQ1 — Latência (Tempo de Resposta)
* **$H_{01}$ (Nula):** A diferença na velocidade de resposta entre GraphQL e REST é nula.
* **$H_{A1}$ (Alternativa):** Consultas GraphQL respondem significativamente mais rápido que REST.

#### RQ2 — Tamanho do Payload
* **$H_{02}$ (Nula):** A diferença no tamanho da resposta (bytes) entre GraphQL e REST é nula.
* **$H_{A2}$ (Alternativa):** Respostas GraphQL têm tamanho significativamente menor que REST.

---

## 2. Metodologia

Para garantir a reprodutibilidade e a validade dos dados, este estudo adotou um delineamento experimental controlado do tipo **Quase-Fatorial com Medidas Repetidas (Within-Subject)**.

### 2.1. Ambiente Experimental

Os *trials* foram realizados no seguinte ambiente:

* **Máquina Cliente:** Python 3.10+ com biblioteca `requests`.
* **Objeto Experimental:** API Pública do GitHub (v3 REST e v4 GraphQL).
* **Alvo dos Dados:** Repositório `facebook/react` (escolhido pelo alto volume de dados, issues e commits).
* **Rede:** Conexão de internet estável; autenticação via *GitHub Personal Access Token* (PAT).

### 2.2. Tratamentos e Variáveis

O experimento manipulou dois fatores: o **Tipo de API** (REST vs GraphQL) e a **Complexidade da Consulta** (Simples vs Complexa).

| Tratamento | Descrição | Objetivo |
| :--- | :--- | :--- |
| **T1: REST Simples** | Requisição única de metadados do repositório (Nome, Estrelas). | Simular *Under-fetching* (REST retorna excesso de dados). |
| **T2: GraphQL Simples** | Requisição única dos mesmos campos exatos. | Testar *Exact-fetching* em cenário trivial. |
| **T3: REST Complexo** | Busca de Repositório + 10 últimos commits + 10 últimas issues. | Simular cenário real com múltiplos *endpoints* (N+1 requests). |
| **T4: GraphQL Complexo** | Busca aninhada dos mesmos dados em uma única chamada. | Testar capacidade de consolidação de dados. |

### 2.3. Execução

Para mitigar a variabilidade da rede e evitar viés de cache, a ordem de execução dos tratamentos (T1 a T4) foi **aleatorizada** a cada iteração. Foram realizadas **50 medições (N=50)** para cada tratamento, totalizando 200 pontos de dados. As métricas coletadas foram:

* **Latência ($ms$):** Tempo decorrido entre o envio da requisição e o recebimento do último byte.
* **Tamanho ($bytes$):** Tamanho total do corpo da resposta (payload).

---

## 3. Resultados e Análise Estatística

Os dados brutos foram processados e validados, não sendo necessária a remoção de outliers extremos, pois a variância observada foi consistente com flutuações normais de rede.

### 3.1. RQ1: Latência (Tempo de Resposta)

A tabela abaixo resume as estatísticas descritivas para o tempo de resposta:

| Tratamento | Média (ms) | Mediana (ms) | Desvio Padrão | Intervalo Confiança (95%) |
| :--- | :--- | :--- | :--- | :--- |
| **GraphQL Simples** | 544.84 | 406.14 | 294.51 | [463.21, 626.48] |
| **REST Simples** | 556.48 | 475.36 | 232.17 | [492.13, 620.84] |
| **GraphQL Complexo** | **608.77** | **500.97** | 293.67 | [527.37, 690.18] |
| **REST Complexo** | 1748.97 | 1595.42 | 400.66 | [1637.92, 1860.03] |

**Análise Estatística:**

1.  **Cenário Simples:** A diferença média entre GraphQL e REST foi de apenas **-11.64 ms**. Os intervalos de confiança de 95% se sobrepõem quase totalmente. O tamanho de efeito (Cohen's d) foi **-0.04** (negligenciável).
    * *Conclusão:* **Falha em rejeitar $H_{01}$** para consultas simples.

2.  **Cenário Complexo:** A diferença média foi de **-1140.20 ms**. O REST foi quase 3x mais lento. O tamanho de efeito foi **-3.25** (muito grande).
    * *Conclusão:* **Rejeita-se $H_{01}$** em favor de $H_{A1}$ para consultas complexas.

> **[Inserir aqui o Gráfico Boxplot do Dashboard: Latência por Complexidade]**
>
> *A figura acima ilustra como a distribuição de tempo do REST se degrada severamente no cenário complexo.*

### 3.2. RQ2: Tamanho do Payload

Os tamanhos das respostas foram constantes para cada tratamento, demonstrando a natureza determinística das APIs.

| Complexidade | GraphQL (bytes) | REST (bytes) | Diferença (%) |
| :--- | :--- | :--- | :--- |
| **Simples** | 99 | 6.156 | GraphQL é **~98% menor** |
| **Complexo** | 1.867 | 113.556 | GraphQL é **~98% menor** |

**Análise Estatística:**

Em ambos os cenários, o GraphQL retornou payloads substancialmente menores devido à sua capacidade de *Exact-fetching*, eliminando campos desnecessários que a API REST retorna por padrão.

* *Conclusão:* **Rejeita-se $H_{02}$** em favor de $H_{A2}$. As respostas GraphQL são estatisticamente e praticamente menores.

> **[Inserir aqui o Gráfico de Barras do Dashboard: Comparação de Tamanho em Bytes]**

---

## 4. Discussão Final

Os resultados deste experimento controlado lançam luz sobre as reais vantagens da adoção do GraphQL.

**1. O Mito da Performance Universal**
Ao contrário do que o senso comum sugere, o GraphQL **não é intrinsecamente mais rápido** que o REST para todas as situações. No cenário de consultas simples ("Simples"), a latência foi estatisticamente idêntica. Isso ocorre porque o custo dominante nessas chamadas é o *overhead* de rede (DNS, Handshake TCP/TLS), que é agnóstico à tecnologia da API.

**2. A Vantagem da Consolidação (Complexidade)**
A grande vantagem do GraphQL manifestou-se no cenário "Complexo". Enquanto a abordagem REST exigiu múltiplas chamadas sequenciais ou o recebimento de grandes volumes de dados desnecessários (*Over-fetching*), o GraphQL permitiu buscar dados relacionais (commits e issues aninhados ao repositório) em um único *round-trip*. Essa consolidação foi responsável por uma redução de latência superior a 1 segundo em média.

**3. Eficiência de Dados**
Em relação à RQ2, o GraphQL mostrou-se superior em 100% dos casos. Para dispositivos móveis ou redes limitadas, a economia de banda (redução de ~98% no tamanho do payload) é um fator crítico de sucesso.

**Conclusão Geral**
A hipótese de que o GraphQL é superior ($H_A$) confirmou-se verdadeira principalmente para cenários de alta complexidade de dados e necessidade de eficiência de banda. Para micro-consultas simples, a escolha entre REST e GraphQL deve ser baseada mais na ergonomia de desenvolvimento e manutenção do que em performance bruta de latência.

### Ameaças à Validade

* **Validade Externa:** O experimento focou em um único repositório (`facebook/react`). Diferentes estruturas de dados podem gerar resultados distintos.
* **Ambiente:** Flutuações pontuais de rede foram mitigadas pela aleatorização, mas não eliminadas.

---
## 5. Dashboard de Visualização

Este relatório é acompanhado por um Dashboard interativo (Power BI) que detalha visualmente os resultados discutidos acima, incluindo:

1.  **Boxplot de Latência:** Evidenciando a variabilidade e outliers do REST em cenários complexos.
2.  **Gráfico de Interação:** Demonstrando o aumento desproporcional do tempo de resposta do REST conforme a complexidade aumenta.
3.  **Comparativo de Tamanho:** Ilustrando a economia massiva de dados proporcionada pelo *Exact-fetching* do GraphQL.

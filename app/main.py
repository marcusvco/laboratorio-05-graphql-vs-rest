import requests
import time
import csv
import os
from random import shuffle, choice
import json

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Configurações do Experimento ---
GITHUB_OWNER = "facebook"
GITHUB_REPO = "react"
REPO_LABEL = f"{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_REST_BASE_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"
NUM_REPETITIONS = 50
OUTPUT_FILE = "resultados_github_exp.csv"

HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json",
}

# --- Consultas GraphQL ---
QUERY_GRAPHQL_SIMPLE = f"""
query SimpleRepoData {{
  repository(owner: "{GITHUB_OWNER}", name: "{GITHUB_REPO}") {{
    name
    stargazerCount
    createdAt
  }}
}}
"""

QUERY_GRAPHQL_COMPLEX = f"""
query ComplexRepoData {{
  repository(owner: "{GITHUB_OWNER}", name: "{GITHUB_REPO}") {{
    name
    stargazerCount
    createdAt
    commits: defaultBranchRef {{
      target {{
        ... on Commit {{
          history(first: 10) {{
            edges {{
              node {{
                messageHeadline
              }}
            }}
          }}
        }}
      }}
    }}
    issues(first: 10, states: [OPEN]) {{
      edges {{
        node {{
          title
        }}
      }}
    }}
  }}
}}
"""


def make_request(url, method="GET", headers=None, data=None):
    """Função auxiliar para fazer requisições e medir performance."""
    start_time = time.perf_counter()
    response = requests.request(
        method, url, headers=headers, json=data, timeout=10
    )  # Adiciona timeout
    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000
    size_bytes = len(response.content)

    if response.status_code == 403:
        print("\nERRO: Limite de taxa (Rate Limit) atingido. O token é necessário.")
        raise Exception("Rate Limit Exceeded")

    response.raise_for_status()  # Lança exceção para erros HTTP (4xx ou 5xx)
    return latency_ms, size_bytes


def run_treatment(treatment_name):
    """Executa um tratamento e retorna a latência e o tamanho."""
    if treatment_name == "REST_SIMPLE":
        # T1: REST Simples (single round-trip, over-fetching)
        return make_request(
            f"{GITHUB_REST_BASE_URL}",
            method="GET",
            headers={"Authorization": HEADERS["Authorization"]},
        )

    elif treatment_name == "GRAPHQL_SIMPLE":
        # T2: GraphQL Simples (single round-trip, exact-fetching)
        data = {"query": QUERY_GRAPHQL_SIMPLE}
        return make_request(
            GITHUB_GRAPHQL_URL, method="POST", headers=HEADERS, data=data
        )

    elif treatment_name == "REST_COMPLEX":
        # T3: REST Complexo (Multiple round-trips: Repositório + Commits + Issues)
        # Medimos o tempo TOTAL de todas as requisições em série.
        total_latency = 0
        total_size = 0

        # 1. Repositório Principal
        latency_1, size_1 = make_request(
            f"{GITHUB_REST_BASE_URL}",
            method="GET",
            headers={"Authorization": HEADERS["Authorization"]},
        )
        total_latency += latency_1
        total_size += size_1

        # 2. Commits
        latency_2, size_2 = make_request(
            f"{GITHUB_REST_BASE_URL}/commits?per_page=10",
            method="GET",
            headers={"Authorization": HEADERS["Authorization"]},
        )
        total_latency += latency_2
        total_size += size_2

        # 3. Issues
        latency_3, size_3 = make_request(
            f"{GITHUB_REST_BASE_URL}/issues?per_page=10",
            method="GET",
            headers={"Authorization": HEADERS["Authorization"]},
        )
        total_latency += latency_3
        total_size += size_3

        return total_latency, total_size

    elif treatment_name == "GRAPHQL_COMPLEX":
        # T4: GraphQL Complexo (single round-trip, exact-fetching)
        data = {"query": QUERY_GRAPHQL_COMPLEX}
        return make_request(
            GITHUB_GRAPHQL_URL, method="POST", headers=HEADERS, data=data
        )

    return 0, 0  # Fallback


def run_experiment():
    """Gerencia a execução do experimento e armazena os resultados."""
    print("--- INICIANDO EXPERIMENTO CONTROLADO (GitHub API) ---")

    # Lista de todos os 4 tratamentos a serem misturados N vezes
    all_treatments = [
        "REST_SIMPLE",
        "GRAPHQL_SIMPLE",
        "REST_COMPLEX",
        "GRAPHQL_COMPLEX",
    ]

    # 1. Preparação da lista de execuções
    execution_plan = all_treatments * NUM_REPETITIONS
    shuffle(execution_plan)  # Aleatoriza a ordem de execução

    results = []

    # 2. Fase de Warm-up
    print("Executando Warm-up (8 requisições)...")
    for _ in range(2):
        for treatment in all_treatments:
            try:
                run_treatment(treatment)
            except Exception as e:
                print(f"Aviso durante Warm-up: {e}")
                time.sleep(1)  # Espera para evitar banimento

    print("Warm-up concluído. Iniciando medições.")

    # 3. Execução das Medições
    for i, treatment in enumerate(execution_plan):
        try:
            latency, size = run_treatment(treatment)
            results.append([REPO_LABEL, treatment, latency, size])

            if (i + 1) % 20 == 0:
                print(
                    f"Progresso: {i + 1}/{len(execution_plan)} medições concluídas. Último: {treatment} ({latency:.2f}ms)"
                )

            # Pequeno delay para evitar sobrecarga ou rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"Erro na medição {i+1} ({treatment}): {e}. Pulando.")
            time.sleep(5)  # Espera mais em caso de erro

    # 4. Armazenamento dos Resultados
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Repo", "Treatment", "Latency_ms", "Size_bytes"])
        writer.writerows(results)

    print(
        f"\nExperimento concluído. Total de {len(results)} medições salvas em {OUTPUT_FILE}"
    )


# Chamada principal
if __name__ == "__main__":
    run_experiment()

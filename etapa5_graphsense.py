import requests 
import networkx as nx 
import json
import requests
import time

BASE_URL = "https://blockstream.info/api"

## API para pegar da rede bitcoin
def obterNeighbors(address, limite_transacoes):

    try:
        url = f"{BASE_URL}/address/{address}/txs"

        time.sleep(0.3)

        resposta = requests.get(
            url,
            timeout=10
        )

        if resposta.status_code != 200:
            return []

        vizinhos = []

        transacoes = resposta.json()

        transacoes = transacoes[:limite_transacoes]

        for tx in transacoes:

            # Inputs
            for vin in tx.get("vin", []):
                prev_out = vin.get("prevout")

                if (prev_out and prev_out.get("scriptpubkey_address")):
                    vizinhos.append({
                        "address": prev_out["scriptpubkey_address"],
                        "value": prev_out.get("value", 0)
                    })

            # Outputs
            for vout in tx.get("vout", []):
                if vout.get("scriptpubkey_address"):
                    vizinhos.append({
                        "address": vout["scriptpubkey_address"],
                        "value": vout.get("value", 0)
                    })
        return vizinhos
    
    except Exception as e:

        print("Erro em", address)
        print(e)

        return []

def expandirGrafo(address, profundidade, max_vizinhos, max_nos):

    G = nx.DiGraph()

    fila = [address]

    visitados = set()

    nivel = 0

    while fila and nivel < profundidade:

        proxima_fila = []

        for atual in fila:

            if atual in visitados:
                continue

            visitados.add(atual)

            vizinhos = obterNeighbors(atual, 10)

            for vizinho in vizinhos[:max_vizinhos]:

                destino = vizinho["address"]

                valor = vizinho["value"]

                G.add_edge(atual, destino, valor=valor)

                if destino not in visitados:

                    proxima_fila.append(destino)

            # Limite global
            if G.number_of_nodes() >= max_nos:

                print("Limite de nós atingido")

                return G

        fila = proxima_fila

        nivel += 1

    return G

def construirGrafoFiltrado(G, uf):

    G_filtrado = nx.DiGraph()

    for origem, destino, dados in G.edges(data=True):

        entidade_origem = uf[origem]

        entidade_destino = uf[destino]

        if entidade_origem != entidade_destino:

            valor = dados.get(
                "valor",
                0
            )

            G_filtrado.add_edge(
                entidade_origem,
                entidade_destino,
                valor=valor
            )

    return G_filtrado
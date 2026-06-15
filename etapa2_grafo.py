import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def filtrarNome(G):
    labels = {}

    for i, no in enumerate(G.nodes()):
        labels[no] = f"wallet_{i}"

    return labels

def gerarGrafoFiltrado(G_filtrado):
    
    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(
        G_filtrado,
        k=2,
        seed=42
    )

    graus = dict(G_filtrado.degree())

    cores = []
    tamanhos = []

    for no in G_filtrado.nodes():

        grau = graus[no]

        if grau >= 8:
            cores.append("red")

        elif grau >= 4:
            cores.append("orange")

        else:
            cores.append("lightgreen")

        tamanhos.append(
            500 + grau*150
        )
    
    nx.draw_networkx_nodes(
        G_filtrado,
        pos,
        node_color=cores,
        node_size=tamanhos
    )

    nx.draw_networkx_edges(
        G_filtrado,
        pos,
        arrows=True,
        arrowsize=15
    )

    labels = filtrarNome(G_filtrado)
    
    nx.draw_networkx_labels(
        G_filtrado,
        pos,
        labels=labels,
        font_size=8
    )

    plt.title(
        "Grafo Filtrado por Heurística de Multi-Input"
    )

    plt.axis("off")

    plt.tight_layout()

    plt.show()

def gerarGrafo(G, carteira_principal):

    plt.figure(figsize=(12, 8))

    pos = nx.spring_layout(
        G,
        k=1.5,
        seed=42
    )

    cores = []

    for no in G.nodes():

        if no == carteira_principal:
            cores.append("red")

        elif G.in_degree(no) >= 3:
            cores.append("orange")

        else:
            cores.append("lightblue")

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=cores,
        node_size=1000
    )

    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowsize=15
    )

    nx.draw_networkx_labels(
        G,
        pos,
        labels=filtrarNome(G),
        font_size=8
    )

    labels = nx.get_edge_attributes(
        G,
        "valor"
    )

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels,
        font_size=7
    )

    plt.title("Rede de Transações Bitcoin")

    plt.axis("off")

    plt.tight_layout()

    plt.show()

    print("Grafo gerado com sucesso!")

""""
def gerarGrafo():
    df = pd.read_csv("transacoesbtcsimples.csv")

    G = nx.from_pandas_edgelist(
        df,
        source="origem",
        target="destino",
        edge_attr="valor",
        create_using=nx.DiGraph()
    )

    plt.figure(figsize=(10,7))

    pos = nx.spring_layout(G, k=2, seed=42)

    cores = []

    for no in G.nodes():
        if no == "ransom_wallet":
            cores.append("red")
        else:
            cores.append("silver")

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=cores,
        node_size=2000
    )

    nx.draw_networkx_edges(
        G,
        pos,
        arrows=True,
        arrowsize=20
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=11
    )

    labels = nx.get_edge_attributes(G, "valor")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=labels
    )

    plt.title("Rede de Transações Bitcoin")
    plt.axis("off")
    plt.tight_layout()

    plt.show()

    plt.show()

    print("Grafo gerado com sucesso!")
"""
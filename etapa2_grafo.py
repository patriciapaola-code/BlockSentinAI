import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def filtrarNome(G):
    return {no: f"wallet_{i}" for i, no in enumerate(G.nodes())}


def filtrarNomeComScore(G, scores):
    labels = {}
    for i, no in enumerate(G.nodes()):
        score = scores.get(no, {}).get("score", 0) if scores else 0
        labels[no] = f"wallet_{i}\n{round(score, 2)}"
    return labels


def adicionarLegenda(itens):
    plt.legend(handles=itens, loc="upper right", frameon=True, title="Legenda")


def corPorRisco(score):
    if score >= 80:
        return "darkred"
    if score >= 60:
        return "red"
    if score >= 40:
        return "orange"
    if score > 0:
        return "lightgreen"
    return "lightgray"


def gerarGrafoFiltrado(
    G_filtrado,
    heuristica_nome,
    scores=None,
    caminho_destacado=None
):
    plt.figure(figsize=(14, 10))

    pos = nx.spring_layout(G_filtrado, k=1.5, seed=42)

    cores = []
    tamanhos = []

    for no in G_filtrado.nodes():
        score = scores.get(no, {}).get("score", 0) if scores else 0

        cores.append(corPorRisco(score))
        tamanhos.append(300 + score * 10)

    nx.draw_networkx_nodes(G_filtrado, pos, node_color=cores, node_size=tamanhos)

    nx.draw_networkx_edges(
        G_filtrado,
        pos,
        arrows=True,
        arrowsize=15,
        alpha=0.6
    )

    if scores:
        for no in G_filtrado.nodes():
            score = scores.get(no, {}).get("score", 0)

            if score >= 70:
                nx.draw_networkx_nodes(
                    G_filtrado,
                    pos,
                    nodelist=[no],
                    node_color="yellow",
                    node_size=1200,
                    edgecolors="black",
                    linewidths=1.5
                )

    if caminho_destacado and len(caminho_destacado) >= 2:
        arestas_caminho = list(zip(caminho_destacado, caminho_destacado[1:]))

        nx.draw_networkx_edges(
            G_filtrado,
            pos,
            edgelist=arestas_caminho,
            edge_color="blue",
            width=3,
            arrows=True,
            arrowsize=20
        )
        
        nx.draw_networkx_nodes(
            G_filtrado,
            pos,
            nodelist=caminho_destacado,
            node_color=[
                corPorRisco(scores.get(no, {}).get("score", 0)) if scores else "lightblue"
                for no in caminho_destacado
            ],
            node_size=1400,
            edgecolors="blue",
            linewidths=2.5
        )

    # 🔥 LABELS
    nx.draw_networkx_labels(
        G_filtrado,
        pos,
        labels=filtrarNomeComScore(G_filtrado, scores) if scores else filtrarNome(G_filtrado),
        font_size=8
    )

    if scores:
        adicionarLegenda([
            Patch(facecolor="darkred", label="Risco crítico (>= 80)"),
            Patch(facecolor="red", label="Risco alto (60-79)"),
            Patch(facecolor="orange", label="Risco médio (40-59)"),
            Patch(facecolor="lightgreen", label="Risco baixo (1-39)"),
            Patch(facecolor="lightgray", label="Sem evidência"),
            Line2D([0], [0], color="blue", lw=3, label="Trajetória provável")
        ])
    else:
        adicionarLegenda([
            Patch(facecolor="red", label="Carteira principal"),
            Patch(facecolor="orange", label="Nó relevante estrutural"),
            Patch(facecolor="lightblue", label="Demais carteiras"),
            Line2D([0], [0], color="black", lw=1, label="Transação")
        ])

    plt.title(f"Grafo Filtrado por Heurística: {heuristica_nome}")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def gerarGrafo(G, carteira_principal, scores=None):
    plt.figure(figsize=(12, 8))

    pos = nx.spring_layout(G, k=1.2, seed=42)

    cores = []
    tamanhos = []

    for no in G.nodes():
        score = scores.get(no, {}).get("score", 0) if scores else 0

        if scores:
            cores.append(corPorRisco(score))
            tamanhos.append(400 + score * 10)

        elif no == carteira_principal:
            cores.append("red")
            tamanhos.append(1000)

        elif G.in_degree(no) >= 3:
            cores.append("orange")
            tamanhos.append(800)

        else:
            cores.append("lightblue")
            tamanhos.append(500)

    nx.draw_networkx_nodes(G, pos, node_color=cores, node_size=tamanhos)

    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=12, alpha=0.6)

    nx.draw_networkx_labels(
        G,
        pos,
        labels=filtrarNomeComScore(G, scores) if scores else filtrarNome(G),
        font_size=8
    )

    labels = nx.get_edge_attributes(G, "valor")

    if labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=7)

    if scores:
        adicionarLegenda([
            Patch(facecolor="darkred", label="Risco crítico"),
            Patch(facecolor="red", label="Risco alto"),
            Patch(facecolor="orange", label="Risco médio"),
            Patch(facecolor="lightgreen", label="Risco baixo"),
            Patch(facecolor="lightgray", label="Sem evidência"),
            Line2D([0], [0], color="black", lw=1, label="Transação")
        ])
    else:
        adicionarLegenda([
            Patch(facecolor="red", label="Carteira principal"),
            Patch(facecolor="orange", label="Nó relevante"),
            Patch(facecolor="lightblue", label="Demais carteiras"),
            Line2D([0], [0], color="black", lw=1, label="Transação")
        ])

    plt.title("Rede de Transações Bitcoin - Grafo")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    print("Grafo gerado com sucesso!")
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config


def corPorRiscoHex(score):
    if score >= 80:
        return "#8B0000"
    if score >= 60:
        return "#FF0000"
    if score >= 40:
        return "#FFA500"
    if score > 0:
        return "#90EE90"
    return "#D3D3D3"

def formatar_btc(valor_satoshis):
    btc = valor_satoshis / 100_000_000
    return f"{btc:.3f} BTC".rstrip("0").rstrip(".")

def renderizar_grafo_interativo(
        G,
        carteira_principal=None,
        scores=None,
        caminho_destacado=None):

    # -------------------------
    # Converte MultiDiGraph sem perder dados
    # -------------------------
    if isinstance(G, nx.MultiDiGraph):
        G_simples = nx.DiGraph()

        for u, v, data in G.edges(data=True):
            if not G_simples.has_edge(u, v):
                G_simples.add_edge(u, v, **data)
            else:
                # opcional: acumula valores se quiser análise mais rica
                G_simples[u][v]["valor"] = G_simples[u][v].get("valor", 0) + data.get("valor", 0)

        G = G_simples

    # -------------------------
    # Limite de segurança visual
    # -------------------------
    MAX_NOS = 200
    MAX_ARESTAS = 1000

    if G.number_of_nodes() > MAX_NOS:
        nos = list(G.nodes())[:MAX_NOS]
        G = G.subgraph(nos).copy()

    # -------------------------
    # Mapeamento de IDs
    # -------------------------
    ids = {no: str(i) for i, no in enumerate(G.nodes())}
    nomes = {no: f"wallet_{i}" for i, no in enumerate(G.nodes())}

    nodes = []
    edges = []

    # -------------------------
    # NÓS
    # -------------------------
    for no in G.nodes():

        score = scores.get(no, {}).get("score", 0) if scores else 0

        tamanho = 35 if no == carteira_principal else 20

        nodes.append(
            Node(
                id=ids[no],
                label=nomes[no],
                title=f"{no}\nScore={round(score, 2)}",
                size=tamanho,
                color=corPorRiscoHex(score),

                font={
                    "color": "#000000",
                    "face": "arial",
                    "size": 14,
                    "strokeWidth": 4,
                    "strokeColor": "#00FF55"
                }
            )
        )

    # -------------------------
    # TRAJETÓRIA DESTACADA
    # -------------------------
    arestas_caminho = set()

    if caminho_destacado and len(caminho_destacado) >= 2:
        arestas_caminho = set(zip(caminho_destacado, caminho_destacado[1:]))

    # -------------------------
    # ARESTAS
    # -------------------------
    contador = 0

    for u, v, data in G.edges(data=True):

        if contador >= MAX_ARESTAS:
            break
        contador += 1

        cor = "#888888"
        largura = 1

        if (u, v) in arestas_caminho:
            cor = "#0000FF"
            largura = 4

        valor = data.get("valor", 0)

        valor = formatar_btc(float(valor)) if valor > 0 else ""
            
        txid = data.get("txid", "")

        label = ""
        if valor != "" and txid != "":
            label = f"{valor}\n{txid[:6]}..."
        elif valor != "":
            label = f"{valor}"

        edges.append(
            Edge(
                source=ids[u],
                target=ids[v],
                color=cor,
                width=largura,
                label=label
            )
        )

    # -------------------------
    # CONFIGURAÇÃO VISUAL
    # -------------------------
    config = Config(
        width="100%",
        height=800,
        directed=True,
        physics=True,
        nodeSpacing=300,
        repulsion=8000,
        springLength=250,
        damping=0.09,
        stabilization=True
    )

    return agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )
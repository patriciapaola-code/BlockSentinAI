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
        trajetorias_destacadas=None,
        possiveis_mixers=None,
        carteiras_alto_risco=None,
        mostrar_nomes_carteiras=True,
        mostrar_valores_transacoes=True):

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
    MAX_NOS = 600
    MAX_ARESTAS = 600

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

    # Prepara conjuntos para busca rápida
    mixer_wallets = {m['carteira'] for m in possiveis_mixers} if possiveis_mixers else set()
    high_risk_wallets = {
        r['carteira'] for r in carteiras_alto_risco 
        if r.get('score', 0) >= 70
    } if carteiras_alto_risco else set()

    # Prepara nós e arestas das trajetórias
    nodes_in_path = set()
    if trajetorias_destacadas:
        for traj in trajetorias_destacadas:
            nodes_in_path.update(traj.get('caminho', []))

    # -------------------------
    # NÓS
    # -------------------------
    for no in G.nodes():

        score = scores.get(no, {}).get("score", 0) if scores else 0

        # Define propriedades visuais com base nos dados do dossiê
        tamanho = 15
        formato = "dot" # Círculo padrão
        cor_no = corPorRiscoHex(score)
        borda_largura = 1
        borda_cor = "#888888" # Cinza padrão

        if no == carteira_principal:
            cor_no = "#006400"  # Verde escuro
            tamanho = 35
        elif no in mixer_wallets:
            cor_no = "#8400FF"  # Roxo para mixers
            tamanho = 25
        elif no in high_risk_wallets:
            cor_no = "#800000"  # Vinho
            tamanho = 22
        
        if no in nodes_in_path:
            borda_cor = "#0000FF" # Borda azul para nós em trajetórias
            borda_largura = 3

        # Define o label do nó
        label_no = ""
        if mostrar_nomes_carteiras:
            if no == carteira_principal:
                label_no = "Carteira Inicial"
            else:
                label_no = nomes[no]

        nodes.append(
            Node(
                id=ids[no],
                label=label_no,
                title=f"{no}\nScore={round(score, 2)}",
                shape=formato,
                size=tamanho,
                # A cor da borda deve ser passada dentro do objeto 'color'
                color={
                    "background": cor_no,
                    "border": borda_cor,
                    "highlight": {"border": "#FFD700", "background": cor_no},
                    "hover": {"border": "#FFD700", "background": cor_no}
                },
                font={
                    "color": "#000000",
                    "face": "arial",
                    "size": 14,
                    "strokeWidth": 4,
                    "strokeColor": "#00FF55"
                },
                borderWidth=borda_largura,
                # Efeito de brilho (neon) usando a propriedade de sombra
                shadow={
                    "enabled": True,
                    "color": cor_no,  # O brilho tem a mesma cor do nó
                    "size": 50,       # Intensidade do brilho
                    "x": 0,
                    "y": 0
                }
            )
        )

    # -------------------------
    # TRAJETÓRIA DESTACADA
    # -------------------------
    arestas_principais = set()
    arestas_secundarias = set()

    if trajetorias_destacadas:
        # A primeira trajetória é a principal
        if len(trajetorias_destacadas) > 0:
            caminho_principal = trajetorias_destacadas[0].get('caminho', [])
            if len(caminho_principal) >= 2:
                arestas_principais = set(zip(caminho_principal, caminho_principal[1:]))
        
        # As demais são secundárias
        for traj in trajetorias_destacadas[1:]:
            caminho_secundario = traj.get('caminho', [])
            arestas_secundarias.update(zip(caminho_secundario, caminho_secundario[1:]))

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
        dashed = False

        if (u, v) in arestas_principais:
            cor = "#0000FF"
            largura = 4
        elif (u, v) in arestas_secundarias:
            cor = "#4169E1" # Royal Blue
            largura = 2
            dashed = True

        valor = data.get("valor", 0)

        valor = formatar_btc(float(valor)) if valor > 0 else ""
            
        txid = data.get("txid", "")

        label = ""
        if mostrar_valores_transacoes:
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
                dashes=dashed,
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
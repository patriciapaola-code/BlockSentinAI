from networkx.utils import UnionFind
import networkx as nx
import pandas as pd
import numpy as np
import json
from collections import defaultdict

# =========================
# HEURÍSTICAS DE TRANSFORMAÇÃO
# =========================

def heuristicaMultiInput(G):
    uf = UnionFind()
    tx_inputs = {}

    # Agrupa todas as origens (inputs) pelo ID da transação (txid/key)
    for origem, destino, chave, dados in G.edges(keys=True, data=True):
        if dados.get("tipo") != "input":
            continue

        txid = dados.get("txid")
        if not txid:
            continue

        if txid not in tx_inputs:
            tx_inputs[txid] = set()

        tx_inputs[txid].add(origem)

    # Se houver mais de uma origem para a mesma transação, unifica sob a mesma entidade
    for txid, origens in tx_inputs.items():
        origens_lista = list(origens)
        if len(origens_lista) > 1:
            principal = origens_lista[0]
            for carteira in origens_lista[1:]:
                uf.union(principal, carteira)
    return uf

def aplicarChangeAddress(G):
    G_novo = G.copy()
    
    for no in list(G.nodes()):
        if no not in G_novo: 
            continue
            
        sucessores = sorted(set(G_novo.successors(no)))
        
        # Só avalia se houver exatamente 2 carteiras de destino únicas
        if len(sucessores) == 2:
            destino1, destino2 = sucessores[0], sucessores[1]
            
            # Funde o nó se um dos destinos for uma carteira "folha" (novo endereço de troco)
            if G_novo.out_degree(destino1) == 0:
                G_novo = nx.contracted_nodes(G_novo, no, destino1, self_loops=False)
            elif G_novo.out_degree(destino2) == 0:
                G_novo = nx.contracted_nodes(G_novo, no, destino2, self_loops=False)
                
    return G_novo

def aplicarValores(G):
    valores = [dados.get("valor", 0) for _, _, _, dados in G.edges(keys=True, data=True)]
    
    if not valores:
        return G
        
    mediana = np.median(valores)

    for origem, destino, txid, dados in G.edges(keys=True, data=True):
        valor = dados.get("valor", 0)
        
        if 0.5 * mediana <= valor <= 1.5 * mediana:
            dados["valor_semelhante"] = True
        else:
            dados["valor_semelhante"] = False
            
    return G

def aplicarTempo(G, bin_size=7*24*3600, top_k=1):

    edges = [
        (u, v, k, d)
        for u, v, k, d in G.edges(keys=True, data=True)
        if d.get("timestamp") is not None
    ]

    if not edges:
        return G

    timestamps = [d["timestamp"] for _, _, _, d in edges]

    t_min = min(timestamps)

    # 1. Criar bins
    bins = defaultdict(list)

    for u, v, k, d in edges:
        ts = d["timestamp"]
        idx = (ts - t_min) // bin_size
        bins[idx].append((u, v, k, d))

    # 2. Calcular score de cada bin
    bin_scores = []

    for b, e_list in bins.items():
        nodes = set()
        for u, v, _, _ in e_list:
            nodes.add(u)
            nodes.add(v)

        score = len(e_list) + len(nodes)  # densidade estrutural simples
        bin_scores.append((score, b))

    # 3. Selecionar top bins
    bin_scores.sort(reverse=True)
    selected_bins = set([b for _, b in bin_scores[:top_k]])

    # 4. Construir subgrafo final
    G_novo = nx.MultiDiGraph()

    for b in selected_bins:
        for u, v, k, d in bins[b]:
            G_novo.add_edge(u, v, key=k, **d)

    return G_novo

def aplicarChain(G):
    G_novo = G.copy()
    
    for no in list(G.nodes()):
        if no not in G_novo: 
            continue
        
        entradas_unicas = list(set(G_novo.predecessors(no)))
        saidas_unicas = list(set(G_novo.successors(no)))

        if len(entradas_unicas) == 1 and len(saidas_unicas) == 1:
            pred = entradas_unicas[0]
            succ = saidas_unicas[0]

            if pred != succ:
                valor_total = sum(d.get("valor", 0) for _, _, d in G_novo.edges(no, data=True))
                G_novo.add_edge(pred, succ, key=f"fused_{no}", valor=valor_total)
                G_novo.remove_node(no)
                
    return G_novo

# =========================
# HEURÍSTICAS DE ANÁLISE
# =========================

def analisarFanIn(G):
    fanin = {}
    for no in G.nodes():
        grau_entrada_unico = len(set(G.predecessors(no)))
        if grau_entrada_unico >= 3:
            fanin[no] = grau_entrada_unico
    return fanin

def analisarFanOut(G):
    fanout = {}
    for no in G.nodes():
        grau_saida_unico = len(set(G.successors(no)))
        if grau_saida_unico >= 3:
            fanout[no] = grau_saida_unico
    return fanout

def analisarPageRank(G):
    G_simples = nx.DiGraph(G)
    return nx.pagerank(G_simples, alpha=0.85)

def analisarBetweenness(G):
    G_simples = nx.DiGraph(G)
    return nx.betweenness_centrality(G_simples)

def analisarCloseness(G):
    G_simples = nx.DiGraph(G)
    return nx.closeness_centrality(G_simples)

def analisarDegree(G):
    G_simples = nx.DiGraph(G)
    return nx.degree_centrality(G_simples)

def analisarClusters(G):
    G_simples = nx.DiGraph(G)
    return list(nx.weakly_connected_components(G_simples))

def analisarChain(G):
    chains = []
    for no in G.nodes():
        entradas_unicas = set(G.predecessors(no))
        saidas_unicas = set(G.successors(no))
        
        if len(entradas_unicas) == 1 and len(saidas_unicas) == 1:
            chains.append(no)
    return chains

def detectarKeyAddresses(G):
    G_simples = nx.DiGraph(G)
    pagerank = nx.pagerank(G_simples)
    
    key_addresses = {no: score for no, score in pagerank.items() if score > 0.01}
    return key_addresses

def normalizar(valor, maior):
    if maior <= 0:
        return 0
    return valor / maior

def resolverCarteiraInicial(carteira_inicial, uf=None):
    if uf is None:
        return carteira_inicial

    return uf[carteira_inicial] if carteira_inicial in uf else carteira_inicial

def classificarRisco(score):
    if score >= 70:
        return "ALTO"
    if score >= 40:
        return "MEDIO"
    if score > 0:
        return "BAIXO"
    return "SEM EVIDENCIA"

def calcularScoreRisco(G, carteira_inicial):
    if G.number_of_nodes() == 0:
        return {}

    G_simples = nx.DiGraph(G)
    G_nao_direcionado = G_simples.to_undirected()

    if carteira_inicial in G_nao_direcionado:
        distancias = nx.single_source_shortest_path_length(
            G_nao_direcionado,
            carteira_inicial
        )
    else:
        distancias = {}

    try:
        pagerank = nx.pagerank(G_simples, alpha=0.85)
    except Exception:
        pagerank = {no: 0 for no in G.nodes()}

    try:
        betweenness = nx.betweenness_centrality(G_simples)
    except Exception:
        betweenness = {no: 0 for no in G.nodes()}

    graus = {
        no: len(set(G.predecessors(no))) + len(set(G.successors(no)))
        for no in G.nodes()
    }
    maior_grau = max(graus.values(), default=0)
    maior_pagerank = max(pagerank.values(), default=0)
    maior_betweenness = max(betweenness.values(), default=0)

    chain_nodes = set(analisarChain(G))
    scores = {}

    for no in G.nodes():
        motivos = []
        score = 0

        if no == carteira_inicial:
            score += 100
            motivos.append("carteira maliciosa inicial")
        else:
            distancia = distancias.get(no)
            if distancia is not None:
                score_distancia = max(0, 35 - (distancia * 8))
                score += score_distancia
                motivos.append(f"distancia {distancia} da carteira inicial")

        grau_score = normalizar(graus.get(no, 0), maior_grau) * 20
        if grau_score >= 8:
            motivos.append("muitas conexoes")
        score += grau_score

        pr_score = normalizar(pagerank.get(no, 0), maior_pagerank) * 15
        if pr_score >= 6:
            motivos.append("PageRank relevante")
        score += pr_score

        between_score = normalizar(betweenness.get(no, 0), maior_betweenness) * 15
        if between_score >= 6:
            motivos.append("atua como intermediaria")
        score += between_score

        arestas = list(G.in_edges(no, keys=True, data=True)) + list(G.out_edges(no, keys=True, data=True))
        if any(dados.get("valor_semelhante") for _, _, _, dados in arestas):
            score += 10
            motivos.append("transaciona valores semelhantes")

        if no in chain_nodes:
            score += 5
            motivos.append("participa de cadeia simples")

        score = float(min(100, round(score, 2)))
        scores[no] = {
            "score": score,
            "risco": classificarRisco(score),
            "motivos": motivos if motivos else ["sem evidencia forte"]
        }

    return scores

def imprimirRelatorioRisco(scores, limite=10):
    ordenados = sorted(
        scores.items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )

    print("\n===== RELATORIO DE RISCO =====")

    for posicao, (carteira, dados) in enumerate(ordenados[:limite], start=1):
        motivos = "; ".join(dados["motivos"][:4])
        print(
            f"{posicao}. {carteira} | score={dados['score']} | "
            f"risco={dados['risco']} | motivos: {motivos}"
        )

def encontrarTrajetoriasProvaveis(
    G,
    carteira_inicial,
    scores,
    limite=5,
    cutoff=6
):
    if G.number_of_nodes() == 0 or carteira_inicial not in G:
        return []

    trajetorias = []
    vistos = set()

    G_work = G.copy()

    # 🔥 cutoff adaptativo (evita travar em grafos maiores)
    cutoff = max(cutoff, int(len(G_work) ** 0.3) + 2)

    for destino in G_work.nodes():
        if destino == carteira_inicial:
            continue

        if not nx.has_path(G_work, carteira_inicial, destino):
            continue

        caminhos = nx.all_simple_paths(
            G_work,
            source=carteira_inicial,
            target=destino,
            cutoff=cutoff
        )

        for caminho in caminhos:
            if len(caminho) < 2:
                continue

            chave = tuple(caminho)
            if chave in vistos:
                continue
            vistos.add(chave)

            # =========================
            # SCORE DO DESTINO (reduzido impacto)
            # =========================
            score_destino = scores.get(destino, {}).get("score", 0)

            entradas = len(set(G_work.predecessors(destino)))
            saidas = len(set(G_work.successors(destino)))

            if saidas == 0:
                score_destino += 15
            elif saidas <= 2:
                score_destino += 8

            if entradas >= 3:
                score_destino += 10

            # =========================
            # SCORE DO CAMINHO (fluxo real)
            # =========================
            risco_caminho = sum(
                scores.get(no, {}).get("score", 0)
                for no in caminho
            )

            # penalização leve (não destrói caminhos longos)
            risco_caminho = risco_caminho / (1 + len(caminho) * 0.3)

            # bônus de profundidade (mais forte que antes)
            profundidade_bonus = min(len(caminho) * 3, 15)

            # =========================
            # SCORE FINAL BALANCEADO
            # =========================
            score_final = (
                risco_caminho * 0.6 +
                score_destino * 0.2 +
                profundidade_bonus
            )

            trajetorias.append({
                "destino": destino,
                "caminho": caminho,
                "score_final": round(score_final, 2),
                "score_base_destino": round(score_destino, 2),
                "entradas": entradas,
                "saidas": saidas,
                "tamanho_caminho": len(caminho)
            })

    # 🔥 ordenação correta (principal fix)
    trajetorias.sort(
        key=lambda x: x["score_final"],
        reverse=True
    )

    return trajetorias[:limite]

def imprimirTrajetorias(trajetorias):
    print("\n===== TRAJETORIAS PROVÁVEIS =====")

    if not trajetorias:
        print("Nenhuma trajetória provável encontrada a partir da carteira inicial.")
        return

    for posicao, dados in enumerate(trajetorias, start=1):
        caminho = " -> ".join(dados["caminho"])

        print(
            f"{posicao}. destino={dados['destino']} | "
            f"score_final={dados['score_final']} | "
            f"score_base_destino={dados['score_base_destino']} | "
            f"tamanho={dados['tamanho_caminho']} | "
            f"entradas={dados['entradas']} | saidas={dados['saidas']}"
        )

        print(f"   caminho: {caminho}")
        
        if dados["score_final"] >= 70:
            risco = "ALTO risco de fluxo suspeito"
        elif dados["score_final"] >= 40:
            risco = "risco moderado de comportamento anômalo"
        else:
            risco = "baixo risco observado"

def topItens(dados, limite=10):
    ordenados = sorted(
        dados.items(),
        key=lambda item: item[1],
        reverse=True
    )[:limite]

    return [
        {
            "carteira": chave,
            "valor": round(float(valor), 4)
        }
        for chave, valor in ordenados
    ]

def calcularSimilaridadeValores(valores):
    valores = [valor for valor in valores if valor is not None and valor > 0]

    if len(valores) < 2:
        return 0

    media = float(np.mean(valores))
    if media == 0:
        return 0

    desvio = float(np.std(valores))
    coeficiente_variacao = desvio / media

    return round(max(0, 1 - coeficiente_variacao), 4)

def entropia_valores(valores):
    valores = np.array(valores)
    if len(valores) == 0:
        return 0
    return np.std(valores) / (np.mean(valores) + 1e-9)


def detectarPossiveisMixers(G, limite=10):
    candidatos = defaultdict(lambda: {
        "score_mixer": 0,
        "motivos": set(),
        "txids": set()
    })

    tx_map = defaultdict(lambda: {
        "inputs": set(),
        "outputs": set(),
        "valores": []
    })

    for u, v, k, d in G.edges(keys=True, data=True):
        txid = d.get("txid")
        if not txid:
            continue

        tx_map[txid]["inputs"].add(u)
        tx_map[txid]["outputs"].add(v)
        tx_map[txid]["valores"].append(d.get("valor", 0))

    for txid, tx in tx_map.items():
        inputs = len(tx["inputs"])
        outputs = len(tx["outputs"])
        valores = tx["valores"]

        if len(valores) == 0:
            continue

        ent = entropia_valores(valores)

        score = 0

        score += min(inputs * 4, 20)
        score += min(outputs * 4, 20)

        score += ent * 30

        if inputs >= 2 and outputs >= 2:
            score += 10

        if ent > 0.5:
            score += 10
            motivo_extra = "alta variacao de valores"

        else:
            motivo_extra = None

        if score >= 25:
            envolvidos = tx["inputs"].union(tx["outputs"])

            for carteira in envolvidos:
                candidatos[carteira]["score_mixer"] += score
                candidatos[carteira]["txids"].add(txid)
                candidatos[carteira]["motivos"].add(
                    f"transacao com {inputs} inputs e {outputs} outputs"
                )

                if motivo_extra:
                    candidatos[carteira]["motivos"].add(motivo_extra)

    for no in G.nodes():
        entradas = len(set(G.predecessors(no)))
        saidas = len(set(G.successors(no)))

        if entradas + saidas == 0:
            continue

        valores = [
            d.get("valor", 0)
            for _, _, _, d in list(G.in_edges(no, keys=True, data=True)) +
                             list(G.out_edges(no, keys=True, data=True))
        ]

        ent = entropia_valores(valores)

        score = 0

        score += min((entradas + saidas) * 2, 25)

        if entradas >= 3 and saidas >= 3:
            score += 15
            candidatos[no]["motivos"].add("hub com fluxo bidirecional")

        score += ent * 20

        if score >= 20:
            candidatos[no]["score_mixer"] += score
            candidatos[no]["motivos"].add(f"fan-in {entradas} / fan-out {saidas}")

    resultado = []

    for carteira, dados in candidatos.items():
        resultado.append({
            "carteira": carteira,
            "score_mixer": float(min(round(dados["score_mixer"], 2), 100)),
            "motivos": sorted(dados["motivos"]),
            "txids": sorted(dados["txids"])
        })

    resultado.sort(key=lambda x: x["score_mixer"], reverse=True)

    return resultado[:limite]

# =========================
# ANÁLISE SOBRE DATAFRAME
# =========================

def analisarBurst(df):
    if df.empty or "timestamp" not in df.columns:
        return pd.Series(dtype=int)
        
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    por_minuto = df.groupby(pd.Grouper(key="timestamp", freq="1min")).size()
    return por_minuto

def analisarTempo(df):
    if df.empty or "timestamp" not in df.columns:
        return pd.Series(dtype=float)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    diferenca = df["timestamp"].diff().dt.total_seconds()
    
    return diferenca

def analisarValores(df):
    if df.empty or "valor" not in df.columns:
        return pd.DataFrame()

    media = df["valor"].mean()
    tolerancia = media * 0.1
    semelhantes = df[abs(df["valor"] - media) < tolerancia]
    
    return semelhantes

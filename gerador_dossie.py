import json
import pandas as pd
import analise_heuristica as ht
import numpy as np

def gerarDossieInvestigativo(G, carteira_inicial, scores, trajetorias=None, possiveis_mixers=None, coinjoin_suspeitas=None):
    
    trajetorias = trajetorias or []
    possiveis_mixers = possiveis_mixers or ht.detectarPossiveisMixers(G)
    coinjoin_suspeitas = coinjoin_suspeitas or {}
    
    # =============================================================================
    # ANÁLISE COMPORTAMENTAL (FOCADA NA CARTEIRA INICIAL)
    # =============================================================================
    # A análise agora é feita especificamente sobre a carteira inicial,
    # em vez de analisar o grafo inteiro, o que é mais preciso.
    analise_comp = ht.analisarAutomacaoPorCarteira(G, carteira_inicial)

    fanin = ht.analisarFanIn(G)
    fanout = ht.analisarFanOut(G)
    pagerank = ht.analisarPageRank(G) if G.number_of_nodes() > 0 else {}
    betweenness = ht.analisarBetweenness(G) if G.number_of_nodes() > 0 else {}
    closeness = ht.analisarCloseness(G) if G.number_of_nodes() > 0 else {}
    degree = ht.analisarDegree(G) if G.number_of_nodes() > 1 else {}
    clusters = ht.analisarClusters(G)
    key_addresses = ht.detectarKeyAddresses(G) if G.number_of_nodes() > 0 else {}
    
    # Extrai os nós de cadeia diretamente do atributo do grafo
    chains = [no for no, data in G.nodes(data=True) if data.get("chain_node", False)]

    vals = np.array([d["score"] for d in scores.values()])

    # Lida com o caso de não haver scores (grafo vazio)
    if vals.size > 0:
        threshold = np.percentile(vals, 90)
    else:
        threshold = 0
    
    carteiras_alto_risco = [
        {
            "carteira": carteira,
            "score": dados["score"],
            "risco": dados["risco"],
            "motivos": dados["motivos"]
        }
        for carteira, dados in sorted(
            scores.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )
        if dados["score"] >= threshold
    ]

    transacoes_coinjoin = [
        {"txid": txid, "motivo": dados["motivo"], "carteiras": dados["carteiras"]}
        for txid, dados in coinjoin_suspeitas.items()
    ]
    
    return {
        "carteira_inicial": carteira_inicial,
        "resumo_grafo": {
            "nos": G.number_of_nodes(),
            "arestas": G.number_of_edges(),
            "clusters": len(clusters)
        },
        "carteiras_alto_risco": carteiras_alto_risco[:10],
        "possiveis_mixers": possiveis_mixers,
        "transacoes_coinjoin_suspeitas": transacoes_coinjoin,
        "trajetorias_provaveis": trajetorias,
        
        "analise_comportamental": analise_comp, 

        "analises": {
            "fanin": ht.topItens(fanin),
            "fanout": ht.topItens(fanout),
            "pagerank": ht.topItens(pagerank),
            "betweenness": ht.topItens(betweenness),
            "closeness": ht.topItens(closeness),
            "degree": ht.topItens(degree),
            "key_addresses": ht.topItens(key_addresses),
            "chains": chains[:20],
            "clusters_maiores": sorted(
                [len(cluster) for cluster in clusters],
                reverse=True
            )[:10]
        },
        "observacoes": [
            "Scores e mixers sao indicios heuristicos, nao prova conclusiva.",
            "Uma LLM investigadora deve usar este dossie para explicar hipoteses e incertezas.",
            "Nos com possivel mixer podem representar servicos legitimos, exchanges ou consolidadores.",
            "A analise comportamental mapeia o uso potencial de scripts e automacoes pelo atacante.",
            "Transacoes em transacoes_coinjoin_suspeitas tem outputs de denominacao identica.",
            "Essas carteiras nao foram fundidas no clustering de common-input-ownership, mas podem indicar coordenacao deliberada entre elas (ex.: consolidacao de pagamentos)."
        ]
    }

def imprimirDossieInvestigativo(dossie):
    print("\n===== DOSSIE INVESTIGATIVO =====")
    print("Carteira inicial:", dossie["carteira_inicial"])
    print("Nos:", dossie["resumo_grafo"]["nos"])
    print("Arestas:", dossie["resumo_grafo"]["arestas"])
    print("Clusters:", dossie["resumo_grafo"]["clusters"])
    print("Carteiras de alto risco:", len(dossie["carteiras_alto_risco"]))
    print("Possiveis mixers:", len(dossie["possiveis_mixers"]))
    print("Trajetorias provaveis:", len(dossie["trajetorias_provaveis"]))
    print("Transacoes com suspeita de CoinJoin:", len(dossie["transacoes_coinjoin_suspeitas"]))
    
    if dossie["possiveis_mixers"]:
        print("\nTop possiveis mixers:")
        for mixer in dossie["possiveis_mixers"][:5]:
            motivos = "; ".join(mixer["motivos"][:3])
            print(
                f"- {mixer['carteira']} | score_mixer={mixer['score_mixer']} | "
                f"motivos: {motivos}"
            )
            
    if dossie["transacoes_coinjoin_suspeitas"]:
        print("\nTop transacoes suspeitas de CoinJoin:")
        for tx in dossie["transacoes_coinjoin_suspeitas"][:5]:
            print(f"- txid={tx['txid']} | motivo: {tx['motivo']} | carteiras: {len(tx['carteiras'])}")

def salvarDossieInvestigativo(dossie, caminho="dossie_investigativo.json"):
    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dossie, arquivo, ensure_ascii=False, indent=2)

        # =========================
        # ATUALIZAÇÃO DO ÍNDICE FAISS (RAG)
        # =========================
        # Após salvar o JSON, também criamos/atualizamos o índice vetorial para o assistente de IA.
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_core.documents import Document

        # Cria um "Documento" único com todo o conteúdo do dossiê para o RAG
        doc = Document(page_content=json.dumps(dossie, indent=2))
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Cria um novo índice FAISS a partir do documento atualizado
        vectorstore = FAISS.from_documents([doc], embeddings)
        vectorstore.save_local("faiss_index")

    except (ImportError, Exception) as e:
        print(f"AVISO: Falha ao salvar ou indexar o dossiê: {e}")

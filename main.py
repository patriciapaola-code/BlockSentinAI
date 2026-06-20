import etapa2_grafo as etp2
import etapa5_graphsense as etp5
import heuristica as ht
import agent as ag
import dossie as ds

def main():

    # Carteira inicial (ponto de origem do rastreamento)
    wallet = "bc1q4my6vqq8cg689drf9jccqudjclv67sz4cudkyd"

    # =========================
    # EXPANSÃO DO GRAFO
    # =========================
    print("Expandindo grafo...")

    # Cria o grafo bruto a partir da blockchain (ou fonte de dados)
    # profundidade: quantos saltos explorar
    # max_vizinhos: limite por nó
    # max_nos: limite total do grafo
    G_bruto = etp5.expandirGrafo(
        wallet,
        profundidade=4,
        max_vizinhos=100,
        max_nos=500
    )

    print("\n===== GRAFO BRUTO =====")
    print("Nós:", G_bruto.number_of_nodes())
    print("Arestas:", G_bruto.number_of_edges())

    # Calcula score de risco inicial no grafo bruto
    score_bruto = ht.calcularScoreRisco(G_bruto, wallet)

    # Visualiza grafo bruto com coloração por risco
    etp2.gerarGrafo(G_bruto, wallet, scores=score_bruto)


    # =========================
    # HEURÍSTICA MULTI-INPUT
    # =========================
    print("\nAplicando Multi-Input...")

    # Agrupa entradas múltiplas de uma mesma transação
    # (heurística de clustering de identidade de usuário)
    uf = ht.heuristicaMultiInput(G_bruto)

    # Reconstroi o grafo com nós fundidos
    G_multi = etp5.construirGrafoFiltrado(G_bruto, uf)

    print("\n===== MULTI-INPUT =====")
    print("Nós:", G_multi.number_of_nodes())
    print("Arestas:", G_multi.number_of_edges())

    # Recalcula risco após agrupamento
    score_multi = ht.calcularScoreRisco(G_multi, wallet)

    # Reconstrói trajetórias prováveis
    trajetorias_multi = ht.encontrarTrajetoriasProvaveis(G_multi, wallet, score_multi)

    # Visualiza grafo com destaque da melhor trajetória
    etp2.gerarGrafoFiltrado(
        G_multi,
        "Multi-Input",
        scores=score_multi,
        caminho_destacado=trajetorias_multi[0]["caminho"] if trajetorias_multi else None
    )


    # =========================
    # HEURÍSTICA CHANGE ADDRESS
    # =========================
    print("\nAplicando Change Address...")

    # Identifica endereços de troco e os funde com origem
    G_change = ht.aplicarChangeAddress(G_multi)

    print("\n===== CHANGE ADDRESS =====")
    print("Nós:", G_change.number_of_nodes())
    print("Arestas:", G_change.number_of_edges())

    score_change = ht.calcularScoreRisco(G_change, wallet)

    trajetorias_change = ht.encontrarTrajetoriasProvaveis(G_change, wallet, score_change)

    # Imprime trajetórias investigativas
    ht.imprimirTrajetorias(trajetorias_change)

    etp2.gerarGrafoFiltrado(
        G_change,
        "Change Address",
        scores=score_change,
        caminho_destacado=trajetorias_change[0]["caminho"] if trajetorias_change else None
    )


    # =========================
    # HEURÍSTICA TEMPORAL
    # =========================
    print("\nAplicando Heurística Temporal...")

    # Seleciona janelas de tempo mais densas de atividade
    G_tempo = ht.aplicarTempo(G_change)

    print("\n===== TEMPO =====")
    print("Nós:", G_tempo.number_of_nodes())
    print("Arestas:", G_tempo.number_of_edges())

    score_tempo = ht.calcularScoreRisco(G_tempo, wallet)

    trajetorias_tempo = ht.encontrarTrajetoriasProvaveis(G_tempo, wallet, score_tempo)

    ht.imprimirTrajetorias(trajetorias_tempo)

    etp2.gerarGrafoFiltrado(
        G_tempo,
        "Tempo",
        scores=score_tempo,
        caminho_destacado=trajetorias_tempo[0]["caminho"] if trajetorias_tempo else None
    )


    # =========================
    # HEURÍSTICA DE VALORES
    # =========================
    print("\nAplicando Similaridade de Valores...")

    # Agrupa transações com valores semelhantes (possível automação ou batching)
    G_valores = ht.aplicarValores(G_change)

    print("\n===== VALORES =====")
    print("Nós:", G_valores.number_of_nodes())
    print("Arestas:", G_valores.number_of_edges())

    score_valores = ht.calcularScoreRisco(G_valores, wallet)

    trajetorias_valores = ht.encontrarTrajetoriasProvaveis(G_valores, wallet, score_valores)

    ht.imprimirTrajetorias(trajetorias_valores)

    etp2.gerarGrafoFiltrado(
        G_valores,
        "Valores",
        scores=score_valores,
        caminho_destacado=trajetorias_valores[0]["caminho"] if trajetorias_valores else None
    )


    # =========================
    # HEURÍSTICA CHAIN
    # =========================
    print("\nAplicando Chain...")

    # Detecta sequências lineares de transações (fluxo em cadeia)
    G_chain = ht.aplicarChain(G_valores)

    print("\n===== CHAIN =====")
    print("Nós:", G_chain.number_of_nodes())
    print("Arestas:", G_chain.number_of_edges())

    score_chain = ht.calcularScoreRisco(G_chain, wallet)

    trajetorias_chain = ht.encontrarTrajetoriasProvaveis(G_chain, wallet, score_chain)

    ht.imprimirTrajetorias(trajetorias_chain)

    etp2.gerarGrafoFiltrado(
        G_chain,
        "Chain",
        scores=score_chain,
        caminho_destacado=trajetorias_chain[0]["caminho"] if trajetorias_chain else None
    )


    # =========================
    # SCORE FINAL + ANÁLISE GLOBAL
    # =========================
    print("\nCalculando score de risco...")

    # Score final consolidado após todas heurísticas
    scores = ht.calcularScoreRisco(G_chain, wallet)

    # Trajetórias finais do sistema
    trajetoria = ht.encontrarTrajetoriasProvaveis(G_chain, wallet, scores)

    ht.imprimirTrajetorias(trajetoria)

    # Detecção de possíveis mixers (heurística de padrão estrutural)
    possive_mixers = ht.detectarPossiveisMixers(G_chain)


    # =========================
    # DOSSIÊ FINAL
    # =========================
    dossie = ds.gerarDossieInvestigativo(
        G_chain,
        wallet,
        scores,
        trajetoria,
        possive_mixers
    )

    ds.salvarDossieInvestigativo(dossie)
    ds.imprimirDossieInvestigativo(dossie)


    # =========================
    # AGENTE INVESTIGATIVO (LLM)
    # =========================
    ag.criarAgent()


if __name__ == "__main__":
    main()
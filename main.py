import etapa1_leitura as etp1
import etapa3_risco as etp3 
import etapa2_grafo as etp2
import etapa3_risco as etp3
import etapa5_graphsense as etp5
import heuristica as ht

def main():

    wallet = "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo" ## id de uma carteira na rede blockchain, nao necessariamente suspeita
    G_bruto = etp5.expandirGrafo(wallet, 2, 50, 1000)
    etp2.gerarGrafo(G_bruto, wallet)
    cluster = ht.multiInputHeuristic(G_bruto)
    G_filtrado = etp5.construirGrafoFiltrado(G_bruto, cluster)
    etp2.gerarGrafoFiltrado(G_filtrado)

main()
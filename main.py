import etapa1_leitura as etp1
import etapa3_risco as etp3 
import etapa2_grafo as etp2
import etapa3_risco as etp3
import etapa5_graphsense as etp5

def main():

    wallet = "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo"
    G = etp5.expandirGrafo(wallet, profundidade=2, max_vizinhos=10, max_nos=500)
    print(type(G))
    etp5.resumirGrafo(G)
    etp2.gerarGrafo(G, carteira_principal=wallet)

main()
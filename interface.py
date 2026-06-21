import json
import time

import streamlit as st
import etapa5_graphsense as etp5
import heuristica as ht
import agent as ag
import dossie as ds
import dashboard_graph as dg
import gerar_grafo as etp2 

# ==============================================================================
# 1. CONFIGURAÇÃO DE PÁGINA DO STREAMLIT (OBRIGATORIAMENTE O PRIMEIRO COMANDO)
# ==============================================================================
st.set_page_config(
    layout="wide", 
    page_title="Sistema Antiransomware - Forense Blockchain", 
    page_icon="🕵️‍♂️"
)

# ==============================================================================
# 2. FUNÇÃO COM CACHE PARA PROCESSAMENTO PESADO DA BLOCKCHAIN
# ==============================================================================
@st.cache_resource(show_spinner=False)
def carregar_toda_a_blockchain(wallet):

    historico = []

    # =========================
    # GRAFO BRUTO
    # =========================
    G_bruto = etp5.expandirGrafo(
        wallet,
        profundidade=4,
        max_vizinhos=100,
        max_nos=500
    )

    score_bruto = ht.calcularScoreRisco(G_bruto, wallet)

    historico.append({
        "nome": "1. Grafo Bruto",
        "grafo": G_bruto,
        "scores": score_bruto,
        "caminho": None
    })

    # =========================
    # MULTI INPUT
    # =========================
    uf = ht.heuristicaMultiInput(G_bruto)
    G_multi = etp5.construirGrafoFiltrado(G_bruto, uf)

    score_multi = ht.calcularScoreRisco(G_multi, wallet)
    trajetorias_multi = ht.encontrarTrajetoriasProvaveis(
        G_multi,
        wallet,
        score_multi
    )

    historico.append({
        "nome": "2. Multi-Input",
        "grafo": G_multi,
        "scores": score_multi,
        "caminho": trajetorias_multi[0]["caminho"] if trajetorias_multi else None
    })

    # =========================
    # CHANGE ADDRESS
    # =========================
    G_change = ht.aplicarChangeAddress(G_multi)

    score_change = ht.calcularScoreRisco(G_change, wallet)
    trajetorias_change = ht.encontrarTrajetoriasProvaveis(
        G_change,
        wallet,
        score_change
    )

    historico.append({
        "nome": "3. Change Address",
        "grafo": G_change,
        "scores": score_change,
        "caminho": trajetorias_change[0]["caminho"] if trajetorias_change else None
    })

    # =========================
    # TEMPO
    # =========================
    G_tempo = ht.aplicarTempo(G_change)

    score_tempo = ht.calcularScoreRisco(G_tempo, wallet)
    trajetorias_tempo = ht.encontrarTrajetoriasProvaveis(
        G_tempo,
        wallet,
        score_tempo
    )

    historico.append({
        "nome": "4. Tempo",
        "grafo": G_tempo,
        "scores": score_tempo,
        "caminho": trajetorias_tempo[0]["caminho"] if trajetorias_tempo else None
    })

    # =========================
    # VALORES
    # =========================
    G_valores = ht.aplicarValores(G_tempo)

    score_valores = ht.calcularScoreRisco(G_valores, wallet)
    trajetorias_valores = ht.encontrarTrajetoriasProvaveis(
        G_valores,
        wallet,
        score_valores
    )

    historico.append({
        "nome": "5. Valores",
        "grafo": G_valores,
        "scores": score_valores,
        "caminho": trajetorias_valores[0]["caminho"] if trajetorias_valores else None
    })

    # =========================
    # CHAIN
    # =========================
    G_chain = ht.aplicarChain(G_valores)

    score_chain = ht.calcularScoreRisco(G_chain, wallet)
    trajetorias_chain = ht.encontrarTrajetoriasProvaveis(
        G_chain,
        wallet,
        score_chain
    )

    historico.append({
        "nome": "6. Chain",
        "grafo": G_chain,
        "scores": score_chain,
        "caminho": trajetorias_chain[0]["caminho"] if trajetorias_chain else None
    })

    # =========================
    # DOSSIÊ
    # =========================
    possiveis_mixers = ht.detectarPossiveisMixers(G_chain)

    dossie = ds.gerarDossieInvestigativo(
        G_chain,
        wallet,
        score_chain,
        trajetorias_chain,
        possiveis_mixers
    )

    return historico, dossie

@st.cache_resource
def carregar_agent():
    return ag.iniciarAgent()

@st.cache_data(show_spinner=False)
def cached_retrieve(_retriever, query):
    return _retriever.invoke(query)

def iniciarChat(llm, prompt):

    st.markdown("""
        <style>
        .stChatMessage { font-size: 15px; }
        .block-container { padding-top: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    # =========================
    # STATE INICIAL
    # =========================
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = [
            {
                "role": "assistant",
                "content": "Sou o investigador forense. Pergunte sobre o grafo ou transações suspeitas."
            }
        ]

    if "last_llm_call" not in st.session_state:
        st.session_state.last_llm_call = 0

    if "processing" not in st.session_state:
        st.session_state.processing = False

    # =========================
    # EXIBIÇÃO HISTÓRICO
    # =========================
    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # =========================
    # INPUT
    # =========================
    pergunta = st.chat_input("Sua pergunta sobre as transações:")

    # =========================
    # CONTROLE PRINCIPAL
    # =========================
    if pergunta:

        pergunta_limpa = pergunta.strip()
        if not pergunta_limpa:
            st.stop()

        if st.session_state.processing:
            st.warning("Já estou processando uma pergunta. Aguarde...")
            st.stop()

        st.session_state.processing = True

        try:
            now = time.time()
            if now - st.session_state.last_llm_call < 3:
                st.warning("⏳ Aguarde alguns segundos antes de enviar outra pergunta.")
                st.stop()

            st.session_state.last_llm_call = now

            st.session_state.mensagens.append(
                {"role": "user", "content": pergunta_limpa}
            )

            with st.chat_message("user"):
                st.markdown(pergunta_limpa)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                placeholder.markdown("🧠 Analisando dados...")

                contexto = json.dumps(st.session_state.dossie, ensure_ascii=False)

                mensagens = prompt.invoke({
                    "contexto": contexto,
                    "pergunta": pergunta_limpa
                })

                resposta = llm.invoke(mensagens).content

                placeholder.markdown(resposta)

                st.session_state.mensagens.append(
                    {"role": "assistant", "content": resposta}
                )

        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                st.error("🚨 Limite de requisições atingido. Aguarde 30–60 segundos.")
            else:
                st.error(f"Erro: {e}")

        finally:
            st.session_state.processing = False

# ==============================================================================
# 3. INTERFACE DO USUÁRIO E CONTROLE DE EXIBIÇÃO (STREAMLIT UI)
# ==============================================================================
def interface():

    st.title("🕵️ Dashboard Interativo - Rastreamento de Ransomware")

    wallet = "bc1q4my6vqq8cg689drf9jccqudjclv67sz4cudkyd"

    # =========================
    # INIT GLOBAL STATE
    # =========================
    if "historico" not in st.session_state:
        with st.spinner("Processando blockchain..."):
            historico, dossie = carregar_toda_a_blockchain(wallet)
            st.session_state.historico = historico
            st.session_state.dossie = dossie

    if "grafo_index" not in st.session_state:
        st.session_state.grafo_index = 0

    if "agent" not in st.session_state:
        st.session_state.agent = None

    # =========================
    # TABS
    # =========================
    tab_grafos, tab_chat = st.tabs([
        "📊 Fluxo de Grafos",
        "🔎 Assistente IA Forense"
    ])

    # =========================
    # ABA 1 - GRAFOS
    # =========================
    with tab_grafos:

        historico = st.session_state.historico
        index = st.session_state.grafo_index

        # proteção contra índice inválido
        index = max(0, min(index, len(historico) - 1))
        st.session_state.grafo_index = index

        etapa = historico[index]

        col1, col2, col3 = st.columns([1, 3, 1])

        with col1:
            if st.button("⬅️", key="prev"):
                if st.session_state.grafo_index > 0:
                    st.session_state.grafo_index -= 1
                    st.rerun()

        with col3:
            if st.button("➡️", key="next"):
                if st.session_state.grafo_index < len(historico) - 1:
                    st.session_state.grafo_index += 1
                    st.rerun()

        st.subheader(etapa["nome"])

        st.write(
            f"Nós: {etapa['grafo'].number_of_nodes()} | "
            f"Arestas: {etapa['grafo'].number_of_edges()}"
        )

        dg.renderizar_grafo_interativo(
            G=etapa["grafo"],
            carteira_principal=wallet,
            scores=etapa["scores"],
            caminho_destacado=etapa["caminho"]
        )

        st.divider()

        with st.expander("Dossiê Investigativo"):
            st.json(st.session_state.dossie)

    # ================================
    # ABA 2 - CHAT (ISOLADO DO GRAFO)
    # ================================
    with tab_chat:

        st.subheader("🔎 Chat Forense Blockchain")
        st.caption("Investigação assistida por Inteligência Artificial")

        # init agent sob demanda
        if st.session_state.agent is None:
            with st.spinner("Inicializando o agente analítico..."):
                st.session_state.agent = carregar_agent()

        llm, prompt = st.session_state.agent

        iniciarChat(llm, prompt)
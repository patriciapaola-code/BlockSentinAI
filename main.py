
import streamlit as st
import fluxo_processamento as fp # Crie este novo módulo

def main():
    st.set_page_config(layout="wide")
    
    # Inicialização de estados
    if "data" not in st.session_state:
        st.session_state.data = None

    # Interface minimalista
    st.title("🕵️ BlockSentinAI")
    wallet = st.sidebar.text_input("Carteira", value="bc1q...")
    
    if st.sidebar.button("Analisar"):
        # A main apenas chama o orquestrador, não processa o grafo
        with st.spinner("Processando..."):
            st.session_state.data = fp.executar_pipeline_completo(wallet)
            fp.renderizar_dashboard(st.session_state.data)
            st.rerun()

    # Exibição (apenas se houver dados)
    if st.session_state.data:
        fp.renderizar_dashboard(st.session_state.data)

if __name__ == "__main__":
    main()


"""import app_streamlit as ui

def main():
    ui.interface()
    
if __name__ == "__main__":
    main() """




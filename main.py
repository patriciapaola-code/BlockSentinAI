import app_streamlit as ui
import indexador_dossie as vs

def main():
    vs.carregarVectorStore()
    ui.interface()
    
if __name__ == "__main__":
    main()

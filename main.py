import interface as ui
import build_vectorstore as vs

def main():
    vs.carregarVectorStore()
    ui.interface()
    
if __name__ == "__main__":
    main()
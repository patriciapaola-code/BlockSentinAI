from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import json

def carregarVectorStore():
    # =========================
    # CARREGAR DADOS
    # =========================
    with open("dossie_investigativo.json", "r", encoding="utf-8") as f:
        dados = json.load(f)

    documents = []

    for chave, valor in dados.items():
        texto = f"{chave}:\n{json.dumps(valor, indent=2, ensure_ascii=False)}"
        documents.append(Document(page_content=texto))

    # =========================
    # EMBEDDINGS (LOCAL)
    # =========================
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # =========================
    # CRIA E SALVA FAISS
    # =========================
    vectorstore = FAISS.from_documents(documents, embeddings)

    vectorstore.save_local("faiss_index")

    print("FAISS salvo com sucesso em 'faiss_index'")
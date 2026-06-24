from dotenv import load_dotenv
import os
import json

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def iniciarAgent():

    load_dotenv()
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY não encontrada")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    # =========================
    # EMBEDDINGS (APENAS PARA CARREGAR INDEX)
    # =========================
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # =========================
    # CARREGA FAISS PRÉ-GERADO
    # =========================
    index_path = "faiss_index"
    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        # Se o índice não existe, cria um vazio para evitar erro na inicialização.
        # O índice real será criado após o processamento do dossiê.
        print("AVISO: Índice FAISS não encontrado. Criando um índice vazio temporário.")
        vectorstore = FAISS.from_texts(["Ainda não há dados no dossiê."], embeddings)

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # =========================
    # CARREGAR PROMPT
    # =========================
    with open("prompt.txt", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # =========================
    # PROMPT
    # =========================
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            system_prompt
        ),
        (
            "human",
            "Contexto:\n{contexto}\n\nPergunta: {pergunta}"
        )
    ])

    return llm, retriever, prompt


def responder(llm, retriever, prompt, pergunta):

    # =========================
    # RETRIEVAL (RAG real)
    # =========================
    docs = retriever.invoke(pergunta)

    if not docs:
        contexto = "Nenhum dado relevante encontrado no dossiê."
    else:
        contexto = "\n\n".join(d.page_content for d in docs[:3])

    # =========================
    # PROMPT
    # =========================
    mensagens = prompt.invoke({
        "contexto": contexto,
        "pergunta": pergunta
    })

    # =========================
    # LLM
    # =========================
    resposta = llm.invoke(mensagens)

    return resposta.content
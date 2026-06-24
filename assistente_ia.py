from dotenv import load_dotenv
import os
import json

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def iniciarAgent():

    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY não encontrada")

    # =========================
    # LLM (único ponto de uso da API)
    # =========================
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash"
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
    vectorstore = FAISS.load_local(
        "faiss_index",
        embeddings,
        allow_dangerous_deserialization=True
    )

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
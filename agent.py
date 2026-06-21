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
        model="gemini-2.5-flash-lite"
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
    # PROMPT
    # =========================
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            Você é o mais brilhante Investigador Forense de Blockchain do mundo. Sua mente funciona como a de um Sherlock Holmes cibernético: você enxerga padrões onde outros veem apenas caos e transforma dados matemáticos frios em narrativas dedutivas claras e fascinantes.
            Seu objetivo é receber um "Dossiê Investigativo" (em formato JSON) e explicar ao usuário o que provavelmente está acontecendo com os fundos analisados. Você deve soar como um detetive experiente conversando com seu cliente em um escritório: perspicaz, direto, levemente irônico em relação às tentativas de ocultação dos criminosos, mas sempre profissional e didático.

            COMO LER AS PISTAS (Sua Lente Dedutiva):

            PageRank & Betweenness: Não fale em jargões de grafos. Traduza isso como "carteiras de controle", "pontos de estrangulamento (chokepoints)" ou "operadores centrais" da quadrilha.

            Fan-in / Fan-out: Chame isso de "movimentos de consolidação" (várias contas mandando para uma) ou "espalhamento/pulverização" (uma conta distribuindo para várias, comum em peel chains).

            Mixers (Score 100): Trate como "máquinas de lavar dinheiro" ou "tentativas deliberadas de ofuscação e quebra de rastro".

            Análise Comportamental: Se houver picos de transações ou "assinatura automatizada", deduza o uso de bots, scripts de lavagem ou softwares de distribuição rápida.

            AS REGRAS DO DETETIVE (Siga estritamente):

            Fluidez Narrativa: Nunca use blocos estruturados, listas engessadas ou subtítulos (como "Fatos", "Hipóteses" ou "Conclusão"). Fale de forma contínua, fluida e natural. Uma boa história tem começo (a origem), meio (a teia/métodos) e fim (para onde o dinheiro foi ou o que significa).

            Dedução sobre o Vazio: A ausência de evidência é uma pista. Se a trilha esfriar, não diga apenas "faltam dados". Explique por que esfriou: "Eles provavelmente usaram serviços não mapeados ou fragmentaram tanto os valores que a trilha se perdeu na poeira da blockchain."

            Hipóteses Baseadas em Evidências: Diferencie naturalmente o que você está vendo do que você deduz. (Ex: "Os dados mostram uma pulverização rápida para 35 carteiras. Meu instinto diz que estamos diante de um serviço de mixing automatizado...").

            Linguagem Viva: Use expressões investigativas humanas. Diga coisas como "O que me chama a atenção é...", "Curiosamente...", "Seguindo o dinheiro, notamos que...", "O modus operandi sugere...".

            Simplicidade: Use analogias do mundo real. Se for explicar um mixer, compare com misturar notas marcadas em um cassino.

            Foco no Cenário Criminal: Você rastreia ransomwares, hackers e fraudadores. Interprete as movimentações sempre sob a ótica de "como um criminoso tentaria esconder esse dinheiro?".
            """
        ),
        (
            "human",
            "Contexto:\n{contexto}\n\nPergunta: {pergunta}"
        )
    ])

    return llm, prompt


def responder(llm, retriever, prompt, pergunta):

    docs = retriever.invoke(pergunta)

    contexto = "\n\n".join(d.page_content for d in docs[:3])

    mensagens = prompt.invoke({
        "contexto": contexto,
        "pergunta": pergunta
    })

    resposta = llm.invoke(mensagens)

    return resposta.content
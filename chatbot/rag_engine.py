import os
from django.conf import settings
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")

#  using huggingface small embedding
EMBEDDINGS = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

# using CHROMa vectore database for store embedding

def get_vectorstore():
    return Chroma(
        persist_directory=str(settings.CHROMA_PERSIST_DIR),
        embedding_function=EMBEDDINGS,
    )



def ingest_text(text: str, metadata: dict) -> int:
    """Split text into chunks, embed, and store. Returns chunk count."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk, metadata=metadata) for chunk in chunks]

    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)
    vectorstore.persist()
    return len(chunks)


def ingest_pdf(file_path: str, metadata: dict) -> int:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(pages)
    for chunk in chunks:
        chunk.metadata.update(metadata)

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    return len(chunks)


def answer_query(query: str, user_id: int, k: int = 4) -> dict:
    """Retrieve relevant chunks and generate an answer, scoped to the user's own documents."""
    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(
        search_kwargs={'k': k, 'filter': {'user_id': user_id}}
    )
    relevant_docs = retriever.invoke(query)

    if not relevant_docs:
        return {
            "answer": "I don't have any relevant documents to answer that yet — try uploading some first.",
            "sources": []
        }

    context = "\n\n".join(doc.page_content for doc in relevant_docs)
    llm = ChatGroq(model="openai/gpt-oss-120b",
                   temperature=0,
                    groq_api_key=api_key)

    prompt = f"""Answer the question using ONLY the context below. If the answer isn't in the context, say so.

Context:
{context}

Question: {query}

Answer:"""

    response = llm.invoke(prompt)

    sources = [
        {"title": doc.metadata.get("title", "Unknown"), "snippet": doc.page_content[:200]}
        for doc in relevant_docs
    ]
    return {"answer": response.content, "sources": sources}
import os
from django.conf import settings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document as LangchainDocument

EMBEDDINGS = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)


def get_vectorstore():
    return Chroma(
        persist_directory=str(settings.CHROMA_PERSIST_DIR),
        embedding_function=EMBEDDINGS,
    )


def ingest_text(text: str, metadata: dict) -> int:
    """Split text into chunks, embed, and store. Returns chunk count."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(text)
    docs = [LangchainDocument(page_content=chunk, metadata=metadata) for chunk in chunks]

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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

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
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()


def _build_context(news_by_topic):
    docs = []
    for topic, articles in news_by_topic.items():
        for article in articles:
            text = f"Title: {article['title']}\n{article['body']}"
            docs.append(Document(
                page_content=text,
                metadata={"topic": topic, "title": article["title"]},
            ))
    return docs


def generate_script(news_by_topic, model="qwen/qwen3.8-27b"):
    docs = _build_context(news_by_topic)
    if not docs:
        return "No news found for the selected topics. Try different topics or check back later."

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": len(chunks)})

    llm = ChatGroq(
        model=model,
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
    )

    prompt = PromptTemplate(
        input_variables=["context"],
        template=(
            "You are a news podcast script writer. Based on the following news articles, "
            "write a natural, engaging podcast script. Group articles by topic. "
            "Start with a welcome intro and end with a closing remark.\n\n"
            "Articles:\n{context}\n\nPodcast Script:"
        ),
    )

    chain = RetrievalQA.from_llm(
        llm=llm,
        retriever=retriever,
        prompt=prompt,
    )
    result = chain.invoke({"query": "Write a podcast script summarizing these news articles."})

    vectorstore.delete_collection()

    return result["result"]

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()


def _build_context(news_by_topic):
    lines = []
    for topic, articles in news_by_topic.items():
        for article in articles:
            lines.append(
                f"[{topic}] {article['title']}\n{article['body']}"
            )
    return "\n\n".join(lines)


def generate_script(news_by_topic, model="qwen/qwen3.8-27b"):
    context = _build_context(news_by_topic)
    if not context.strip():
        return "No news found for the selected topics. Try different topics or check back later."

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

    chain = prompt | llm
    result = chain.invoke({"context": context})

    return result.content

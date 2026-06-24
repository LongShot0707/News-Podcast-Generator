import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.news_service import search_news
from services.script_generator import generate_script
from services.tts_service import text_to_speech

app = FastAPI()

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

PREDEFINED_TOPICS = [
    "Technology", "Sports", "Politics", "Science",
    "Health", "Business", "Entertainment", "World News",
    "Local News",
]

COUNTRIES = {
    "Worldwide": "wt-wt",
    "USA": "us-en",
    "England": "gb-en",
    "Canada": "ca-en",
    "Australia": "au-en",
    "India": "in-en",
    "Nepal": "np-en",
    "Japan": "jp-jp",
    "South Korea": "kr-kr",
    "Philippines": "ph-en",
    "China": "cn-en",
}

TIMELIMITS = {
    "Hot": None,
    "Last Week": "w",
    "Last Month": "m",
    "Last Year": "y",
}

GROQ_MODELS: dict[str, str] = {
    "Llama 3.3 70B": "llama-3.3-70b-versatile",
    "Llama 3.1 8B": "llama-3.1-8b-instant",
    "Llama 4 Scout 17B": "meta-llama/llama-4-scout-17b-16e-instruct",
    "Qwen 3 32B": "qwen/qwen3-32b",
}


class FetchNewsRequest(BaseModel):
    topics: list[str]
    country: str = "USA"
    timelimit: str = "Last Week"


class GenerateScriptRequest(BaseModel):
    articles_by_topic: dict[str, list[dict]]
    model: str = "llama-3.3-70b-versatile"


class GenerateAudioRequest(BaseModel):
    script: str
    voice: str = "female"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "topics": PREDEFINED_TOPICS,
            "countries": list(COUNTRIES.keys()),
            "timelimits": list(TIMELIMITS.keys()),
            "models": GROQ_MODELS,
        },
    )


@app.post("/fetch-news")
def fetch_news(data: FetchNewsRequest):
    if not data.topics:
        return JSONResponse({"error": "Select at least one topic"}, status_code=400)

    region = COUNTRIES.get(data.country, "us-en")
    timelimit = TIMELIMITS.get(data.timelimit, "w")

    resolved_topics = [
        data.country if t == "Local News" else t
        for t in data.topics
    ]

    news_by_topic = search_news(resolved_topics, region=region, timelimit=timelimit)

    return {
        "articles_by_topic": news_by_topic,
        "topics_found": {
            t: len(articles)
            for t, articles in news_by_topic.items()
        },
    }

@app.post("/generate-script")
def generate_script_endpoint(data: GenerateScriptRequest):
    if not data.articles_by_topic:
        return JSONResponse({"error": "No articles to generate script from"}, status_code=400)

    script = generate_script(data.articles_by_topic, model=data.model)
    return {"script": script}


@app.post("/generate-audio")
def generate_audio(data: GenerateAudioRequest):
    if not data.script:
        return JSONResponse({"error": "No script to convert to audio"}, status_code=400)

    audio_filename = asyncio.run(text_to_speech(data.script, voice=data.voice))
    return {"audio_url": f"/static/audio/{audio_filename}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

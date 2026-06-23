# News Podcast Generator

A local web app that automatically generates news podcasts, select topics, review sources, generate an AI-written script, and convert it to speech all from a single browser interface. Runs entirely on free tools, no cloud subscription required.

## Features

- **4-step pipeline:** Topic selection → Source review → AI script generation → Text-to-speech audio
- **Customizable:** 11 countries, 4 timelines, 4 AI models (Groq), 2 voices (male/female)
- **Live search:** Fetches fresh news from DuckDuckGo for any topic
- **Responsive UI:** Works on PC and phone via Bootstrap 5
- **LAN accessible:** Any device on the same network can use it
- **Content creator ready:** Produces a downloadable MP3 podcast in under 5 minutes

## Tech Stack

| Component | Tool |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Bootstrap 5 + Vanilla JS |
| News Search | DuckDuckGo (ddgs) |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace) |
| Vector Store | ChromaDB  |
| LLM | Groq (llama-3.3-70b, qwen3-32b, etc.) |
| TTS | edge-tts (Microsoft Edge neural voices) |

## Architecture

```
Browser → 4-Step SPA
              │
    ┌─────────┼─────────┐
    │         │         │
POST /    POST /    POST /
fetch-news generate- generate-
           script    audio
    │         │         │
[News      [RAG +    [edge-tts]
 Service]   Groq LLM]
            │
       [ChromaDB]
```

## How to Run

1. Clone the repo
2. Create `.env` with: `GROQ_API_KEY=gsk_your_key_here`
3. Install dependencies: `pip install -r requirements.txt`
4. Start: `uvicorn app:app --host 0.0.0.0 --port 5000`
5. Open `http://localhost:5000`

## Project Structure

```
├── app.py                      # FastAPI server (routes + orchestration)
├── services/
│   ├── news_service.py         # DuckDuckGo search with fallback logic
│   ├── script_generator.py     # ChromaDB + Groq LLM pipeline
│   └── tts_service.py          # edge-tts audio generation
├── templates/
│   └── index.html              # 4-step SPA frontend
├── static/audio/               # Generated MP3 files
├── docs/                       # Design docs & presentation notes
└── .env                        # API key (excluded from git)
```

## Team Roles

| Member | File | Responsibility |
|---|---|---|
| 1 | `app.py` | Server setup, endpoints, pipeline orchestration |
| 2 | `services/news_service.py` | News search via DuckDuckGo, 4-tier fallback |
| 3 | `services/script_generator.py` | RAG pipeline, Groq LLM script generation |
| 4 | `services/tts_service.py` | edge-tts text-to-speech, audio generation |
| 5 | `templates/index.html` | 4-step SPA, Bootstrap UI, JavaScript state |

## Limitations

- Requires internet (DuckDuckGo, Groq API, edge-tts all online)
- English-only voices and models
- No persistent database — state resets on page refresh
- Free Groq API key must be refreshed periodically (expires)

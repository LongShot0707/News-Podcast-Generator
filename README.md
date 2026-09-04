# News Podcast Generator

A local web app that automatically generates news podcasts — select topics, review sources, generate an AI-written script, and convert it to speech — all from a single browser interface. Runs entirely on free tools, no cloud subscription required.

## Features

- **4-step pipeline:** Topic selection → Source review → AI script generation → Text-to-speech audio
- **Customizable:** 11 countries, 4 timelines, 5 AI models (Groq), 2 voices (male/female)
- **Live search:** Fetches fresh news from DuckDuckGo for any topic
- **Responsive UI:** Works on PC and phone via Bootstrap 5
- **Containerized:** Ships with a `Dockerfile` + `docker-compose.yml` for a single-container homelab deployment
- **LAN/Tailscale accessible:** Any device on the same network (or tailnet) can use it
- **Content creator ready:** Produces a downloadable MP3 podcast in under 5 minutes

## Tech Stack

| Component | Tool |
|---|---|
| Backend | FastAPI (Python) |
| Frontend | Bootstrap 5 + Vanilla JS |
| News Search | DuckDuckGo (ddgs) |
| LLM | Groq (Qwen 3.6/3.8, OpenAI GPT-OSS, Groq Compound) |
| TTS | edge-tts (Microsoft Edge neural voices) |

> **Note on embeddings/vector search:** The original version used a RAG pipeline
> (ChromiaDB + `all-MiniLM-L6-v2` + `sentence-transformers`). These were removed in favor
> of sending the fetched articles directly to the Groq LLM for script generation. This
> keeps the app working on older hardware (no AVX2 / no PyTorch) and drastically reduces
> memory and image size. See "Compatibility" below.

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
[DuckDuckGo] [Groq   [edge-tts]
             LLM]
```

## How to Run (development, without Docker)

1. Clone the repo
2. Create `.env` with: `GROQ_API_KEY=gsk_your_key_here`
3. Set up a virtual environment (Python 3.11 recommended):

   ```bash
   uv venv --python 3.11
   uv pip install -r requirements.txt
   ```

4. Start:

   ```bash
   uv run uvicorn app:app --host 0.0.0.0 --port 5000
   ```

5. Open `http://localhost:5000`

## How to Run (Docker / homelab deployment)

The project includes a `Dockerfile` and `docker-compose.yml` for a single-container deployment.

1. Clone the repo onto the host
2. Create `.env` with: `GROQ_API_KEY=gsk_your_key_here`
3. Build and start:

   ```bash
   docker compose build
   docker compose up -d
   ```

4. Open `http://<host-ip>:5000`

**Key configuration (`docker-compose.yml`):**
- `ports: "5000:5000"` — exposes the app
- `env_file: .env` — injects `GROQ_API_KEY` at runtime (secrets are never baked into the image)
- `restart: unless-stopped` — automatic restart on crash/boot
- `mem_limit: 1g` — caps memory (works on small/old hosts)
- `volumes: podcast-audio:/app/static/audio` — persists generated MP3s across restarts

**Security:** `.env` is excluded via both `.gitignore` and `.dockerignore`, so the API key stays out of git history and image layers.

## Model Configuration

Available Groq models (in `app.py` `GROQ_MODELS`):

| Label | Model ID |
|---|---|
| Qwen 3.6 27B | `qwen/qwen3.6-27b` |
| Qwen 3.8 27B | `qwen/qwen3.8-27b` |
| OpenAI GPT-OSS 120B | `openai/gpt-oss-120b` |
| OpenAI GPT-OSS 20B | `openai/gpt-oss-20b` |
| Groq Compound | `groq/compound` |

> **Note:** Groq model IDs change over time. Older IDs (e.g. `llama-3.3-70b-versatile`,
> `meta-llama/llama-4-scout-17b-16e-instruct`) may return `404 model_not_found`. If you get
> a 404, query <https://console.groq.com/keys> or the `/models` endpoint to see current
> model IDs and update `GROQ_MODELS`.

## Project Structure

```
├── app.py                      # FastAPI server (routes + orchestration)
├── services/
│   ├── news_service.py         # DuckDuckGo search with fallback logic
│   ├── script_generator.py     # Groq LLM script generation (lightweight, no torch)
│   └── tts_service.py          # edge-tts audio generation
├── templates/
│   └── index.html              # 4-step SPA frontend
├── static/audio/               # Generated MP3 files (volume-mounted in Docker)
├── Dockerfile                  # Image recipe (python:3.11-slim)
├── docker-compose.yml          # Single-container orchestration
└── .env                        # API key (excluded from git & image)
```

## Compatibility & the AVX/PyTorch lesson

The server this runs on is an older x86-64 CPU (Intel Pentium Dual-Core T4200, no AVX2).
PyTorch / `sentence-transformers` / `chromadb` ship native binaries compiled for modern
CPUs and crash with **SIGILL (exit code 132)** on CPUs without AVX2.

The fix was to remove the vector-database RAG entirely and pass the (small) set of fetched
articles directly to the Groq LLM. This:
- Removes the native-ML dependency crash (SIGILL) on old hardware
- Cuts image size and memory use significantly
- Keeps identical observable behavior (Groq writes the script from the articles)

If you want to restore embeddings/vector search, you must run on a CPU with AVX2 (any CPU
from ~2013 onward) and re-add the removed requirements.

## Limitations

- Requires internet (DuckDuckGo, Groq API, edge-tts all online)
- English-only voices and models
- No persistent database — state resets on page refresh
- Free Groq API key must be refreshed periodically (expires after inactivity)

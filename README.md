# GEN_AI_Tasks

Three AI automation tasks built for the internship assignment.

---

## Setup (All Tasks)

```bash
# 1. Clone / open the project in VS Code
# 2. Copy .env.example to .env and add your API keys
cp .env.example .env

# 3. Install dependencies per task
cd Task1/code && pip install -r requirements.txt
cd Task2/code && pip install -r requirements.txt
cd Task3/code && pip install -r requirements.txt
```

---

## Task 1 — AI Video Generation Tool

**Pipeline:** Trending news → AI script → MP4 video with text overlays

```bash
cd Task1/code
python main.py
```

**Outputs:** `Task1/outputs/assets/automated_video.mp4`

**API Keys needed:**
- `OPENAI_API_KEY` — script generation
- `NEWSAPI_KEY` — trending news (optional, falls back to mock data)
- `PEXELS_API_KEY` — background images (optional, falls back to gradients)

---

## Task 2 — SEO Blog Post Creation Tool

**Pipeline:** Amazon product scraping → SEO keyword research → AI blog post → `.md` files

```bash
cd Task2/code
python main.py
```

**Outputs:** `Task2/outputs/blog_post_1.md`, `blog_post_2.md`

**API Keys needed:**
- `OPENAI_API_KEY` — keyword research + blog writing

---

## Task 3 — High-Level to Low-Level Architecture Pipeline

**Pipeline:** Business requirement → Module design → DB schemas → Pseudocode → API spec → `technical_spec.md`

```bash
cd Task3/code
# Use the built-in sample requirement:
python main.py

# Or pass your own requirement:
python main.py "Build a hospital appointment booking system with patient records"
```

**Outputs:** `Task3/outputs/technical_spec.md`

**API Keys needed:**
- `OPENAI_API_KEY` — all AI-powered generation steps (all steps have rule-based fallbacks)

---

## Project Structure

```
GEN_AI_Tasks/
├── .env.example
├── README.md
├── Task1/
│   ├── code/
│   │   ├── main.py              # Pipeline entry point
│   │   ├── scraper.py           # NewsAPI trending article fetcher
│   │   ├── script_generator.py  # GPT-4o-mini script writer
│   │   ├── video_generator.py   # MoviePy video builder
│   │   └── requirements.txt
│   └── outputs/
│       └── assets/
│           └── automated_video.mp4
├── Task2/
│   ├── code/
│   │   ├── main.py              # Pipeline entry point
│   │   ├── scraper.py           # Amazon BeautifulSoup scraper
│   │   ├── seo_keywords.py      # AI + rule-based keyword research
│   │   ├── blog_generator.py    # GPT-4o-mini blog writer
│   │   └── requirements.txt
│   └── outputs/
│       ├── blog_post_1.md
│       └── blog_post_2.md
└── Task3/
    ├── code/
    │   ├── main.py              # Pipeline entry point + spec writer
    │   ├── analyzer.py          # Requirement → entities/features
    │   ├── module_generator.py  # Entities → system modules
    │   ├── schema_generator.py  # Modules → DB schemas
    │   ├── pseudocode_gen.py    # Modules → pseudocode
    │   ├── api_generator.py     # Modules → REST API spec
    │   └── requirements.txt
    └── outputs/
        └── technical_spec.md
```

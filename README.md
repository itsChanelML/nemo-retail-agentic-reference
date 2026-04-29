<div align="center">

<br/>

```
 ██████╗██╗  ██╗ ██████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗██████╗
██╔════╝██║  ██║██╔═══██╗██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗
╚█████╗ ███████║██║   ██║██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ██║
 ╚═══██╗██╔══██║██║   ██║██╔═══╝ ██║╚██╔╝██║██║██║╚██╗██║██║  ██║
██████╔╝██║  ██║╚██████╔╝██║     ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
```

**Agentic Retail AI · Powered by NVIDIA Nemotron**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![LangChain](https://img.shields.io/badge/LangChain-ReAct-1C3C3C?style=flat-square)](https://langchain.com)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20%7C%20Nemotron-76b900?style=flat-square&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)

<br/>

*A production-grade reference implementation showing how AI-native retail startups can integrate NVIDIA's Nemotron models with open-source RAG infrastructure — grounded answers, cited sources, agentic reasoning.*

<br/>

</div>

---

## What This Is

ShopMind is a conversational retail agent that answers questions like:

> *"Best noise-canceling headphones under $250 for gym use"*
> *"Compare Sony vs Bose for a frequent flyer"*
> *"I need a pro laptop for ML engineering under $2K"*

...and returns **grounded, cited product recommendations** backed by a multi-stage retrieval pipeline — not hallucinated guesses.

The agent uses a LangChain ReAct loop to decide which tool to invoke (semantic search, structured filtering, or cross-encoder reranking), synthesizes results through **NVIDIA Nemotron** via NIM, and streams its reasoning chain in real time. Every answer cites the specific product documents it retrieved.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Query                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              LangChain ReAct Agent (Orchestrator)               │
│         Reasons → selects tool → observes → iterates           │
└────────────┬──────────────────┬──────────────────┬─────────────┘
             │                  │                  │
             ▼                  ▼                  ▼
    ┌─────────────┐    ┌──────────────┐   ┌──────────────────┐
    │RAG Retriever│    │Product Filter│   │  Cross-Encoder   │
    │             │    │              │   │    Re-Ranker      │
    │ FAISS dense │    │ Price, brand │   │                  │
    │  (60% wt)  │    │ category,    │   │ms-marco-MiniLM   │
    │ BM25 sparse │    │ rating, stock│   │  precision pass  │
    │  (40% wt)  │    └──────────────┘   └──────────────────┘
    │             │
    │ HuggingFace │
    │all-MiniLM   │
    │   -L6-v2    │
    └─────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│        nvidia/nemotron-mini-4b-instruct  (via NVIDIA NIM)       │
│              OpenAI-compatible endpoint · streaming             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
              Grounded recommendation + cited sources
```

**Stack at a glance:**

| Layer | Technology |
|---|---|
| Agent orchestration | LangChain ReAct (`create_react_agent`) |
| Retrieval — dense | FAISS + HuggingFace `sentence-transformers/all-MiniLM-L6-v2` |
| Retrieval — sparse | BM25 (`rank-bm25`) |
| Hybrid fusion | LangChain `EnsembleRetriever` (60/40 weights) |
| Re-ranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Generation | `nvidia/nemotron-mini-4b-instruct` via NVIDIA NIM |
| API | FastAPI + SSE streaming |
| Frontend | Next.js 14 + Tailwind + Framer Motion |
| Deployment | Vercel (monorepo) |
| Evaluation | RAGAS (faithfulness · answer relevancy · context recall) |

---

## Why Each Technical Choice Was Made

**Hybrid retrieval (FAISS + BM25)** — Dense embeddings capture semantic intent ("comfortable headphones for long flights") while BM25 catches exact-match queries ("WH-1000XM5"). Running both with ensemble fusion gives best-of-both-worlds recall before the precision pass.

**Two-stage retrieve → rerank** — Bi-encoder retrieval is fast but approximate. The cross-encoder reranker scores (query, document) pairs directly, recovering precision that the embedding shortlist misses. This mirrors production RAG architectures at scale.

**Nemotron via NIM** — NVIDIA Inference Microservices expose an OpenAI-compatible endpoint, meaning Nemotron is a drop-in for any GPT-4 workflow. Startups can migrate to NVIDIA's stack with a one-line model string change — exactly the adoption pattern this role drives.

**LangChain ReAct agent** — The Reasoning + Acting loop lets the agent dynamically choose tools based on query structure: open-ended queries route to RAG, structured constraints route to the filter, ambiguous multi-candidate results route to the reranker. This is the agentic pattern NeMo Agent Toolkit formalizes.

**SSE streaming** — Surfacing agent steps in real time reduces perceived latency and makes the reasoning chain transparent to end users — both a UX win and a trust signal for enterprise retail deployments.

---

## Quickstart

### Prerequisites

- Python 3.11+
- Node.js 18+
- An [NVIDIA NIM API key](https://build.nvidia.com) (free tier available)

### 1. Clone and configure

```bash
git clone https://github.com/your-username/shopmind.git
cd shopmind
cp .env.example .env
```

Edit `.env`:
```bash
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Get your NVIDIA API key

1. Visit [build.nvidia.com](https://build.nvidia.com)
2. Log in → navigate to **Nemotron Mini 4B**
3. Click **API** → copy your key
4. Free tier includes generous inference credits

### 3. Run the API

```bash
cd api
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # First run downloads ~90MB of HF models
uvicorn main:app --reload --port 8000
```

Verify it's running:
```bash
curl http://localhost:8000/api/health
# → {"status": "ok", "agent_ready": true}
```

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## Deployment to Vercel

### Option A — CLI (fastest)

```bash
npm install -g vercel
vercel --prod
```

### Option B — GitHub integration

1. Push to GitHub
2. Go to [vercel.com/new](https://vercel.com/new) → import repository
3. Set root directory to `.`
4. Add environment variables (see below)
5. Deploy

### Required environment variables

| Variable | Where to set | Value |
|---|---|---|
| `NVIDIA_API_KEY` | Vercel dashboard → Settings → Environment Variables | `nvapi-...` |
| `NEXT_PUBLIC_API_URL` | Vercel dashboard | Leave empty — rewrites handle routing |

> **Production note:** Vercel serverless functions support Python up to 50MB and cache HuggingFace models between invocations. For high-throughput production use, deploy the FastAPI backend to a GPU-enabled host (GCP Cloud Run, AWS ECS, or NVIDIA-hosted infrastructure) and point `NEXT_PUBLIC_API_URL` at it. Swap `faiss-cpu` → `faiss-gpu` to leverage CUDA acceleration.

---

## API Reference

```
POST /api/query
```
```json
{
  "query": "Best smartwatch for marathon training",
  "session_id": "user_abc123",
  "stream": false
}
```

Returns:
```json
{
  "answer": "For marathon training, the Garmin Fenix 7X Solar...",
  "sources": [{"sku": "SW-003", "name": "Garmin Fenix 7X Solar"}],
  "products": [{ "sku": "SW-003", "name": "...", "price": 749.99, ... }],
  "agent_steps": ["RAGRetriever: smartwatch marathon...", "ReRanker: ..."],
  "model": "nvidia/nemotron-mini-4b-instruct",
  "retrieval_score": 0.87
}
```

```
POST /api/query/stream   → text/event-stream (SSE)
GET  /api/health
DELETE /api/session/{session_id}
```

---

## Evaluation

Run the RAGAS evaluation harness to score the full RAG pipeline:

```bash
pip install ragas datasets
python scripts/eval.py
```

Outputs faithfulness, answer relevancy, and context recall scores against a curated ground-truth test set. Scores above 0.80 indicate production-ready retrieval quality.

---

## Extending the Demo

**Add your own products** — edit `api/products.py`. Each entry is a dict; the `description` field is what gets embedded and retrieved.

**Connect a real database** — replace the `PRODUCT_CATALOG` import in `agent.py` with any database connector.

**Upgrade the model** — swap one line in `agent.py`:
```python
# From:
model="nvidia/nemotron-mini-4b-instruct"
# To:
model="nvidia/llama-3.1-nemotron-70b-instruct"
```

**Self-host with NeMo Microservices** — replace the NIM API endpoint with your self-hosted NeMo deployment. The OpenAI-compatible interface means zero code changes beyond the `openai_api_base` URL.

**Enable GPU acceleration** — on a CUDA-enabled host:
```bash
pip uninstall faiss-cpu && pip install faiss-gpu
```

---

## NVIDIA Stack Alignment

| ShopMind Component | Maps to NVIDIA Technology |
|---|---|
| Nemotron via NIM API | Nemotron models · NVIDIA NIM |
| Self-hosted NeMo endpoint | NeMo Microservices |
| LangChain ReAct agent | NeMo Agent Toolkit patterns |
| FAISS-GPU (GPU host) | CUDA-accelerated pipelines |
| NIM inference layer | NVIDIA Dynamo |

---

## Project Structure

```
shopmind/
├── api/
│   ├── main.py          # FastAPI app · /query · /query/stream · /health
│   ├── agent.py         # LangChain ReAct agent · Nemotron LLM · 3 tools
│   ├── retriever.py     # Hybrid FAISS+BM25 retrieval · cross-encoder rerank
│   ├── products.py      # 45-product seed catalog (replace with your DB)
│   ├── index.py         # Vercel Python serverless entry point
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx   # Font setup · metadata
│   │   ├── page.tsx     # Chat interface · SSE streaming · session memory
│   │   └── globals.css  # Design system · NVIDIA green palette · animations
│   └── components/
│       ├── ProductCard.tsx   # Product result card with rating + stock
│       ├── AgentSteps.tsx    # Collapsible reasoning chain trace
│       └── SystemBadge.tsx   # Live API health indicator
├── scripts/
│   └── eval.py          # RAGAS evaluation harness
├── vercel.json          # Monorepo deployment config
└── .env.example
```

---

## Built by

**Chanel Power**
Founder & CEO, Mentor Me Collective · Senior ML Engineer · Technical Startup Advisor · NVIDIA Certified Builder · Google Certified Generative AI Leader

[LinkedIn](https://linkedin.com/in/powerc1) · [@itsChanelML](https://linktr.ee/itsChanelML)

> *Real skills. Real careers. Master Differently.*

---

<div align="center">

Built to demonstrate agentic AI integration on NVIDIA's stack —<br/>
the same pattern retail startups need to ship production AI at scale.

</div>
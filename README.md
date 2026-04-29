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

ShopMind is a reference implementation of the intelligent product discovery system a retail brand like Best Buy would deploy for in-store sales specialists. It gives a specialist a way to take a customer's natural language request and return a cited, stock-aware recommendation in seconds. 

No more manually searching terminals and guessing. The system knows what is in stock, what is on sale, and which store carries it. It is powered by NVIDIA Nemotron and a hybrid RAG pipeline that understands the difference between "noise-canceling headphones for the gym" and "WH-1000XM5."


</div>

---

## What This Is

ShopMind is a conversational retail agent that answers natural language shopping queries like:

> *"Best noise-canceling headphones under $250 for gym use"*
> *"Show me 65-inch TVs available at Best Buy right now"*
> *"What laptops with 32GB RAM are on sale?"*
> *"Compare Sony and LG OLED TVs"*
> *"I need a robot vacuum under $500 — what's in stock?"*

Every answer is **grounded in retrieved product data**, reasoned through by **NVIDIA Nemotron**, and returned with **cited SKUs**, **live stock status**, **sale pricing**, and **store availability**. The full reasoning chain streams to the user in real time.

---

## Agent Reasoning — How It Works

ShopMind uses a LangChain **ReAct** (Reasoning + Acting) loop. For every query the agent:

1. **Thinks** — determines what the user needs and which tool to call
2. **Acts** — calls one of three specialized tools
3. **Observes** — reads the tool output
4. **Repeats** — iterates until it has enough to answer confidently
5. **Responds** — synthesizes a grounded answer through Nemotron with product citations

### The Three Tools

**RAG Retriever** — semantic + keyword hybrid search. Uses FAISS dense embeddings (60%) combined with BM25 sparse retrieval (40%). Catches both "comfortable headphones for long flights" (semantic) and "WH-1000XM5" (exact keyword).

**Product Filter** — structured attribute filtering for constrained queries. Supports `category`, `max_price`, `min_price`, `min_rating`, `brand`, `in_stock`, `on_sale`, `store`, `keyword`. Uses sale price for budget queries so a product on sale for $199 correctly appears in a "under $200" search.

**Cross-Encoder ReRanker** — precision pass using `cross-encoder/ms-marco-MiniLM-L-6-v2`. Scores (query, product) pairs directly to find the best match from the retrieval shortlist.

### Example Reasoning Trace

```
User: "Best TV under $1000 available at Target"

Thought: User wants a TV, max_price=1000, store=Target, in_stock=true. Filter first.
Action: ProductFilter
Input: category=televisions, max_price=1000, store=Target, in_stock=true
Observation: [TV-001] LG OLED C3 65" — $999.99 sale | Target ✓
             [TV-004] Hisense QLED Q6 65" — $449.99 sale | Target ✓
             [TV-005] Hisense U8K Mini-LED 65" — $697.99 sale | Target ✓

Thought: Good candidates. Rerank to find the best match.
Action: ReRanker
Input: best TV under 1000 Target | TV-001, TV-004, TV-005
Observation: 1. TV-001 LG OLED C3 (score: 0.94)  2. TV-005 Hisense U8K (score: 0.81)

Final Answer: For under $1000 at Target, the LG OLED C3 65" at $999.99 is the
standout — OLED self-lit pixels deliver perfect blacks no LCD can match at this
price. For budget headroom, the Hisense U8K Mini-LED at $697.99 is the best LCD
alternative with 1500 local dimming zones.
Sources: TV-001, TV-005
```

---

## Product Data — Synthetic Retail Catalog

The catalog is modeled after a Best Buy-style consumer electronics inventory. It lives in `data/products.csv`, loads at startup, embeds into FAISS, and drives all retrieval and filtering.

### Catalog Overview — 50 Products, 10 Categories, 5 Brands Each

| Category | Brands | Price Range | Notes |
|---|---|---|---|
| Televisions | LG, Samsung, Sony, Hisense (×2) | $449 – $1,800 | 65" across all, varying panel tech |
| Cameras | Sony, Canon, Fujifilm, Nikon, OM System | $799 – $2,499 | Fujifilm X100VI intentionally out of stock |
| Vacuums | Dyson, iRobot, Shark, Bissell, Tineco | $69 – $899 | Robot, upright, cordless, wet-dry |
| Laptops | Apple, Dell, Lenovo, ASUS, Acer | $349 – $1,999 | M3 Pro to budget Chromebook |
| Headphones | Sony, Bose, Sennheiser, Jabra, Anker | $59 – $449 | Consumer to enterprise |
| Phones | Apple (×2), Samsung, Google, OnePlus | $699 – $1,299 | iPhone 15 and 15 Pro both included |
| Monitors | Dell, Samsung, LG, ASUS, Gigabyte | $329 – $1,499 | 27" and 49" ultrawide OLED |
| Tablets | Apple, Samsung, Google, Lenovo, Amazon | $139 – $1,099 | iPad Pro to Fire HD 10 |
| Smartwatches | Apple, Samsung, Garmin (×2), Fitbit | $149 – $749 | Solar, sport, fitness, enterprise |
| Speakers | Sonos, Apple, JBL, Bang & Olufsen, Samsung | $149 – $1,499 | Portable to 11.1.4ch soundbar |

### CSV Schema — Every Field Explained

```
sku                  Unique identifier (e.g. TV-001, LAP-003, HP-005)
name                 Full product name including key specs
brand                Manufacturer / brand name
category             Product category in lowercase (e.g. televisions, laptops)
price                Regular retail price in USD
sale_price           Current promotional price (empty string if not on sale)
rating               Customer review average on 0–5 scale
review_count         Total number of customer reviews
in_stock             true or false
stock_quantity       Units currently available (0 if out of stock)
store_availability   Pipe-separated retailer list: Best Buy|Target|Amazon|B&H|Walmart
description          Rich embedding-ready paragraph covering features, use cases,
                     differentiators, and target audience — this is the primary
                     field used for semantic retrieval
display_size         Screen diagonal in inches (TVs, laptops, monitors, tablets, phones)
resolution           Display resolution and panel type (e.g. 4K OLED, 3024x1964 Liquid Retina XDR)
processor            CPU/chip (e.g. Apple M3 Pro, Intel Core i7-13700H, Snapdragon 8 Gen 3)
ram                  Memory spec (e.g. 18GB unified, 32GB DDR5)
storage              Storage spec (e.g. 512GB SSD, 1TB NVMe)
battery_life         Manufacturer-rated battery hours
weight               Product weight in grams or kilograms
color                Primary color / finish
model_number         Official manufacturer part number
warranty_years       Warranty length in years
```

### Intentional Data Design Decisions

**Sale prices on ~60% of products** — mirrors real retailer promotional cadence. The product filter uses `sale_price` when available for budget queries, so a TV on sale for $999 correctly surfaces in a "under $1000" search even if its regular price is $1,299.

**Store availability varies by product** — premium products like Bang & Olufsen and B&H-exclusive cameras aren't available everywhere. Queries like "available at Walmart" or "in stock at B&H" correctly scope results.

**One intentional out-of-stock** — Fujifilm X100VI (`CAM-003`, `stock_quantity=0`) mirrors the real-world situation where this camera has been perpetually backordered since launch. The agent correctly flags this and recommends in-stock alternatives.

**Spec fields enriched into descriptions** — `csv_loader.py` builds the embedding description by combining the base description with all spec fields. This enables retrieval on spec-level queries: "laptop with 32GB RAM", "TV with HDMI 2.1 for PS5", "camera under 500g" — without requiring exact keyword matches.

**Review counts reflect realistic distribution** — from 543 (Bang & Olufsen Beosound A5) to 12,432 (iPhone 15 Pro), mimicking how popularity varies across premium and mass-market products.

**Five brands per category** — ensures no single brand dominates retrieval. Comparison queries ("Sony vs LG OLED", "Dyson vs iRobot") always have both sides represented.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Query                            │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│           LangChain ReAct Agent (Orchestrator)               │
│      Reasons → selects tool → observes → iterates           │
└───────────┬─────────────────┬──────────────────┬────────────┘
            │                 │                  │
            ▼                 ▼                  ▼
   ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐
   │RAG Retriever │  │Product Filter│  │  ReRanker       │
   │              │  │              │  │                 │
   │ FAISS dense  │  │ price, brand,│  │cross-encoder/   │
   │   60% wt     │  │ category,    │  │ms-marco-MiniLM  │
   │ BM25 sparse  │  │ store, stock,│  │  precision pass │
   │   40% wt     │  │ on_sale      │  └─────────────────┘
   │              │  └──────────────┘
   │ HuggingFace  │
   │all-MiniLM-L6 │
   └──────────────┘
            │
            ▼
┌──────────────────────────────────────────────────────────────┐
│     nvidia/nemotron-mini-4b-instruct  (via NVIDIA NIM)       │
│       OpenAI-compatible endpoint · SSE streaming             │
└─────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
        Grounded answer + cited SKUs + store availability
                  + sale price + stock status
```

---

## What the Output Looks Like

Every ShopMind response includes:

**The answer** — grounded natural language from Nemotron citing specific SKUs and referencing retrieved specs. Never states information not present in the product data.

**Agent step trace** — collapsible panel showing which tools fired, what inputs were passed, and what was observed. Full transparency into the reasoning chain.

**Product cards** — one card per cited product showing brand, name, SKU, regular price, sale price (if applicable), star rating, review count, and stock status.

**Source citations** — SKU pills (e.g. `TV-001`, `HP-003`) showing exactly which product records grounded the answer.

**Model attribution** — `nvidia/nemotron-mini-4b-instruct` on every response.

---

## Quickstart

### Prerequisites
- Python 3.11+, Node.js 18+
- [NVIDIA NIM API key](https://build.nvidia.com) (free tier)

### 1. Clone and configure
```bash
git clone https://github.com/itsChanelML/nemo-retail-agentic-reference.git
cd nemo-retail-agentic-reference
cp .env.example .env
# Add your NVIDIA_API_KEY to .env
```

### 2. Run the API
```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Watch for:
```
CSV catalog loaded: 50 products from products.csv
ShopMind agent ready.
```

### 3. Run the frontend
```bash
cd frontend && npm install && npm run dev
# Open http://localhost:3000
```

---

## Try These Queries

```
Best 65-inch TV under $1000 at Target
Show me Sony cameras in stock
What laptops have 32GB RAM under $1500?
Compare Dyson and iRobot robot vacuums
Noise-canceling headphones for gym use under $300
What products are on sale right now?
Tablets available at Walmart under $200
Best smartwatch for marathon training
Monitors available at B&H Photo
Which camera is out of stock?
```

---

## Extending the Demo

**Add or edit products** — edit `data/products.csv`. The `description` column matters most for retrieval — write rich, specific descriptions including use cases, specs, and differentiators.

**Connect a live inventory feed** — replace `csv_loader.py` with a connector to your retail partner's API or database. Returns the same schema, nothing else changes.

**Enable Best Buy live data** — add `BESTBUY_API_KEY` to `.env`. Get a free key at [developer.bestbuy.com](https://developer.bestbuy.com) using a company email address.

**Upgrade the model:**
```python
model="nvidia/llama-3.1-nemotron-70b-instruct"
```

**Run the RAG evaluation harness:**
```bash
pip install ragas datasets
python scripts/eval.py
# Outputs: faithfulness, answer relevancy, context recall scores
```

---

## NVIDIA Stack Alignment

| ShopMind Component | NVIDIA Technology |
|---|---|
| Nemotron via NIM API | Nemotron models · NVIDIA NIM |
| NIM OpenAI endpoint | Drop-in for NeMo Microservices |
| LangChain ReAct agent | NeMo Agent Toolkit patterns |
| FAISS-GPU on CUDA host | CUDA-accelerated pipelines |
| NIM inference serving | NVIDIA Dynamo |

---

## Project Structure

```
nemo-retail-agentic-reference/
├── api/
│   ├── main.py                # FastAPI · /query · /query/stream · /health
│   ├── agent.py               # LangChain ReAct agent · Nemotron · 3 tools
│   ├── retriever.py           # FAISS+BM25 hybrid · cross-encoder · filters
│   ├── csv_loader.py          # CSV ingestion · description builder · normalization
│   ├── bestbuy_connector.py   # Best Buy API v1 connector (optional live data)
│   ├── products.py            # Fallback seed catalog (45 products)
│   ├── index.py               # Vercel Python entry point
│   └── requirements.txt
├── data/
│   └── products.csv           # 50-product synthetic retail catalog
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Chat UI · SSE streaming · session memory
│   │   └── globals.css        # NVIDIA green design system
│   └── components/
│       ├── ProductCard.tsx    # Product card · rating · stock · sale price
│       ├── AgentSteps.tsx     # Collapsible reasoning chain trace
│       └── SystemBadge.tsx    # Live API health indicator
├── scripts/
│   └── eval.py                # RAGAS evaluation harness
├── vercel.json
└── .env.example
```

## Built by

**Chanel Power**
Founder & CEO, Mentor Me Collective · Senior ML Engineer · Technical Startup Advisor · NVIDIA Certified Builder · Google Certified Generative AI Leader

[LinkedIn](https://linkedin.com/in/powerc1) · [@itsChanelML](https://linktr.ee/itsChanelML)


---

<div align="center">

Built to demonstrate agentic AI integration on NVIDIA's stack —<br/>
the same pattern retail startups need to ship production AI at scale.

</div>
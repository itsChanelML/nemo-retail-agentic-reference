"""
ShopMind Agent
LangChain ReAct agent with three tools:
  1. RAG Retriever — semantic product search via FAISS + HuggingFace embeddings
  2. Product Filter — structured attribute-based filtering
  3. Re-ranker — cross-encoder reranking for precision
NVIDIA Nemotron via NIM API is the generation backbone.
"""

import os
import json
import asyncio
from typing import AsyncIterator, Optional
from dataclasses import dataclass, field

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings          # langchain-huggingface >= 0.0.3
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document                     # moved to langchain-core

from retriever import ProductRetriever
from csv_loader import load_bestbuy_catalog

# ── Nemotron via NVIDIA NIM (OpenAI-compatible endpoint) ─────────────────────
def get_nemotron_llm() -> ChatOpenAI:
    """
    NVIDIA NIM exposes an OpenAI-compatible API.
    Pass NVIDIA_API_KEY in your .env — no OPENAI_API_KEY needed.
    """
    nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
    if not nvidia_key:
        raise ValueError(
            "NVIDIA_API_KEY is not set. "
            "Get a free key at https://build.nvidia.com and add to your .env."
        )
    return ChatOpenAI(
        model="nvidia/nemotron-mini-4b-instruct",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_key,
        temperature=0.3,
        max_tokens=1024,
        streaming=True,
    )


# ── Agent system prompt ───────────────────────────────────────────────────────
REACT_PROMPT = PromptTemplate.from_template("""
You are ShopMind, an expert retail AI assistant powered by NVIDIA Nemotron.
Your job is to help customers find the perfect product through grounded, cited recommendations.

RULES:
- Always use the RAG retriever first to ground your answer in real product data
- Use the product filter tool when the user specifies attributes (price, color, category)
- Use the re-ranker tool when you have multiple candidates and need the best match
- Cite specific products by name and SKU in your final answer
- Never hallucinate product specs — only state what the retrieved documents confirm
- Be concise, confident, and helpful

You have access to the following tools:
{tools}

Use this format:

Question: the input question
Thought: think step by step about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have enough information to answer
Final Answer: [your grounded recommendation with product citations]

Begin!

Chat History:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}
""")


@dataclass
class AgentSession:
    memory: ConversationBufferWindowMemory = field(
        default_factory=lambda: ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=False
        )
    )


class ShopMindAgent:
    def __init__(self):
        self.retriever: ProductRetriever = None
        self.llm = None
        self.sessions: dict[str, AgentSession] = {}
        self._initialized = False

    async def initialize(self):
        """Build vector store and initialize all components."""
        if self._initialized:
            return

        print("Loading product catalog (Etsy API or seed fallback)...")
        catalog = await load_bestbuy_catalog(fallback_to_seed=True)
        self._catalog = catalog

        print("Loading HuggingFace embeddings (all-MiniLM-L6-v2)...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        print(f"Building FAISS vector store from {len(catalog)} products...")
        docs = [
            Document(
                page_content=p["description"],
                metadata={k: v for k, v in p.items() if k != "description"}
            )
            for p in catalog
        ]

        faiss_store = FAISS.from_documents(docs, embeddings)
        dense_retriever = faiss_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 6}
        )

        # BM25 for hybrid retrieval (keyword matching)
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = 6

        # EnsembleRetriever: 60% semantic, 40% keyword
        hybrid_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, bm25_retriever],
            weights=[0.6, 0.4]
        )

        self.retriever = ProductRetriever(
            hybrid_retriever=hybrid_retriever,
            all_products=catalog
        )

        print("Connecting to NVIDIA NIM (Nemotron)...")
        self.llm = get_nemotron_llm()

        self._initialized = True
        print("ShopMind agent ready.")

    def _get_session(self, session_id: str) -> AgentSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = AgentSession()
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def _build_executor(self, session: AgentSession) -> AgentExecutor:
        """Build a fresh AgentExecutor with session memory."""

        # Tool 1: RAG Retriever
        def rag_retrieve(query: str) -> str:
            docs = self.retriever.retrieve(query)
            if not docs:
                return "No relevant products found."
            results = []
            for doc in docs[:4]:
                m = doc.metadata
                results.append(
                    f"[SKU: {m.get('sku')}] {m.get('name')} — ${m.get('price')} | "
                    f"Category: {m.get('category')} | Rating: {m.get('rating')}/5\n"
                    f"{doc.page_content[:200]}"
                )
            return "\n\n".join(results)

        # Tool 2: Product Filter
        def product_filter(query: str) -> str:
            """
            Parse structured filters from the query.
            Expected format: 'category=headphones, max_price=200, min_rating=4'
            """
            filters = {}
            for part in query.split(","):
                part = part.strip()
                if "=" in part:
                    k, v = part.split("=", 1)
                    filters[k.strip()] = v.strip()

            results = self.retriever.filter_products(filters)
            if not results:
                return "No products match those filters."

            lines = []
            for p in results[:5]:
                lines.append(
                    f"[SKU: {p['sku']}] {p['name']} — ${p['price']} | "
                    f"Rating: {p['rating']} | In stock: {p['in_stock']}"
                )
            return "\n".join(lines)

        # Tool 3: Re-ranker
        def rerank(query_and_skus: str) -> str:
            """
            Re-rank a set of SKUs against a query.
            Format: 'query | SKU1,SKU2,SKU3'
            """
            try:
                query, skus_raw = query_and_skus.split("|", 1)
                skus = [s.strip() for s in skus_raw.split(",")]
            except ValueError:
                return "Invalid format. Use: query | SKU1,SKU2,SKU3"

            ranked = self.retriever.rerank(query.strip(), skus)
            lines = [f"{i+1}. [{p['sku']}] {p['name']} (score: {p.get('rank_score', 'N/A')})"
                     for i, p in enumerate(ranked)]
            return "\n".join(lines) if lines else "No products to re-rank."


        # Tool 4: Price Match Checker
        def price_match(sku: str) -> str:
            """
            Check competitor prices for a product SKU.
            Identifies if Best Buy can price match a lower price elsewhere.
            Input: a single SKU (e.g. HP-001)
            """
            sku = sku.strip().upper()
            product = next((p for p in self._catalog if p["sku"] == sku), None)
            if not product:
                return f"SKU {sku} not found in catalog."

            bby_price = product.get("sale_price") or product["price"]
            competitors = product.get("competitor_prices", {})

            if not competitors:
                return (
                    f"{product['name']} — Best Buy: ${bby_price:.2f}. "
                    "No competitor pricing data available."
                )

            lines = [f"{product['name']}"]
            lines.append(f"Best Buy price: ${bby_price:.2f}")
            lines.append("Competitor prices:")

            cheapest_store = None
            cheapest_price = bby_price

            for store, price in sorted(competitors.items(), key=lambda x: x[1]):
                diff = bby_price - price
                if price < bby_price:
                    lines.append(
                        f"  {store}: ${price:.2f} "
                        f"(${diff:.2f} cheaper — PRICE MATCH ELIGIBLE)"
                    )
                    if price < cheapest_price:
                        cheapest_price = price
                        cheapest_store = store
                else:
                    lines.append(f"  {store}: ${price:.2f}")

            if cheapest_store:
                savings = bby_price - cheapest_price
                lines.append(
                    f"Recommendation: Match {cheapest_store} at ${cheapest_price:.2f}. "
                    f"Customer saves ${savings:.2f} and keeps their Best Buy purchase."
                )
            else:
                lines.append("Best Buy has the lowest price. No price match needed.")

            return "\n".join(lines)

        tools = [
            Tool(name="RAGRetriever", func=rag_retrieve,
                 description="Semantic search over product catalog using dense+sparse hybrid retrieval. "
                              "Use for any query about finding products. Input: natural language query."),
            Tool(name="ProductFilter", func=product_filter,
                 description="Filter products by structured attributes. "
                              "Input format: 'category=headphones, max_price=200, min_rating=4'. "
                              "Use when user specifies price range, category, or rating constraints."),
            Tool(name="ReRanker", func=rerank,
                 description="Re-rank candidate products by relevance to user query. "
                              "Use after retrieval to pick the single best match. "
                              "Input format: 'user query | SKU1,SKU2,SKU3'"),
            Tool(name="PriceMatchChecker", func=price_match,
                 description="Check competitor prices for a product and identify price match opportunities. "
                              "Use when a customer asks about price matching, mentions seeing it cheaper "
                              "elsewhere, or when proactively showing the best available price. "
                              "Input: a single product SKU (e.g. HP-001)."),
        ]

        agent = create_react_agent(self.llm, tools, REACT_PROMPT)
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=session.memory,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    async def run(self, query: str, session_id: str = "default") -> dict:
        """Run the agent and return structured response."""
        session = self._get_session(session_id)
        executor = self._build_executor(session)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: executor.invoke({"input": query})
        )

        # Extract intermediate steps for transparency
        steps = []
        sources = []
        products = []

        for action, observation in result.get("intermediate_steps", []):
            steps.append(f"{action.tool}: {action.tool_input[:80]}...")
            if action.tool == "RAGRetriever":
                # Parse sources from RAG output
                for line in observation.split("\n\n"):
                    if "[SKU:" in line:
                        try:
                            sku = line.split("[SKU:")[1].split("]")[0].strip()
                            name = line.split("] ")[1].split(" — ")[0]
                            sources.append({"sku": sku, "name": name})
                            # Find full product data
                            p = next((x for x in self._catalog if x["sku"] == sku), None)
                            if p and p not in products:
                                products.append(p)
                        except (IndexError, StopIteration):
                            pass

        return {
            "answer": result["output"],
            "sources": sources[:4],
            "products": products[:3],
            "agent_steps": steps,
            "model": "nvidia/nemotron-mini-4b-instruct",
            "retrieval_score": len(sources) / max(len(products), 1) if products else 0.0,
        }

    async def run_stream(self, query: str, session_id: str = "default") -> AsyncIterator[dict]:
        """Stream agent steps and final answer."""
        session = self._get_session(session_id)
        executor = self._build_executor(session)

        yield {"type": "status", "content": "🔍 Analyzing your query..."}
        await asyncio.sleep(0.1)

        loop = asyncio.get_event_loop()

        def _run():
            return executor.invoke({"input": query})

        # Run in executor to avoid blocking
        future = loop.run_in_executor(None, _run)

        yield {"type": "status", "content": "⚡ Running agentic retrieval..."}

        result = await future

        for action, observation in result.get("intermediate_steps", []):
            yield {
                "type": "step",
                "tool": action.tool,
                "content": f"Used {action.tool}: {str(action.tool_input)[:100]}"
            }
            await asyncio.sleep(0.05)

        yield {
            "type": "answer",
            "content": result["output"],
            "model": "nvidia/nemotron-mini-4b-instruct"
        }

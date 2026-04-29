'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Zap, Database, Cpu, RotateCcw, ChevronRight } from 'lucide-react'
import ProductCard from '@/components/ProductCard'
import AgentSteps from '@/components/AgentSteps'
import SystemBadge from '@/components/SystemBadge'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  products?: Product[]
  sources?: Source[]
  steps?: string[]
  model?: string
  retrievalScore?: number
  timestamp: Date
}

interface Product {
  sku: string
  name: string
  brand: string
  category: string
  price: number
  rating: number
  in_stock: boolean
  description: string
}

interface Source {
  sku: string
  name: string
}

const EXAMPLE_QUERIES = [
  'Best noise-canceling headphones under $250 for gym use',
  'I need a professional laptop for ML engineering, budget $2000',
  'Compare Sony vs Bose wireless headphones',
  'Smartwatch for a serious marathon runner',
  'Best budget earbuds under $100 with ANC',
]

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [streamSteps, setStreamSteps] = useState<string[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamSteps])

  const sendMessage = async (query: string) => {
    if (!query.trim() || loading) return
    setInput('')
    setStreamSteps([])

    const userMsg: Message = {
      id: `u_${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      // Use streaming endpoint
      const res = await fetch(`${API_BASE}/api/query/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: sessionId, stream: true }),
      })

      if (!res.ok) throw new Error(`API error: ${res.status}`)

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let finalAnswer = ''
      let finalProducts: Product[] = []
      let finalSources: Source[] = []
      let finalSteps: string[] = []
      let finalModel = ''

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          const text = decoder.decode(value)
          const lines = text.split('\n').filter(l => l.startsWith('data: '))

          for (const line of lines) {
            const data = line.slice(6)
            if (data === '[DONE]') break
            try {
              const chunk = JSON.parse(data)
              if (chunk.type === 'status' || chunk.type === 'step') {
                setStreamSteps(prev => [...prev, chunk.content])
                if (chunk.type === 'step') finalSteps.push(chunk.content)
              } else if (chunk.type === 'answer') {
                finalAnswer = chunk.content
                finalModel = chunk.model || ''
              }
            } catch { /* ignore parse errors on partial chunks */ }
          }
        }
      }

      // Fallback: fetch full response for products/sources
      const fullRes = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, session_id: `${sessionId}_meta` }),
      })

      if (fullRes.ok) {
        const full = await fullRes.json()
        finalProducts = full.products || []
        finalSources = full.sources || []
        if (!finalAnswer) finalAnswer = full.answer
        if (!finalModel) finalModel = full.model
        if (finalSteps.length === 0) finalSteps = full.agent_steps || []
      }

      const assistantMsg: Message = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: finalAnswer || 'I found some relevant products for you.',
        products: finalProducts,
        sources: finalSources,
        steps: finalSteps,
        model: finalModel,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: `e_${Date.now()}`,
        role: 'assistant',
        content: `⚠ Agent error: ${err instanceof Error ? err.message : 'Unknown error'}. Check that the API server is running and NVIDIA_API_KEY is set.`,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
      setStreamSteps([])
    }
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const clearChat = () => {
    setMessages([])
    setStreamSteps([])
    fetch(`${API_BASE}/api/session/${sessionId}`, { method: 'DELETE' }).catch(() => {})
  }

  return (
    <div className="min-h-screen grid-bg flex flex-col">
      {/* Header */}
      <header className="border-b border-white/8 bg-[#080808]/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-8 h-8 rounded border border-[#76b900]/60 flex items-center justify-center glow-green">
                <Zap size={14} className="text-[#76b900]" />
              </div>
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-[#76b900] rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="font-display font-800 text-white text-lg leading-none tracking-tight">
                Shop<span className="text-[#76b900] text-glow">Mind</span>
              </h1>
              <p className="text-[10px] text-white/35 font-mono tracking-widest mt-0.5">
                NVIDIA NEMOTRON × LANGCHAIN × FAISS
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <SystemBadge />
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="flex items-center gap-1.5 text-white/40 hover:text-white/70 text-xs font-mono transition-colors px-2 py-1 border border-white/8 rounded hover:border-white/20"
              >
                <RotateCcw size={10} />
                clear
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 flex flex-col gap-4">
        {/* Empty state */}
        {messages.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex-1 flex flex-col items-center justify-center gap-8 py-16"
          >
            <div className="text-center">
              <div className="inline-flex items-center gap-2 text-[#76b900]/60 text-xs font-mono tracking-widest mb-4 border border-[#76b900]/20 rounded px-3 py-1">
                <span className="w-1.5 h-1.5 bg-[#76b900] rounded-full animate-pulse" />
                AGENTIC RAG SYSTEM ONLINE
              </div>
              <h2 className="font-display text-4xl font-800 text-white mb-3">
                What are you looking for?
              </h2>
              <p className="text-white/40 font-mono text-sm max-w-md">
                Powered by Nemotron + hybrid retrieval. Ask anything about products —
                the agent reasons, retrieves, and cites.
              </p>
            </div>

            {/* Example queries */}
            <div className="w-full max-w-2xl grid gap-2">
              {EXAMPLE_QUERIES.map((q, i) => (
                <motion.button
                  key={q}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  onClick={() => sendMessage(q)}
                  className="flex items-center gap-3 text-left px-4 py-3 border border-white/8 rounded bg-[#111]/50 hover:border-[#76b900]/30 hover:bg-[#76b900]/5 transition-all group card-lift"
                >
                  <ChevronRight size={12} className="text-[#76b900]/40 group-hover:text-[#76b900] transition-colors flex-shrink-0" />
                  <span className="text-white/60 text-sm font-mono group-hover:text-white/90 transition-colors">{q}</span>
                </motion.button>
              ))}
            </div>

            {/* Stack badges */}
            <div className="flex flex-wrap justify-center gap-2 mt-2">
              {['Nemotron-Mini-4B', 'LangChain ReAct', 'FAISS + BM25', 'HuggingFace Embeddings', 'Cross-Encoder Rerank'].map(t => (
                <span key={t} className="text-[10px] font-mono text-white/30 border border-white/8 rounded px-2 py-0.5">
                  {t}
                </span>
              ))}
            </div>
          </motion.div>
        )}

        {/* Messages */}
        <div className="flex flex-col gap-6">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`flex flex-col gap-3 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                {/* Label */}
                <span className="text-[10px] font-mono text-white/25 tracking-widest px-1">
                  {msg.role === 'user' ? 'YOU' : '// SHOPMIND AGENT'}
                </span>

                {/* Bubble */}
                <div className={`max-w-3xl w-full rounded border p-4 ${
                  msg.role === 'user'
                    ? 'bg-[#76b900]/8 border-[#76b900]/20 ml-auto max-w-xl'
                    : 'bg-[#111] border-white/8'
                }`}>
                  <p className="text-sm font-mono leading-relaxed text-white/85 whitespace-pre-wrap">
                    {msg.content}
                  </p>
                </div>

                {/* Agent steps */}
                {msg.steps && msg.steps.length > 0 && (
                  <AgentSteps steps={msg.steps} />
                )}

                {/* Product cards */}
                {msg.products && msg.products.length > 0 && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 w-full max-w-3xl">
                    {msg.products.map((p, i) => (
                      <motion.div
                        key={p.sku}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                      >
                        <ProductCard product={p} />
                      </motion.div>
                    ))}
                  </div>
                )}

                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 max-w-3xl">
                    <span className="text-[10px] font-mono text-white/25 self-center">SOURCES:</span>
                    {msg.sources.map(s => (
                      <span key={s.sku} className="text-[10px] font-mono text-[#76b900]/60 border border-[#76b900]/15 rounded px-2 py-0.5">
                        {s.sku}
                      </span>
                    ))}
                  </div>
                )}

                {/* Model badge */}
                {msg.model && (
                  <div className="flex items-center gap-1.5 text-[10px] font-mono text-white/20">
                    <Cpu size={9} />
                    {msg.model}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading / streaming steps */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-3 items-start"
            >
              <span className="text-[10px] font-mono text-white/25 tracking-widest px-1">// SHOPMIND AGENT</span>
              <div className="bg-[#111] border border-white/8 rounded p-4 max-w-2xl w-full">
                {streamSteps.length === 0 ? (
                  <div className="flex items-center gap-2">
                    <div className="agent-pulse flex gap-1">
                      {[0,1,2].map(i => (
                        <div key={i} className="w-1.5 h-1.5 bg-[#76b900] rounded-full"
                             style={{ animationDelay: `${i * 0.15}s` }} />
                      ))}
                    </div>
                    <span className="text-xs font-mono text-white/40">Initializing agent...</span>
                  </div>
                ) : (
                  <div className="flex flex-col gap-1.5">
                    {streamSteps.map((step, i) => (
                      <div key={i} className="step-reveal flex items-start gap-2 text-xs font-mono text-white/50">
                        <span className="text-[#76b900]/60 flex-shrink-0">›</span>
                        {step}
                      </div>
                    ))}
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-[#76b900] cursor-blink text-sm">▊</span>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>

        <div ref={bottomRef} />
      </main>

      {/* Input bar */}
      <div className="sticky bottom-0 bg-[#080808]/90 backdrop-blur-sm border-t border-white/8">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="relative flex items-end gap-3 bg-[#111] border border-white/10 rounded focus-within:border-[#76b900]/40 transition-colors glow-green">
            <div className="absolute left-4 top-3.5">
              <Database size={13} className="text-[#76b900]/50" />
            </div>
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask about any product... (Shift+Enter for newline)"
              rows={1}
              className="flex-1 bg-transparent text-sm font-mono text-white/85 placeholder-white/20 resize-none pl-9 pr-3 py-3.5 outline-none min-h-[48px] max-h-[120px]"
              style={{ fieldSizing: 'content' } as React.CSSProperties}
              disabled={loading}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              className="m-2 p-2 bg-[#76b900] rounded hover:bg-[#8fd600] disabled:opacity-25 disabled:cursor-not-allowed transition-all flex-shrink-0"
            >
              <Send size={14} className="text-black" />
            </button>
          </div>
          <p className="text-[10px] font-mono text-white/20 text-center mt-2">
            Nemotron via NVIDIA NIM · Hybrid RAG (FAISS + BM25) · LangChain ReAct Agent
          </p>
        </div>
      </div>
    </div>
  )
}

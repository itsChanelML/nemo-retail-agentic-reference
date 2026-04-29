'use client'

import { motion } from 'framer-motion'
import { Search, Filter, ArrowUpDown, ChevronDown } from 'lucide-react'
import { useState } from 'react'

const TOOL_ICONS: Record<string, React.ReactNode> = {
  RAGRetriever: <Search size={10} />,
  ProductFilter: <Filter size={10} />,
  ReRanker: <ArrowUpDown size={10} />,
}

const TOOL_COLORS: Record<string, string> = {
  RAGRetriever: 'text-blue-400/70 border-blue-800/30 bg-blue-900/10',
  ProductFilter: 'text-amber-400/70 border-amber-800/30 bg-amber-900/10',
  ReRanker: 'text-purple-400/70 border-purple-800/30 bg-purple-900/10',
}

export default function AgentSteps({ steps }: { steps: string[] }) {
  const [open, setOpen] = useState(false)

  if (!steps || steps.length === 0) return null

  return (
    <div className="max-w-3xl w-full">
      <button
        onClick={() => setOpen(v => !v)}
        className="flex items-center gap-2 text-[10px] font-mono text-white/25 hover:text-white/50 transition-colors"
      >
        <span className="border border-white/10 rounded px-2 py-0.5 flex items-center gap-1.5">
          <span className="w-1 h-1 bg-[#76b900]/60 rounded-full" />
          {steps.length} agent step{steps.length !== 1 ? 's' : ''}
          <ChevronDown size={9} className={`transition-transform ${open ? 'rotate-180' : ''}`} />
        </span>
      </button>

      {open && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2 flex flex-col gap-1.5 overflow-hidden"
        >
          {steps.map((step, i) => {
            // Parse tool name from step string
            const toolMatch = Object.keys(TOOL_ICONS).find(t => step.includes(t))
            const colorClass = toolMatch ? TOOL_COLORS[toolMatch] : 'text-white/30 border-white/8 bg-white/3'
            const icon = toolMatch ? TOOL_ICONS[toolMatch] : null

            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`flex items-start gap-2 text-[11px] font-mono px-2.5 py-1.5 rounded border ${colorClass}`}
              >
                <span className="flex-shrink-0 mt-0.5">{icon || '›'}</span>
                <span className="opacity-80">{step}</span>
              </motion.div>
            )
          })}
        </motion.div>
      )}
    </div>
  )
}

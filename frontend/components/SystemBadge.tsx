'use client'

import { useEffect, useState } from 'react'
import { Cpu } from 'lucide-react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SystemBadge() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking')

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) })
        const data = await res.json()
        setStatus(data.agent_ready ? 'online' : 'offline')
      } catch {
        setStatus('offline')
      }
    }
    check()
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className={`flex items-center gap-1.5 text-[10px] font-mono border rounded px-2 py-1 ${
      status === 'online'
        ? 'border-[#76b900]/25 text-[#76b900]/60'
        : status === 'offline'
        ? 'border-red-800/30 text-red-400/50'
        : 'border-white/10 text-white/25'
    }`}>
      <div className={`w-1.5 h-1.5 rounded-full ${
        status === 'online' ? 'bg-[#76b900] animate-pulse' :
        status === 'offline' ? 'bg-red-500' : 'bg-white/20 animate-pulse'
      }`} />
      <Cpu size={9} />
      {status === 'online' ? 'AGENT ONLINE' : status === 'offline' ? 'API OFFLINE' : 'CONNECTING...'}
    </div>
  )
}

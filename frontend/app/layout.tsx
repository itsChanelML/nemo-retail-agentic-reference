import type { Metadata } from 'next'
import { Space_Mono, Syne } from 'next/font/google'
import './globals.css'

const syne = Syne({
  subsets: ['latin'],
  variable: '--font-display',
  weight: ['400', '600', '700', '800'],
})

const spaceMono = Space_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '700'],
})

export const metadata: Metadata = {
  title: 'ShopMind — Agentic Retail AI',
  description: 'NVIDIA Nemotron-powered retail agent with hybrid RAG. Built for NVIDIA DevRel demo.',
  openGraph: {
    title: 'ShopMind — Agentic Retail AI',
    description: 'Nemotron × LangChain × FAISS. The future of retail search.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${syne.variable} ${spaceMono.variable}`}>
      <body className="bg-[#080808] text-white font-body antialiased">
        {children}
      </body>
    </html>
  )
}

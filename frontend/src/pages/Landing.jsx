import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Oneko from 'react-cursor-cat'
import Button from '../components/ui/Button'
import Textarea from '../components/ui/Textarea'
import { byPrefixAndName } from '../lib/icons'

const EXAMPLES = [
  'How does DNS work and how does Cloudflare do it?',
  'A practical guide to RAG evaluation metrics',
  'The best open-source LLMs in 2026',
  'Understanding the self-attention mechanism',
  'Prompt injection: attack surface and defenses',
]

export default function Landing() {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')

  function submit(e) {
    e?.preventDefault()
    const trimmed = topic.trim()
    if (trimmed.length < 3) return
    navigate(`/generate?topic=${encodeURIComponent(trimmed)}`)
  }

  return (
    <div className="mx-auto max-w-5xl px-6 pb-24 pt-16">
      <Oneko />

      <div className="text-center">
        <h1 className="mt-6 text-balance text-5xl font-extrabold leading-[1.05] tracking-tight text-slate-900 sm:text-6xl">
          Turn a topic into a
          <span className="bg-gradient-to-r from-orange-500 via-orange-400 to-violet-600 bg-clip-text text-transparent">
            {' '}
            researched technical blog
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-500">
          Give it a topic. The agent decides whether to search the web, builds an outline,
          writes every section in parallel, drops in diagrams, and hands you editable Markdown.
        </p>
      </div>

      <form onSubmit={submit} className="card mx-auto mt-12 max-w-3xl p-6">
        <label htmlFor="topic" className="mb-2 block text-sm font-medium text-slate-700">
          What should we write about?
          <span className="ml-2 text-orange-500">
            <FontAwesomeIcon icon={byPrefixAndName.fas['cat']} />
          </span>
        </label>
        <Textarea
          id="topic"
          rows={4}
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="e.g. How does DNS work and how does Cloudflare do it?"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit(e)
          }}
        />

        <div className="mt-4 flex justify-end">
          <Button type="submit" disabled={topic.trim().length < 3} className="sm:min-w-[180px]">
            Generate blog
            <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 10h11M11 5l5 5-5 5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Button>
        </div>

        <div className="mt-5 flex flex-wrap gap-2 border-t border-orange-100 pt-4">
          <span className="py-1 text-xs text-slate-400">Try:</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => setTopic(ex)}
              className="chip transition hover:border-orange-300 hover:bg-orange-100 hover:text-orange-800"
            >
              {ex}
            </button>
          ))}
        </div>
      </form>
    </div>
  )
}

import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import MarkdownEditor from '../components/MarkdownEditor'
import ProgressTimeline from '../components/ProgressTimeline'
import { getBlog, streamGenerate } from '../lib/api'
import { cn, downloadMarkdown, toFilename } from '../lib/utils'

const STEPS = [
  { key: 'router_node', label: 'Routing the topic' },
  { key: 'research_node', label: 'Researching the web' },
  { key: 'orchestrator', label: 'Planning the outline' },
  { key: 'worker', label: 'Writing sections' },
  { key: 'reducer', label: 'Assembling & generating diagrams' },
]

const initialStatus = () => Object.fromEntries(STEPS.map((s) => [s.key, 'pending']))

function modeTone(mode) {
  if (mode === 'open_book') return 'amber'
  if (mode === 'hybrid') return 'sky'
  return 'green'
}

export default function Generator() {
  const [params] = useSearchParams()
  const topic = params.get('topic') || ''
  const blogId = params.get('id') || ''

  const [status, setStatus] = useState('idle')
  const [markdown, setMarkdown] = useState('')
  const [error, setError] = useState('')
  const [title, setTitle] = useState('')
  const [meta, setMeta] = useState({})
  const [stepStatus, setStepStatus] = useState(initialStatus)
  const [sections, setSections] = useState([])
  const [evidenceCount, setEvidenceCount] = useState(0)
  const [imageCount, setImageCount] = useState(0)
  const [copied, setCopied] = useState(false)

  const startedRef = useRef(false)
  const abortRef = useRef(null)

  function applyProgress(node, data) {
    setStepStatus((prev) => {
      const next = { ...prev }
      const activate = (key) => {
        if (next[key] === 'pending') next[key] = 'active'
      }

      if (node === 'worker') {
        if (next.worker === 'pending') next.worker = 'active'
        return next
      }

      if (node in next) next[node] = 'done'

      if (node === 'orchestrator' && next.research_node === 'pending') {
        next.research_node = 'skipped'
      }

      if (node === 'router_node') {
        if (data?.needs_research) activate('research_node')
        else activate('orchestrator')
      } else if (node === 'research_node') {
        activate('orchestrator')
      } else if (node === 'orchestrator') {
        activate('worker')
      } else if (node === 'reducer') {
        if (next.worker !== 'done' && next.worker !== 'skipped') next.worker = 'done'
        next.reducer = 'done'
      }

      return next
    })
  }

  async function runGeneration() {
    setStatus('running')
    setError('')
    setMarkdown('')
    setSections([])
    setEvidenceCount(0)
    setImageCount(0)
    setStepStatus({ ...initialStatus(), router_node: 'active' })

    const controller = new AbortController()
    abortRef.current = controller

    try {
      await streamGenerate(
        { topic },
        {
          signal: controller.signal,
          onEvent: (event, data) => {
            if (event === 'progress') {
              applyProgress(data.node, data)
            } else if (event === 'plan') {
              setTitle(data.blog_title || '')
              setMeta((m) => ({ ...m, blog_kind: data.blog_kind, mode: data.mode }))
            } else if (event === 'evidence') {
              setEvidenceCount(data.count || 0)
            } else if (event === 'section') {
              setSections((prev) => [...prev, data])
            } else if (event === 'images') {
              setImageCount(data.count || 0)
            } else if (event === 'done') {
              setMarkdown(data.markdown || '')
              setTitle(data.title || '')
              setMeta(data)
              setStatus('done')
            } else if (event === 'error') {
              setError(data.message || 'Generation failed')
              setStatus('error')
            }
          },
        },
      )
    } catch (e) {
      if (e.name !== 'AbortError') {
        setError(e.message || 'Generation failed')
        setStatus('error')
      }
    }
  }

  // Load an existing blog when ?id= is present.
  useEffect(() => {
    if (!blogId) return undefined
    let cancelled = false
    setStatus('loading')
    getBlog(blogId)
      .then((b) => {
        if (cancelled) return
        setMarkdown(b.markdown || '')
        setTitle(b.title || '')
        setMeta(b)
        setEvidenceCount(b.evidence_count || 0)
        setStatus('done')
      })
      .catch((e) => {
        if (cancelled) return
        setError(e.message || 'Failed to load blog')
        setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [blogId])

  // Kick off generation once.
  useEffect(() => {
    if (blogId || !topic || startedRef.current) return undefined
    startedRef.current = true
    runGeneration()
    return () => abortRef.current?.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const timeline = useMemo(
    () =>
      STEPS.map((s) => {
        let detail
        if (s.key === 'research_node' && evidenceCount) detail = `${evidenceCount} sources`
        if (s.key === 'worker' && sections.length) detail = `${sections.length} sections written`
        if (s.key === 'reducer' && imageCount) detail = `${imageCount} diagrams`
        return { ...s, status: stepStatus[s.key], detail }
      }),
    [stepStatus, evidenceCount, sections.length, imageCount],
  )

  async function copyMarkdown() {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* ignore */
    }
  }

  const isRunning = status === 'running' || status === 'loading'

  if (!topic && !blogId) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-24 text-center">
        <h2 className="text-2xl font-bold text-slate-900">No topic provided</h2>
        <p className="mt-2 text-slate-500">Start from the home page to generate a blog.</p>
        <Link to="/" className="btn-primary mt-6 inline-flex">
          Back home
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      {isRunning ? (
        <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
          <Card>
            <p className="text-xs font-semibold uppercase tracking-widest text-orange-600">
              Generating
            </p>
            <h2 className="mt-2 text-lg font-semibold leading-snug text-slate-900">
              {topic || 'Working…'}
            </h2>
            <div className="mt-6">
              <ProgressTimeline steps={timeline} />
            </div>
            {status === 'running' && (
              <Button variant="ghost" className="mt-6 w-full" onClick={() => abortRef.current?.abort()}>
                Cancel
              </Button>
            )}
          </Card>

          <Card className="min-h-[420px]">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-600">Live draft</p>
              <span className="chip">{sections.length} sections</span>
            </div>
            <div className="mt-5 space-y-4">
              {sections.length === 0 ? (
                <div className="space-y-3">
                  {[90, 75, 80, 60].map((w, i) => (
                    <div
                      key={i}
                      className="h-4 animate-pulse rounded bg-slate-100"
                      style={{ width: `${w}%` }}
                    />
                  ))}
                </div>
              ) : (
                sections.map((s) => (
                  <div key={s.task_id} className="rounded-xl border border-orange-100 bg-orange-50/60 p-4">
                    <p className="text-xs font-semibold text-orange-600">Section {s.task_id}</p>
                    <pre className="mt-2 max-h-40 overflow-hidden whitespace-pre-wrap font-mono text-xs text-slate-500">
                      {s.markdown.slice(0, 600)}
                      {s.markdown.length > 600 ? '…' : ''}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      ) : status === 'error' ? (
        <Card className="mx-auto max-w-2xl border-rose-200">
          <h2 className="text-lg font-semibold text-rose-600">Generation failed</h2>
          <p className="mt-2 whitespace-pre-wrap text-sm text-slate-500">{error}</p>
          <div className="mt-6 flex gap-3">
            <Button
              onClick={() => {
                startedRef.current = false
                runGeneration()
              }}
            >
              Retry
            </Button>
            <Link to="/" className="btn-ghost">
              New topic
            </Link>
          </div>
        </Card>
      ) : (
        <div>
          <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <Link to="/" className="text-xs font-medium text-slate-400 hover:text-slate-700">
                ← Back to home
              </Link>
              <h1 className="mt-2 max-w-3xl text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
                {title || topic}
              </h1>
              <div className="mt-3 flex flex-wrap gap-2">
                {meta.mode && <Badge tone={modeTone(meta.mode)}>{meta.mode}</Badge>}
                {meta.blog_kind && <Badge tone="brand">{meta.blog_kind}</Badge>}
                {typeof meta.needs_research === 'boolean' && (
                  <Badge tone={meta.needs_research ? 'sky' : 'default'}>
                    {meta.needs_research ? 'web research' : 'closed book'}
                  </Badge>
                )}
                {evidenceCount > 0 && <Badge>{evidenceCount} sources</Badge>}
                {imageCount > 0 && <Badge>{imageCount} diagrams</Badge>}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button variant="ghost" onClick={copyMarkdown}>
                {copied ? 'Copied!' : 'Copy markdown'}
              </Button>
              <Button
                variant="ghost"
                onClick={() => downloadMarkdown(toFilename(title), markdown)}
              >
                Download .md
              </Button>
              <Link to="/" className="btn-primary">
                New blog
              </Link>
            </div>
          </div>

          <MarkdownEditor value={markdown} onChange={setMarkdown} />

          <p className="mt-4 text-center text-xs text-slate-400">
            Edits are local to this view. Download or copy to keep them.
          </p>
        </div>
      )}
    </div>
  )
}

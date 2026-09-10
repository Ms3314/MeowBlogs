import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import { deleteBlog, listBlogs } from '../lib/api'
import { formatDate } from '../lib/utils'

export default function History() {
  const [blogs, setBlogs] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState('')

  async function load() {
    setStatus('loading')
    try {
      const data = await listBlogs()
      setBlogs(data)
      setStatus('ready')
    } catch (e) {
      setError(e.message || 'Failed to load history')
      setStatus('error')
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function remove(id) {
    try {
      await deleteBlog(id)
      setBlogs((prev) => prev.filter((b) => b.id !== id))
    } catch (e) {
      setError(e.message || 'Failed to delete')
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Your library</h1>
          <p className="mt-1 text-sm text-slate-500">Every generated blog is saved automatically.</p>
        </div>
        <Link to="/" className="btn-primary">
          New blog
        </Link>
      </div>

      {status === 'loading' && (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-2xl bg-slate-100" />
          ))}
        </div>
      )}

      {status === 'error' && (
        <Card className="border-rose-200">
          <p className="text-sm text-rose-600">{error}</p>
        </Card>
      )}

      {status === 'ready' && blogs.length === 0 && (
        <Card className="text-center">
          <p className="text-slate-500">No blogs yet. Generate your first one.</p>
          <Link to="/" className="btn-primary mx-auto mt-5 inline-flex">
            Get started
          </Link>
        </Card>
      )}

      <div className="space-y-3">
        {blogs.map((blog) => (
          <Card key={blog.id} className="flex items-center justify-between gap-4 p-5 transition hover:border-orange-300">
            <Link to={`/generate?id=${blog.id}`} className="min-w-0 flex-1">
              <h3 className="truncate text-base font-semibold text-slate-900">
                {blog.title || blog.topic}
              </h3>
              <p className="mt-1 truncate text-sm text-slate-500">{blog.topic}</p>
              <div className="mt-3 flex flex-wrap items-center gap-2">
                {blog.mode && <Badge tone="sky">{blog.mode}</Badge>}
                {blog.blog_kind && <Badge tone="brand">{blog.blog_kind}</Badge>}
                <span className="text-xs text-slate-400">{formatDate(blog.created_at)}</span>
              </div>
            </Link>
            <div className="flex shrink-0 items-center gap-2">
              <Link to={`/generate?id=${blog.id}`} className="btn-ghost">
                Open
              </Link>
              <Button
                variant="ghost"
                onClick={() => remove(blog.id)}
                className="text-rose-500 hover:bg-rose-50"
              >
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

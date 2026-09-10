const API_BASE = import.meta.env.VITE_API_BASE || ''

/**
 * POST the topic to the backend and consume the SSE progress stream.
 * `onEvent(eventName, data)` is called for each SSE frame.
 * Returns a promise that resolves when the stream ends.
 */
export async function streamGenerate(payload, { onEvent, signal } = {}) {
  const res = await fetch(`${API_BASE}/api/blog/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })

  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed with status ${res.status}`)
  }
  if (!res.body) {
    throw new Error('Streaming is not supported in this browser.')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const frames = buffer.split('\n\n')
    buffer = frames.pop() || ''

    for (const frame of frames) {
      if (!frame.trim()) continue
      let event = 'message'
      let data = ''
      for (const line of frame.split('\n')) {
        if (line.startsWith('event:')) event = line.slice(6).trim()
        else if (line.startsWith('data:')) data += line.slice(5).trim()
      }
      if (!data) continue
      let parsed = data
      try {
        parsed = JSON.parse(data)
      } catch {
        /* keep raw string */
      }
      onEvent?.(event, parsed)
    }
  }
}

export async function listBlogs() {
  const res = await fetch(`${API_BASE}/api/blogs`)
  if (!res.ok) throw new Error('Failed to load history')
  return res.json()
}

export async function getBlog(id) {
  const res = await fetch(`${API_BASE}/api/blogs/${id}`)
  if (!res.ok) throw new Error('Failed to load blog')
  return res.json()
}

export async function deleteBlog(id) {
  const res = await fetch(`${API_BASE}/api/blogs/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Failed to delete blog')
  return res.json()
}

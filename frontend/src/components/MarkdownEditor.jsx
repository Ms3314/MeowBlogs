import { useState } from 'react'
import MDEditor from '@uiw/react-md-editor'
import { cn } from '../lib/utils'

const MODES = [
  { key: 'live', label: 'Split' },
  { key: 'edit', label: 'Edit' },
  { key: 'preview', label: 'Preview' },
]

export default function MarkdownEditor({ value, onChange, height = 640 }) {
  const [mode, setMode] = useState('live')

  return (
    <div data-color-mode="light" className="w-full">
      <div className="mb-3 flex items-center justify-end gap-1 rounded-xl border border-orange-100 bg-orange-50/60 p-1">
        {MODES.map((m) => (
          <button
            key={m.key}
            type="button"
            onClick={() => setMode(m.key)}
            className={cn(
              'rounded-lg px-3.5 py-1.5 text-xs font-semibold transition',
              mode === m.key
                ? 'bg-orange-500 text-white shadow'
                : 'text-slate-500 hover:text-slate-900',
            )}
          >
            {m.label}
          </button>
        ))}
      </div>

      <MDEditor
        value={value}
        onChange={(v) => onChange?.(v ?? '')}
        height={height}
        preview={mode}
        visibleDragbar={false}
      />
    </div>
  )
}

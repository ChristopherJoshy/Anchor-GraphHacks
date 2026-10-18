import { Braces, ChevronDown, ChevronRight } from 'lucide-react'
import { useState } from 'react'
import { asRecord, formatValue } from './data'

export function JsonPanel({ title, value, empty = 'No data returned yet.' }: { title: string; value: unknown; empty?: string }) {
  const [open, setOpen] = useState(false)
  if (value === null || value === undefined) return <div className="empty-inline">{empty}</div>
  const record = asRecord(value)
  const keys = record ? Object.keys(record).slice(0, 5) : []
  return <section className="data-panel">
    <button className="json-toggle" aria-expanded={open} onClick={() => setOpen(!open)}>
      {open ? <ChevronDown size={15} /> : <ChevronRight size={15} />}<Braces size={15} />{title}
      {!open && keys.length > 0 && <span className="preview-keys">{keys.join(' · ')}</span>}
    </button>
    {open && <pre className="json-view">{formatValue(value)}</pre>}
  </section>
}

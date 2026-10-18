import type { RecordValue } from './types'

const base = (import.meta.env.VITE_ANCHOR_API_URL ?? '').replace(/\/$/, '')

export async function api<T = unknown>(path: string, method = 'GET', body?: RecordValue): Promise<T> {
  const response = await fetch(`${base}/api${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const root = payload && typeof payload === 'object' ? payload as RecordValue : null
    const error = (root?.error ?? root?.detail) as RecordValue | null
    const message = typeof error?.message === 'string' ? error.message
      : typeof root?.detail === 'string' ? root.detail : `Request failed (${response.status})`
    const code = typeof error?.code === 'string' ? `${error.code}: ` : ''
    throw new Error(`${code}${message}`)
  }
  return payload as T
}

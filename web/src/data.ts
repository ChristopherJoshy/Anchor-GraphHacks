import type { Arc, Point, RecordValue } from './types'

export const SCENARIO_ID = 'SCENARIO-SILICON-CASCADE'
export const INCIDENT_ENTITY_ID = 'SUP-TAIWAN-FOUNDRY'
export const INDEPENDENT_SUPPLIER_ID = 'SUP-INDEPENDENT-D'

export function asRecord(value: unknown): RecordValue | null {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as RecordValue : null
}

export function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : []
}

export function firstString(...values: unknown[]): string | undefined {
  return values.find((value): value is string => typeof value === 'string' && value.length > 0)
}

function rowsFrom(value: unknown, names: string[]): RecordValue[] {
  const root = asRecord(value)
  if (!root) return []
  for (const name of names) {
    const rows = asArray(root[name]).map(asRecord).filter((row): row is RecordValue => row !== null)
    if (rows.length) return rows
  }
  return []
}

export function entitiesFrom(network: unknown): RecordValue[] {
  const root = asRecord(network)
  if (!root) return []
  const direct = rowsFrom(root, ['entity_records', 'nodes', 'items'])
  if (direct.length) return direct
  const groups = asRecord(root.entities)
  if (!groups) return []
  return Object.entries(groups).flatMap(([kind, entries]) => asArray(entries).map(asRecord)
    .filter((row): row is RecordValue => row !== null).map(row => ({ ...row, _kind: kind })))
}

export function locationsFrom(network: unknown): RecordValue[] {
  return rowsFrom(asRecord(network)?.locations ?? asRecord(network)?.scenario_locations, ['locations', 'items'])
    .concat(rowsFrom(network, ['locations', 'scenario_locations']))
}

export function relationshipsFrom(network: unknown): RecordValue[] {
  return rowsFrom(network, ['relationship_records', 'edges', 'relationship_paths', 'paths'])
}

export function historyRows(history: unknown, kind: string): RecordValue[] {
  const root = asRecord(history)
  const list = Array.isArray(history) ? history : asArray(root?.[kind.toLowerCase() + 's'])
  return list.map(asRecord).filter((row): row is RecordValue => row !== null)
    .filter(row => !row.kind || String(row.kind).toLowerCase() === kind.toLowerCase())
}

function coordinate(row: RecordValue, latNames: string[], lngNames: string[]): Point | null {
  const lat = latNames.map(key => row[key]).find(value => typeof value === 'number')
  const lng = lngNames.map(key => row[key]).find(value => typeof value === 'number')
  if (typeof lat !== 'number' || typeof lng !== 'number') return null
  return { lat, lng, label: firstString(row.name, row.label, row.id) ?? 'Location', id: typeof row.id === 'string' ? row.id : undefined }
}

export function pointsFrom(network: unknown): Point[] {
  return locationsFrom(network).map(row => coordinate(row, ['lat', 'latitude'], ['lon', 'lng', 'longitude']))
    .filter((point): point is Point => point !== null)
}

export function arcsFrom(network: unknown): Arc[] {
  const points = new Map(pointsFrom(network).filter(point => point.id).map(point => [point.id!, point]))
  return relationshipsFrom(network).flatMap(row => {
    const from = firstString(row.from, row.source, row.start, row.from_id, row.source_id)
    const to = firstString(row.to, row.target, row.end, row.to_id, row.target_id)
    const start = from ? points.get(from) : undefined
    const end = to ? points.get(to) : undefined
    return start && end ? [{ startLat: start.lat, startLng: start.lng, endLat: end.lat, endLng: end.lng, label: firstString(row.type, row.label, row.kind) ?? 'Relationship' }] : []
  })
}

export function formatValue(value: unknown, depth = 0): string {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (depth > 1) return Array.isArray(value) ? `${value.length} records` : 'Structured data'
  return JSON.stringify(value, null, 2)
}

export function findObject(value: unknown, key: string): RecordValue | undefined {
  const root = asRecord(value)
  if (!root) return undefined
  if (typeof root[key] === 'object' && root[key] !== null) return asRecord(root[key]) ?? undefined
  for (const child of Object.values(root)) {
    if (Array.isArray(child)) {
      for (const item of child) {
        const found = findObject(item, key)
        if (found) return found
      }
    } else {
      const found = findObject(child, key)
      if (found) return found
    }
  }
  return undefined
}

export function findString(value: unknown, key: string): string | undefined {
  const root = asRecord(value)
  if (!root) return undefined
  if (typeof root[key] === 'string') return root[key] as string
  for (const child of Object.values(root)) {
    if (Array.isArray(child)) {
      for (const item of child) {
        const found = findString(item, key)
        if (found) return found
      }
    } else {
      const found = findString(child, key)
      if (found) return found
    }
  }
  return undefined
}

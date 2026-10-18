import { asArray, asRecord, entitiesFrom, firstString, locationsFrom, relationshipsFrom } from './data.ts'
import type { RecordValue } from './types'

export type MapLayer = 'dependencies' | 'transport' | 'recovery'
export interface MapLocation {
  id: string
  name: string
  country: string
  lat: number
  lng: number
  records: RecordValue[]
  affected: string[]
}
export interface MapConnection {
  id: string
  from: string
  to: string
  layer: MapLayer
  label: string
  affected: boolean
  evidence: string[]
  quantity?: number
}

export function recordName(record: RecordValue | undefined, fallback = 'Unknown record'): string {
  return firstString(record?.name, record?.id) ?? fallback
}

export function recordKind(record: RecordValue): string {
  const labels = asArray(record.labels)
  if (typeof labels[0] === 'string') return labels[0]
  // The demo API omits labels; these prefixes are its stable application ID conventions.
  const prefix = String(record.id ?? '').split('-')[0]
  return ({ SUP: 'Supplier', FAC: 'Facility', INV: 'Inventory', ORDER: 'Order', CUST: 'Customer' } as Record<string, string>)[prefix] ?? 'Record'
}

/** Geographic display joins only. Dependency paths and eligibility come from the backend. */
export function buildGeography(network: unknown, assessment: unknown = null, plan: unknown = null) {
  const locations: MapLocation[] = []
  const seen = new Set<string>()
  for (const row of locationsFrom(network)) {
    const id = firstString(row.id)
    const lat = row.lat ?? row.latitude
    const lng = row.lon ?? row.lng ?? row.longitude
    if (!id || seen.has(id) || typeof lat !== 'number' || typeof lng !== 'number'
      || !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) continue
    seen.add(id)
    locations.push({ id, name: recordName(row), country: firstString(row.country) ?? '', lat, lng, records: [], affected: [] })
  }
  const records = entitiesFrom(network)
  const byId = new Map(records.map(row => [String(row.id), row]))
  const byLocation = new Map(locations.map(row => [row.id, row]))
  const byCountry = new Map(locations.filter(row => row.country).map(row => [row.country, row]))
  const located = new Map<string, string>()
  for (const location of locations) located.set(location.id, location.id)
  for (const row of records) {
    const location = byCountry.get(String(row.country ?? ''))
    if (location) located.set(String(row.id), location.id)
  }
  const relations = relationshipsFrom(network)
  // A warehouse inventory record can inherit its recorded facility's reference location.
  for (const type of ['LOCATED_AT', 'HELD_AT', 'DELIVERED_TO']) {
    for (const edge of relations.filter(edge => edge.type === type)) {
      const destination = located.get(String(edge.to))
      if (destination) located.set(String(edge.from), destination)
    }
  }
  const impact = asRecord(assessment)
  const affectedIds = new Set(asArray(impact?.affected_entities).map(asRecord).map(row => String(row?.id)))
  const incident = asRecord(impact?.incident)
  if (incident?.entity_id) affectedIds.add(String(incident.entity_id))
  for (const row of records) {
    const location = byLocation.get(located.get(String(row.id)) ?? '')
    if (location && ['Supplier', 'Facility', 'Inventory'].includes(recordKind(row))) {
      location.records.push(row)
      if (affectedIds.has(String(row.id))) location.affected.push(String(row.id))
    }
  }
  const connections: MapConnection[] = []
  function connect(id: string, fromId: string, toId: string, layer: MapLayer, label: string, evidence: string[], quantity?: number) {
    const from = located.get(fromId), to = located.get(toId)
    if (!from || !to || from === to) return
    connections.push({ id, from, to, layer, label, evidence, quantity,
      affected: affectedIds.has(fromId) || affectedIds.has(toId) })
  }
  for (const row of relations.filter(row => row.type === 'DEPENDS_ON')) {
    connect(`dependency:${row.from}:${row.to}`, String(row.from), String(row.to), 'dependencies',
      `${recordName(byId.get(String(row.from)))} depends on ${recordName(byId.get(String(row.to)))}`, [String(row.from), String(row.to)])
  }
  const starts = new Map(relations.filter(row => row.type === 'STARTS_AT').map(row => [String(row.from), String(row.to)]))
  for (const row of relations.filter(row => row.type === 'ENDS_AT')) {
    const start = starts.get(String(row.from))
    if (start) connect(`route:${row.from}`, start, String(row.to), 'transport', `Modeled route ${row.from}`, [String(row.from)])
  }
  for (const [i, value] of asArray(asRecord(plan)?.allocations).entries()) {
    const allocation = asRecord(value)
    if (!allocation) continue
    connect(`recovery:${i}`, String(allocation.source_id), String(allocation.order_id), 'recovery',
      `${allocation.quantity} units from ${recordName(byId.get(String(allocation.source_id)), String(allocation.source_id))}`,
      [String(allocation.source_id), String(allocation.order_id)], typeof allocation.quantity === 'number' ? allocation.quantity : undefined)
  }
  return { locations, connections, records, byId, located }
}

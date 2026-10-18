import assert from 'node:assert/strict'
import test from 'node:test'
import { buildGeography } from '../src/geography.ts'

const network = {
  locations: [
    { id: 'LOC-JP', name: 'Japan', country: 'JP', lat: 35.67, lon: 139.65 },
    { id: 'LOC-TW', name: 'Taiwan', country: 'TW', lat: 25.03, lon: 121.56 },
    { id: 'BAD', lat: 999, lon: 0 }, { id: 'NOT-FINITE', lat: NaN, lon: 0 },
  ],
  entity_records: [
    { id: 'SUP-X', name: 'Vendor X', country: 'JP' },
    { id: 'SUP-Y', name: 'Upstream Y', country: 'TW' },
    { id: 'FAC-X', country: 'JP' }, { id: 'INV-X', quantity: 350 },
    { id: 'ORDER-X' }, { id: 'CUST-X', country: 'TW' },
  ],
  relationship_records: [
    { from: 'SUP-X', to: 'SUP-Y', type: 'DEPENDS_ON' },
    { from: 'SUP-X', to: 'MISSING', type: 'DEPENDS_ON' },
    { from: 'INV-X', to: 'FAC-X', type: 'HELD_AT' },
    { from: 'ORDER-X', to: 'CUST-X', type: 'DELIVERED_TO' },
    { from: 'ROUTE-X', to: 'LOC-JP', type: 'STARTS_AT' },
    { from: 'ROUTE-X', to: 'LOC-TW', type: 'ENDS_AT' },
    { from: 'ROUTE-INCOMPLETE', to: 'LOC-TW', type: 'ENDS_AT' },
  ],
}

test('maps geographic references and warehouse records without inventing coordinates', () => {
  const graph = buildGeography(network)
  assert.equal(graph.locations.length, 2)
  assert.equal(graph.located.get('INV-X'), 'LOC-JP')
  assert.equal(graph.located.has('MISSING'), false)
  assert.equal(graph.locations[0].records.length, 3)
  assert.equal(graph.connections.length, 2)
  assert.equal(graph.connections[0].label, 'Vendor X depends on Upstream Y')
  assert.deepEqual(graph.connections[1].evidence, ['ROUTE-X'])
})

test('reflects graph-returned impact and real allocations, including a changed dependency edge', () => {
  const impact = { incident: { entity_id: 'SUP-Y' }, affected_entities: [{ id: 'SUP-X' }] }
  const plan = { allocations: [{ source_id: 'INV-X', order_id: 'ORDER-X', quantity: 350 }] }
  const graph = buildGeography(network, impact, plan)
  assert.deepEqual(graph.locations.map(row => row.affected), [['SUP-X'], ['SUP-Y']])
  assert.equal(graph.connections[0].affected, true)
  assert.deepEqual(graph.connections.at(-1), { id: 'recovery:0', from: 'LOC-JP', to: 'LOC-TW', layer: 'recovery',
    label: '350 units from INV-X', affected: false, evidence: ['INV-X', 'ORDER-X'], quantity: 350 })
  const disconnected = { ...network, relationship_records: network.relationship_records.filter(row => row.type !== 'DEPENDS_ON') }
  assert.equal(buildGeography(disconnected).connections.filter(row => row.layer === 'dependencies').length, 0)
})

test('missing graph data yields an empty map, not a synthetic fallback network', () => {
  assert.deepEqual(buildGeography(null).locations, [])
  assert.deepEqual(buildGeography({}).connections, [])
})

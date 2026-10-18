import { ArrowLeft, ArrowUpRight, Building2, MapPin } from 'lucide-react'
import { asArray, asRecord, relationshipsFrom } from './data'
import { recordKind, recordName } from './geography'
import type { MapConnection, MapLocation } from './geography'
import type { RecordValue } from './types'
import { money } from './RecoveryResults'

interface Props {
  location: MapLocation
  record: RecordValue | undefined
  connection: MapConnection | undefined
  network: unknown
  byId: Map<string, RecordValue>
  assessment: unknown
  onRecord: (id: string) => void
  onClose: () => void
  onCity: () => void
}

export function LocationInspector({ location, record, connection, network, byId, assessment, onRecord, onClose, onCity }: Props) {
  const dependents = relationshipsFrom(network).filter(row => row.type === 'DEPENDS_ON' && row.from === record?.id)
  const exposed = record ? location.affected.includes(String(record.id)) : location.affected.length > 0
  const paths = asArray(asRecord(assessment)?.shared_dependency_paths).map(asRecord).filter(row => row?.supplier_id === record?.id)
  return <section className="location-inspector">
    <button className="text-button back-button" onClick={onClose}><ArrowLeft size={14} />Back to recovery guide</button>
    <span className="section-label">{connection ? 'Connection details' : record ? recordKind(record) : 'Network location'}</span>
    <h2>{record ? recordName(record).replace(' (synthetic)', '') : location.name}</h2>
    <p className="location-reference"><MapPin size={14} />{location.name} · {location.country} · geographic reference</p>
    {connection && <div className="inline-notice"><strong>{connection.label}</strong><p>{connection.layer === 'transport' ? 'A modeled transport connection, not a live shipment.' : 'A relationship returned from the operational graph.'}</p><small>{connection.evidence.join(' → ')}</small></div>}
    <div className={`exposure-message ${exposed ? 'exposed' : ''}`}><i /><div><strong>{exposed ? 'Connected to the disruption' : assessment ? 'No impact shown in this assessment' : 'Impact not assessed yet'}</strong><p>{exposed ? 'The returned dependency paths place this record or location in the affected network.' : 'Availability and exposure are different. Use the recovery guide to assess the incident.'}</p></div></div>
    {record && <><dl className="record-facts">
      {typeof record.capacity === 'number' && <div><dt>Modeled capacity</dt><dd>{record.capacity.toLocaleString()} units / demo bucket</dd></div>}
      {typeof record.quantity === 'number' && <div><dt>Recorded inventory</dt><dd>{record.quantity.toLocaleString()} units</dd></div>}
      {typeof record.unit_price_minor === 'number' && <div><dt>Modeled unit price</dt><dd>{money(record.unit_price_minor)}</dd></div>}
      {typeof record.lead_days === 'number' && <div><dt>Delivery lead time</dt><dd>{record.lead_days} days</dd></div>}
      {typeof record.available === 'boolean' && <div><dt>Availability flag</dt><dd>{record.available ? 'Marked available' : 'Marked unavailable'}</dd></div>}
    </dl>
    {dependents.length > 0 && <div className="inspector-group"><h3>Recorded upstream dependencies</h3>{dependents.map((edge, index) => <p key={index}>{recordName(byId.get(String(edge.to)), String(edge.to)).replace(' (synthetic)', '')}</p>)}</div>}
    {paths.length > 0 && <div className="inspector-group"><h3>Incident evidence</h3>{paths.map((path, index) => <p key={index}>{asArray(path?.path).map(id => recordName(byId.get(String(id)), String(id)).replace(' (synthetic)', '')).join(' → ')}</p>)}</div>}
    </>}
    <div className="inspector-group"><h3>{record ? 'Other records at this reference' : 'Suppliers, facilities & inventory'}</h3><p className="muted">{location.records.length} records returned for this location.</p><div className="record-list">{location.records.filter(row => row.id !== record?.id).map(row => <button key={String(row.id)} onClick={() => onRecord(String(row.id))}><Building2 size={15} /><span>{recordName(row).replace(' (synthetic)', '')}<small>{recordKind(row)}</small></span><ArrowUpRight size={13} /></button>)}</div></div>
    <button className="secondary-button city-button" onClick={onCity}><MapPin size={15} />Explore the reference area</button>
    <p className="simulation-note">Locations are city reference points, not precise factory or warehouse addresses. Companies and commercial relationships are synthetic.</p>
    {record && <details className="technical-details"><summary>Record provenance & technical fields</summary><pre>{JSON.stringify(record, null, 2)}</pre></details>}
  </section>
}

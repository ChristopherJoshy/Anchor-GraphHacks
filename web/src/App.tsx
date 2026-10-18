import { Anchor, ArrowLeft, ArrowRight, ArrowUpRight, Check, Database, Globe2, RefreshCw, Search, X } from 'lucide-react'
import { lazy, Suspense, useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { asRecord, entitiesFrom, firstString, historyRows, INCIDENT_ENTITY_ID, INDEPENDENT_SUPPLIER_ID, SCENARIO_ID } from './data'
import { buildGeography, recordKind, recordName } from './geography'
import type { MapFocus } from './EarthExplorer'
import { JsonPanel } from './JsonPanel'
import { LocationInspector } from './LocationInspector'
import { RecoveryPanel } from './RecoveryPanel'
import { RecoveryResults } from './RecoveryResults'

const EarthExplorer = lazy(() => import('./EarthExplorer').then(module => ({ default: module.EarthExplorer })))
const countryNames = new Intl.DisplayNames(['en'], { type: 'region' })
type View = 'network' | 'recovery' | 'evidence'
type Operation = 'incident' | 'assessment' | 'plan' | 'execute' | 'verify' | 'capacity' | 'reset'
type Snapshot = { health: unknown; network: unknown; history: unknown }
const working: Record<Operation, string> = { incident: 'Recording the outage…', assessment: 'Tracing connections…', plan: 'Calculating recovery…', execute: 'Applying the plan…', verify: 'Checking the ERP…', capacity: 'Updating capacity…', reset: 'Preparing the scenario…' }

function dateLabel(value: unknown) {
  const date = new Date(String(value ?? ''))
  return Number.isNaN(date.getTime()) ? 'Time not recorded' : date.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

export default function App() {
  const [snapshot, setSnapshot] = useState<Snapshot>({ health: null, network: null, history: null })
  const [view, setView] = useState<View>('network')
  const [incident, setIncident] = useState<unknown>(null)
  const [assessment, setAssessment] = useState<unknown>(null)
  const [plan, setPlan] = useState<unknown>(null)
  const [execution, setExecution] = useState<unknown>(null)
  const [verification, setVerification] = useState<unknown>(null)
  const [capacity, setCapacity] = useState(650)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [connectionError, setConnectionError] = useState('')
  const [updated, setUpdated] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [locationId, setLocationId] = useState<string | null>(null)
  const [recordId, setRecordId] = useState<string | null>(null)
  const [connectionId, setConnectionId] = useState<string | null>(null)
  const [focus, setFocus] = useState<MapFocus | null>(null)

  const refresh = useCallback(async () => {
    try {
      const [health, network, history] = await Promise.all([api('/health'), api('/network'), api('/history')])
      setSnapshot({ health, network, history })
      setConnectionError('')
      setUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }))
      const source = entitiesFrom(network).find(row => row.id === INDEPENDENT_SUPPLIER_ID)
      if (typeof source?.capacity === 'number') setCapacity(source.capacity)
    } catch (reason) {
      setConnectionError(reason instanceof Error ? reason.message : String(reason))
      throw reason
    }
  }, [])
  useEffect(() => { void refresh().catch(() => undefined) }, [refresh])

  const geo = useMemo(() => buildGeography(snapshot.network, assessment, plan), [snapshot.network, assessment, plan])
  const health = asRecord(snapshot.health)
  const network = asRecord(snapshot.network)
  const counts = asRecord(network?.entities)
  const connected = health?.graph === 'connected' && !connectionError
  const canAct = connected && health?.ready === true && health?.mode === 'SIMULATION'
  const incidents = historyRows(snapshot.history, 'Incident')
  const previous = incidents[0]
  const previousRecovery = !incident && previous?.status === 'RECOVERED'
  const incidentId = firstString(asRecord(incident)?.id, previousRecovery ? undefined : previous?.id)
  const planId = firstString(asRecord(plan)?.id)
  const runId = firstString(asRecord(execution)?.run_id)
  const verified = asRecord(verification)?.verified
  const step = verified === true ? 5 : verified === false ? 2 : execution ? 4 : plan ? 3 : assessment ? 2 : incidentId ? 1 : 0
  const targetOrder = geo.byId.get('ORDER-SILICON-1000')
  const demand = typeof targetOrder?.quantity === 'number' ? targetOrder.quantity : null
  const selectedLocation = geo.locations.find(row => row.id === locationId)
  const selectedRecord = recordId ? geo.byId.get(recordId) : undefined
  const selectedConnection = geo.connections.find(row => row.id === connectionId)
  const filtered = geo.locations.filter(location => `${location.name} ${location.country} ${countryNames.of(location.country)} ${location.records.map(row => recordName(row)).join(' ')}`.toLowerCase().includes(query.toLowerCase()))
  const statusError = error || connectionError

  function selectLocation(id: string, level: MapFocus['level'] = 'region') {
    setLocationId(id); setRecordId(null); setConnectionId(null)
    setFocus(current => ({ locationId: id, level, sequence: (current?.sequence ?? 0) + 1 }))
  }
  function selectRecord(id: string) {
    const reference = geo.located.get(id)
    if (reference) { selectLocation(reference); setRecordId(id) }
  }
  function selectConnection(id: string) {
    const connection = geo.connections.find(row => row.id === id)
    if (connection) { selectLocation(connection.from); setConnectionId(id) }
  }

  async function perform(operation: Operation) {
    if (!canAct || busy) return
    setBusy(working[operation]); setError('')
    try {
      if (operation === 'reset') {
        await api('/demo/reset', 'POST')
        setIncident(null); setAssessment(null); setPlan(null); setExecution(null); setVerification(null)
        setLocationId(null); setRecordId(null); setConnectionId(null); setFocus(null)
      } else if (operation === 'incident') {
        const result = await api('/incidents', 'POST', { scenario_id: SCENARIO_ID, entity_id: INCIDENT_ENTITY_ID, incident_type: 'SUPPLIER_OUTAGE', severity: 5, mode: 'SIMULATION' })
        setIncident(result)
        const reference = geo.located.get(INCIDENT_ENTITY_ID)
        if (reference) setFocus(current => ({ locationId: reference, level: 'region', sequence: (current?.sequence ?? 0) + 1 }))
      } else if (operation === 'assessment') setAssessment(await api(`/incidents/${encodeURIComponent(incidentId!)}/assess?max_depth=8`, 'POST'))
      else if (operation === 'plan') {
        setPlan(await api(`/incidents/${encodeURIComponent(incidentId!)}/plans`, 'POST', { max_iterations: 8 }))
        setExecution(null); setVerification(null)
      } else if (operation === 'execute') setExecution(await api(`/plans/${encodeURIComponent(planId!)}/execute`, 'POST', { mode: 'SIMULATION', idempotency_key: crypto.randomUUID() }))
      else if (operation === 'verify') setVerification(await api(`/runs/${encodeURIComponent(runId!)}/verify`))
      else {
        await api('/simulation/modify', 'POST', { entity_id: INDEPENDENT_SUPPLIER_ID, capacity })
        setPlan(null); setExecution(null); setVerification(null)
      }
      await refresh()
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) }
    finally { setBusy(null) }
  }
  const controls = <RecoveryPanel step={step} busy={busy} canAct={canAct} previousRecovery={previousRecovery} demand={demand}
    onAdvance={() => void perform((['incident', 'assessment', 'plan', 'execute', 'verify'] as Operation[])[step])}
    onReset={() => void perform('reset')} capacity={capacity} onCapacity={setCapacity} onApplyCapacity={() => void perform('capacity')} />

  return <div className="anchor-app">
    <a className="skip-link" href="#main">Skip to workspace</a>
    <header className="app-header"><a className="wordmark" href="#main" onClick={() => setView('network')}><span className="anchor-symbol"><Anchor size={22} strokeWidth={1.6} /></span><span>anchor<span className="wordmark-period">.</span><small>Resilience operations</small></span></a>
      <nav aria-label="Workspace views">{([['network', 'Explore network'], ['recovery', 'Recover orders'], ['evidence', 'Activity & evidence']] as const).map(([key, label]) => <button key={key} aria-current={view === key ? 'page' : undefined} onClick={() => setView(key)}>{label}</button>)}</nav>
      <div className="header-status"><span className="simulation-badge">Simulation</span><span className={`connection-state ${connected ? 'connected' : ''}`}><i />{connected ? 'Graph connected' : connectionError ? 'Connection lost' : 'Connecting'}</span><button className="refresh-button" aria-label="Refresh network data" disabled={Boolean(busy)} onClick={() => { setError(''); void refresh().catch(() => undefined) }}><RefreshCw size={15} /></button></div>
    </header>
    <div className="context-bar"><span>Operations <span className="context-slash">/</span> The Silicon Cascade</span><span>Synthetic manufacturing network <span className="context-slash">·</span> {updated ? `Updated ${updated}` : 'Waiting for data'}</span></div>
    {statusError && <div className="error-banner" role="alert"><div><strong>{connectionError ? 'Live network data is unavailable' : 'This step could not complete'}</strong><p>{statusError}</p>{connectionError && snapshot.network ? <p>The map shows the last loaded snapshot. Recovery actions are disabled.</p> : null}</div><button aria-label="Dismiss operation error" onClick={() => setError('')}><X size={16} /></button></div>}
    <main id="main">
      {view === 'network' && <div className="exploration-workspace">
        <aside className="network-directory" aria-label="Network location directory"><div className="directory-heading"><span className="section-label">Your network</span><h2>A world of dependencies.</h2><p>Select a location to understand what operates there.</p></div>
          <div className="network-totals"><div><strong>{counts?.Supplier === undefined ? '—' : String(counts.Supplier)}</strong><span>suppliers</span></div><div><strong>{geo.locations.length || '—'}</strong><span>locations</span></div><div><strong>{counts?.Order === undefined ? '—' : String(counts.Order)}</strong><span>orders</span></div></div>
          <label className="network-search"><Search size={15} /><span className="sr-only">Find a location or supplier</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Find a location or supplier" />{query && <button aria-label="Clear search" onClick={() => setQuery('')}><X size={13} /></button>}</label>
          <div className="directory-list-heading"><span>Network locations</span><small>{filtered.length}</small></div>
          <ul className="location-directory">{filtered.map(location => <li key={location.id}><button className={`location-button ${locationId === location.id ? 'selected' : ''}`} aria-pressed={locationId === location.id} onClick={() => selectLocation(location.id)}><span className="country-code">{location.country}</span><span><strong>{countryNames.of(location.country) ?? location.name}</strong><small>{location.records.filter(row => recordKind(row) === 'Supplier').length} suppliers · {location.records.filter(row => recordKind(row) === 'Facility').length} facilities</small></span>{location.affected.length ? <span className="location-alert" aria-label="Affected location" /> : <ArrowUpRight size={14} />}</button>
            {query && location.records.filter(row => recordName(row).toLowerCase().includes(query.toLowerCase())).slice(0, 4).map(row => <button key={String(row.id)} className="search-record" onClick={() => selectRecord(String(row.id))}>{recordName(row).replace(' (synthetic)', '')}<ArrowRight size={12} /></button>)}
          </li>)}</ul>
          {!filtered.length && <p className="directory-empty">{snapshot.network ? 'No matching location or supplier. Try another name.' : 'Connect the backend to load the location directory.'}</p>}
          <div className="directory-footnote"><Database size={13} /><span>Records from FalkorDB<br /><small>Commercial relationships are fictional.</small></span></div>
        </aside>
        <div className="map-workspace"><Suspense fallback={<div className="map-loading">Loading Earth explorer…</div>}><EarthExplorer locations={geo.locations} connections={geo.connections} selectedId={locationId} focus={focus} onSelect={selectLocation} onConnection={selectConnection} /></Suspense></div>
        <aside className="mission-inspector" aria-label={selectedLocation ? 'Selected location details' : 'Recovery guide'}>{selectedLocation ? <LocationInspector location={selectedLocation} record={selectedRecord} connection={selectedConnection} network={snapshot.network} byId={geo.byId} assessment={assessment} onRecord={selectRecord} onClose={() => { setLocationId(null); setRecordId(null); setConnectionId(null) }} onCity={() => setFocus(current => ({ locationId: selectedLocation.id, level: 'city', sequence: (current?.sequence ?? 0) + 1 }))} /> : controls}
          {!selectedLocation && Boolean(assessment || plan) && <button className="view-results-button" onClick={() => setView('recovery')}>See impact, plan & results<ArrowRight size={15} /></button>}
        </aside>
      </div>}
      {view === 'recovery' && <div className="recovery-workspace"><div className="recovery-page"><div className="page-intro"><span className="section-label">Order recovery</span><h1>Understand the risk.<br />Follow the recovery.</h1><p>Evidence first, a feasible allocation next, and a result that is checked against the simulated ERP.</p><button className="text-button" onClick={() => setView('network')}><Globe2 size={15} />See the connections on Earth<ArrowUpRight size={13} /></button></div><RecoveryResults plan={plan} assessment={assessment} verification={verification} execution={execution} byId={geo.byId} /></div><aside className="mission-inspector">{controls}</aside></div>}
      {view === 'evidence' && <div className="evidence-workspace"><div className="page-intro"><span className="section-label">Activity & evidence</span><h1>A decision you can inspect.</h1><p>Recent activity is retrieved from the graph. Technical fields are available below when you need them.</p></div>
        <section className="activity-section"><h2>Recent incident activity</h2>{incidents.length ? incidents.map(row => <article className="activity-row" key={String(row.id)}><span className={`activity-marker ${row.status === 'RECOVERED' ? 'good' : ''}`}>{row.status === 'RECOVERED' ? <Check size={16} /> : <Database size={16} />}</span><div><strong>{recordName(geo.byId.get(String(row.entity_id)), String(row.entity_id)).replace(' (synthetic)', '')}</strong><p>{String(row.incident_type ?? 'Recorded incident').replaceAll('_', ' ').toLowerCase()} · {dateLabel(row.created_at)}</p><small>{String(row.id)}</small></div><span className="activity-status">{String(row.status ?? 'Recorded').replaceAll('_', ' ').toLowerCase()}</span></article>) : <div className="composed-empty"><div><strong>No incident history has been returned.</strong><p>Start a scenario in the recovery guide to create an auditable activity trail.</p></div></div>}</section>
        <section className="technical-section"><h2>Graph evidence & operational records</h2><p>FalkorDB snapshot version {String(network?.version ?? 'not loaded')} · {String(network?.entity_count ?? '—')} nodes · {String(network?.relationship_count ?? '—')} relationships. The network response is bounded; the directory lists records returned in this snapshot.</p><JsonPanel title="Incident and dependency assessment" value={assessment} /><JsonPanel title="Recovery plan and tested scenarios" value={plan} /><JsonPanel title="Execution receipts" value={execution} /><JsonPanel title="Verification results" value={verification} /><JsonPanel title="Persisted session history" value={snapshot.history} /><JsonPanel title="Network snapshot and provenance" value={snapshot.network} /></section>
        <button className="text-button" onClick={() => setView('network')}><ArrowLeft size={14} />Back to the network</button>
      </div>}
    </main>
    <footer className="app-footer"><span>Team Nexus <i>·</i> Graph Hacks 2026</span><span>FalkorDB context <i>→</i> constrained recovery <i>→</i> verified simulation</span><span>Simulation only</span></footer>
  </div>
}

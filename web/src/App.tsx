import {
  Activity, AlertTriangle, ArrowDownRight, ArrowRight, Check, CircleDot, Clock3,
  Database, GitBranch, LoaderCircle, Play, RefreshCw, RotateCcw, ShieldCheck,
  SlidersHorizontal, Zap,
} from 'lucide-react'
import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from 'react'
import { api } from './api'
import { asArray, asRecord, entitiesFrom, findString, firstString, historyRows, INCIDENT_ENTITY_ID,
  INDEPENDENT_SUPPLIER_ID, relationshipsFrom, SCENARIO_ID } from './data'
import { JsonPanel } from './JsonPanel'
import type { RecordValue } from './types'

const GlobePanel = lazy(() => import('./GlobePanel').then(module => ({ default: module.GlobePanel })))

type Snapshot = { health: unknown; network: unknown; history: unknown }
type Busy = string | null

function StatusPill({ value }: { value: unknown }) {
  const text = typeof value === 'string' ? value.replaceAll('_', ' ') : 'UNKNOWN'
  const kind = /recover|verified|ready|healthy|success|applied/i.test(text) ? 'good' : /fail|error|reject|review/i.test(text) ? 'bad' : 'neutral'
  return <span className={`status-pill ${kind}`}><i />{text}</span>
}

function Metric({ label, value, icon: Icon }: { label: string; value: unknown; icon: typeof Activity }) {
  return <div className="metric"><span className="metric-label"><Icon size={14} />{label}</span><strong>{value === undefined ? '—' : String(value)}</strong></div>
}

function DataTable({ title, rows, empty, columns }: { title: string; rows: RecordValue[]; empty: string; columns: string[] }) {
  return <div className="table-wrap">
    <table><caption className="sr-only">{title}</caption>
      <thead><tr>{columns.map(key => <th key={key}>{key.replaceAll('_', ' ')}</th>)}</tr></thead>
      <tbody>{rows.map((row, index) => <tr key={String(row.id ?? index)}>{columns.map(key => <td key={key}>{typeof row[key] === 'object' && row[key] !== null ? <code>{JSON.stringify(row[key])}</code> : String(row[key] ?? '—')}</td>)}</tr>)}</tbody>
    </table>
    {!rows.length && <div className="empty-inline">{empty}</div>}
  </div>
}

export default function App() {
  const [snapshot, setSnapshot] = useState<Snapshot>({ health: null, network: null, history: null })
  const [incident, setIncident] = useState<unknown>(null)
  const [assessment, setAssessment] = useState<unknown>(null)
  const [plan, setPlan] = useState<unknown>(null)
  const [execution, setExecution] = useState<unknown>(null)
  const [verification, setVerification] = useState<unknown>(null)
  const [capacity, setCapacity] = useState(450)
  const [busy, setBusy] = useState<Busy>(null)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    const [health, network, history] = await Promise.all([
      api('/health'), api('/network'), api('/history'),
    ])
    setSnapshot({ health, network, history })
    setLastUpdated(new Date().toLocaleTimeString())
  }, [])

  useEffect(() => { refresh().catch(reason => setError(reason instanceof Error ? reason.message : String(reason))) }, [refresh])

  const incidentId = findString(incident, 'id') ?? firstString(historyRows(snapshot.history, 'Incident').at(-1)?.id)
  const planId = findString(plan, 'id')
  const runId = findString(execution, 'run_id')
  const networkRecord = asRecord(snapshot.network)
  const entityRows = useMemo(() => entitiesFrom(snapshot.network), [snapshot.network])
  const relationRows = useMemo(() => relationshipsFrom(snapshot.network), [snapshot.network])
  const healthRecord = asRecord(snapshot.health)
  const mode = firstString(healthRecord?.mode) ?? 'UNKNOWN'
  const incidentStatus = findString(incident, 'status') ?? findString(assessment, 'status')
  const allocations = asArray(asRecord(plan)?.allocations).map(asRecord).filter((row): row is RecordValue => row !== null)
  const receipts = asArray(asRecord(execution)?.receipts).map(asRecord).filter((row): row is RecordValue => row !== null)
  const verifiedAllocations = asArray(asRecord(verification)?.verified_allocations ?? asRecord(verification)?.allocations).map(asRecord).filter((row): row is RecordValue => row !== null)
  const plans = historyRows(snapshot.history, 'RecoveryPlan')
  const actions = historyRows(snapshot.history, 'Action')
  const incidents = historyRows(snapshot.history, 'Incident')
  const activeIncidents = incidents.filter(row => !['RECOVERED', 'VERIFIED'].includes(String(row.status ?? '').toUpperCase()))
  const assessmentRecord = asRecord(assessment)
  const affectedRows = asArray(assessmentRecord?.affected_entities).map(asRecord).filter((row): row is RecordValue => row !== null)
  const pathRows = asArray(assessmentRecord?.shared_dependency_paths).map(asRecord).filter((row): row is RecordValue => row !== null)
  const objective = asRecord(asRecord(plan)?.objective)
  const cost = objective?.incremental_cost_minor
  const unmet = asRecord(asRecord(plan)?.unmet_by_order)
  const shortfall = asRecord(plan)?.remaining_shortfall ?? (unmet ? Object.values(unmet).reduce<number>((sum, value) => sum + (typeof value === 'number' ? value : 0), 0) : asRecord(plan)?.total_shortfall ?? asRecord(plan)?.shortfall)
  const counterexample = asRecord(plan)?.worst_counterexample

  async function operate(label: string, action: () => Promise<unknown>, refreshAfter = true) {
    setBusy(label)
    setError('')
    try {
      const result = await action()
      if (label === 'Reset demo') {
        setIncident(null); setAssessment(null); setPlan(null); setExecution(null); setVerification(null); setCapacity(650)
      } else if (label === 'Trigger incident') setIncident(result)
      else if (label === 'Assess cascade') setAssessment(result)
      else if (label === 'Find recovery plan') { setPlan(result); setExecution(null); setVerification(null) }
      else if (label === 'Execute recovery') setExecution(result)
      else if (label === 'Verify recovery') setVerification(result)
      else if (label === 'Modify capacity') { setPlan(null); setExecution(null); setVerification(null) }
      if (refreshAfter) await refresh()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally { setBusy(null) }
  }

  const canAct = mode === 'SIMULATION'
  const operationButton = (label: string, action: () => Promise<unknown>, icon: typeof Play, disabled = false, primary = false) => {
    const Icon = icon
    return <button className={`action-button${primary ? ' primary' : ''}`} disabled={Boolean(busy) || disabled || !canAct} onClick={() => void operate(label, action)}>
      {busy === label ? <LoaderCircle className="spin" size={15} /> : <Icon size={15} />}{busy === label ? 'Working…' : label}
    </button>
  }

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="#main" aria-label="Anchor operations home"><span className="brand-mark"><Activity size={19} /></span><span>ANCHOR<span className="brand-dot">.</span></span><small>RESILIENCE OPERATIONS</small></a>
      <div className="topbar-right"><span className="environment"><span />{mode} ENVIRONMENT</span><span className="divider" /><button className="icon-button" onClick={() => void operate('Refresh', refresh, false)} disabled={Boolean(busy)} aria-label="Refresh backend state"><RefreshCw size={16} /></button><span className="updated">{lastUpdated ? `Updated ${lastUpdated}` : 'Connecting…'}</span></div>
    </header>

    <main id="main" className="main-content">
      <section className="page-heading">
        <div><div className="eyebrow"><span className="eyebrow-line" />NETWORK RECOVERY / OPERATIONS</div><h1>Recovery <em>under pressure.</em></h1><p>Investigate the cascade. Challenge the recovery. Verify the outcome.</p></div>
        <div className="heading-status"><StatusPill value={mode} /><div className="connection"><span className={healthRecord?.graph === 'connected' || healthRecord?.graph_ready === true ? 'connected' : ''} />FalkorDB · {String(healthRecord?.graph ?? (healthRecord?.graph_ready === true ? 'READY' : 'STATUS UNKNOWN'))}</div></div>
      </section>

      {error && <div className="error-banner" role="alert"><AlertTriangle size={17} /><div><strong>Backend request failed</strong><span>{error}</span></div><button className="icon-button" aria-label="Dismiss error" onClick={() => setError('')}>×</button></div>}

      <section className="metric-grid" aria-label="Live network summary">
        <Metric label="Network nodes" value={networkRecord?.entity_count ?? (entityRows.length || networkRecord?.entities ? Object.values(asRecord(networkRecord?.entities) ?? {}).reduce<number>((sum, value) => sum + (typeof value === 'number' ? value : Array.isArray(value) ? value.length : 0), 0) : undefined)} icon={Database} />
        <Metric label="Relationships" value={networkRecord?.relationship_count ?? networkRecord?.relationships} icon={GitBranch} />
        <Metric label="Active incidents" value={networkRecord?.active_incidents ?? (snapshot.history ? activeIncidents.length : undefined)} icon={AlertTriangle} />
        <Metric label="Graph version" value={networkRecord?.version ?? networkRecord?.graph_version} icon={Activity} />
      </section>

      <section className="workspace-grid">
        <div className="panel network-panel">
          <div className="panel-heading"><div><span className="section-kicker">LIVE TOPOLOGY</span><h2>Connected network</h2></div><span className="panel-meta"><i />Backend data</span></div>
          <Suspense fallback={<div className="globe-loading"><LoaderCircle className="spin" size={18} />Loading network globe…</div>}><GlobePanel network={snapshot.network} /></Suspense>
          <div className="panel-subheading"><span>{entityRows.length ? 'GRAPH ENTITIES' : 'ENTITY COUNTS · SUMMARY ONLY'}</span><b>{entityRows.length ? `${entityRows.length} returned` : 'No individual entity records in API response'}</b></div>
          <DataTable title="Graph entities or entity class counts" rows={entityRows.length ? entityRows.slice(0, 8) : Object.entries(asRecord(networkRecord?.entities) ?? {}).map(([kind, value]) => ({ entity_type: kind, count: typeof value === 'number' ? value : Array.isArray(value) ? value.length : '—' }))} columns={entityRows.length ? Object.keys(entityRows[0]).slice(0, 4) : networkRecord?.entities ? ['entity_type', 'count'] : ['id', 'name', 'type']} empty="The network route returned no entity records or class counts." />
          <div className="panel-subheading"><span>RELATIONSHIPS & PATHS</span><b>{relationRows.length ? `${relationRows.length} returned` : 'No paths returned'}</b></div>
          <DataTable title="Relationships and paths" rows={relationRows.slice(0, 6)} columns={relationRows.length ? Object.keys(relationRows[0]).slice(0, 4) : ['source', 'relationship', 'target']} empty="No relationship records were included in the network response." />
          <div className="panel-subheading"><span>INCIDENT GRAPH EVIDENCE</span><b>{affectedRows.length} affected · {pathRows.length} dependency paths</b></div>
          <DataTable title="Affected graph entities" rows={affectedRows.slice(0, 8)} columns={affectedRows.length ? Object.keys(affectedRows[0]).slice(0, 5) : ['id', 'labels', 'name', 'depth', 'path']} empty="Trigger and assess an incident to retrieve affected graph entities." />
          <DataTable title="Shared upstream dependency paths" rows={pathRows.slice(0, 6)} columns={pathRows.length ? Object.keys(pathRows[0]).slice(0, 4) : ['supplier_id', 'path']} empty="No shared dependency paths were returned for the current assessment." />
          <JsonPanel title="Cascade assessment · affected entities & graph paths" value={assessment} empty="Assess a triggered incident to retrieve affected entities and FalkorDB path evidence." />
          <JsonPanel title="Raw network response" value={snapshot.network} empty="Waiting for GET /api/network." />
        </div>

        <aside className="panel control-panel">
          <div className="panel-heading"><div><span className="section-kicker">CONTROL ROOM</span><h2>Silicon Cascade</h2></div><span className="incident-tag"><CircleDot size={13} />DEMO</span></div>
          <p className="control-intro">Run the synthetic disruption through investigation, stress-aware planning, and verified execution.</p>
          <div className="incident-summary"><div className="incident-icon"><Zap size={18} /></div><div><strong>Upstream foundry failure</strong><span>{INCIDENT_ENTITY_ID} · Severity 5</span></div><StatusPill value={incidentStatus ?? 'STANDBY'} /></div>
          <div className="step-list">
            <div className={`step ${incident ? 'done' : 'current'}`}><span className="step-index">{incident ? <Check size={14} /> : '01'}</span><div><b>Trigger incident</b><small>Create a simulation event</small></div>{operationButton('Trigger incident', () => api('/incidents', 'POST', { scenario_id: SCENARIO_ID, entity_id: INCIDENT_ENTITY_ID, incident_type: 'SUPPLIER_OUTAGE', severity: 5, mode: 'SIMULATION' }), Zap, Boolean(incidentId))}</div>
            <div className={`step ${assessment ? 'done' : incidentId ? 'current' : ''}`}><span className="step-index">{assessment ? <Check size={14} /> : '02'}</span><div><b>Assess cascade</b><small>Trace downstream impact</small></div>{operationButton('Assess cascade', () => api(`/incidents/${encodeURIComponent(incidentId!)}/assess?max_depth=8`, 'POST'), GitBranch, !incidentId)}</div>
            <div className={`step ${plan ? 'done' : assessment ? 'current' : ''}`}><span className="step-index">{plan ? <Check size={14} /> : '03'}</span><div><b>Stress-test & plan</b><small>Compute recovery alternatives</small></div>{operationButton('Find recovery plan', () => api(`/incidents/${encodeURIComponent(incidentId!)}/plans`, 'POST', { max_iterations: 8 }), ShieldCheck, !incidentId)}</div>
            <div className={`step ${execution ? 'done' : planId ? 'current' : ''}`}><span className="step-index">{execution ? <Check size={14} /> : '04'}</span><div><b>Execute in simulation</b><small>Mutate ERP and collect receipts</small></div>{operationButton('Execute recovery', () => api(`/plans/${encodeURIComponent(planId!)}/execute`, 'POST', { mode: 'SIMULATION', idempotency_key: crypto.randomUUID() }), Play, !planId, true)}</div>
            <div className={`step ${verification ? 'done' : runId ? 'current' : ''}`}><span className="step-index">{verification ? <Check size={14} /> : '05'}</span><div><b>Verify postconditions</b><small>Read back operational state</small></div>{operationButton('Verify recovery', () => api(`/runs/${encodeURIComponent(runId!)}/verify`), Check, !runId)}</div>
          </div>

          <div className="capacity-control"><div className="capacity-label"><div><SlidersHorizontal size={15} /><b>Independent supplier capacity</b></div><output htmlFor="capacity">{capacity} units</output></div><label className="sr-only" htmlFor="capacity">Set synthetic independent supplier capacity</label><input id="capacity" type="range" min="0" max="650" step="50" value={capacity} onChange={event => setCapacity(Number(event.target.value))} /><div className="range-markers"><span>0</span><span>650 units</span></div><button className="modify-button" disabled={Boolean(busy) || !canAct} onClick={() => void operate('Modify capacity', () => api('/simulation/modify', 'POST', { entity_id: INDEPENDENT_SUPPLIER_ID, capacity }))}><SlidersHorizontal size={14} />Apply capacity change</button></div>
          <button className="reset-button" disabled={Boolean(busy) || !canAct} onClick={() => void operate('Reset demo', () => api('/demo/reset', 'POST'))}><RotateCcw size={14} />Reset deterministic demo</button>
          {!canAct && <p className="mode-warning" role="status">Actions are disabled because the service did not report SIMULATION mode.</p>}
        </aside>
      </section>

      <section className="results-grid">
        <div className="panel result-panel"><div className="panel-heading"><div><span className="section-kicker">RECOVERY PLAN</span><h2>Allocation & exposure</h2></div>{planId && <span className="mono-id">{planId}</span>}</div>
          <div className="result-metrics"><Metric label="Incremental cost · minor units" value={typeof cost === 'number' ? cost.toLocaleString() : undefined} icon={Activity} /><Metric label="Remaining shortfall" value={shortfall} icon={ArrowDownRight} /><Metric label="Stress suite" value={typeof asRecord(plan)?.stress_passed === 'boolean' ? (asRecord(plan)?.stress_passed ? 'PASSED' : 'COUNTEREXAMPLE') : undefined} icon={ShieldCheck} /></div>
          <DataTable title="Current recovery allocation" rows={allocations} columns={allocations.length ? Object.keys(allocations[0]).slice(0, 6) : ['source', 'order', 'quantity', 'unit price']} empty="No recovery allocation has been returned." />
          {counterexample !== null && counterexample !== undefined && <div className="counterexample"><div className="counterexample-title"><AlertTriangle size={15} />WORST COUNTEREXAMPLE</div><JsonPanel title="Stress-test failure scenario" value={counterexample} /></div>}
          <JsonPanel title="Full stress-test results & objective" value={plan} />
        </div>
        <div className="panel result-panel"><div className="panel-heading"><div><span className="section-kicker">EXECUTION PROOF</span><h2>Receipts & verification</h2></div><StatusPill value={findString(verification, 'status') ?? (asRecord(verification)?.verified === true ? 'VERIFIED' : asRecord(verification)?.verified === false ? 'FAILED' : verification ? 'VERIFICATION RETURNED' : 'PENDING')} /></div>
          <div className="proof-state"><div className="proof-icon"><ShieldCheck size={19} /></div><div><strong>{asRecord(verification)?.verified === true ? 'Read-back verified' : asRecord(verification)?.verified === false ? 'Read-back did not verify' : 'Awaiting independent read-back'}</strong><span>{runId ? `Run ${runId}` : 'Execute the plan to create a verification run.'}</span></div></div>
          <DataTable title="Action receipts" rows={receipts} columns={receipts.length ? Object.keys(receipts[0]).slice(0, 6) : ['action', 'status', 'source', 'order', 'quantity']} empty="No action receipts returned yet." />
          <div className="panel-subheading"><span>VERIFIED ERP POSTCONDITIONS</span><b>{verifiedAllocations.length ? `${verifiedAllocations.length} allocations read back` : 'Not verified'}</b></div>
          <DataTable title="Verified ERP allocations" rows={verifiedAllocations} columns={verifiedAllocations.length ? Object.keys(verifiedAllocations[0]).slice(0, 6) : ['source', 'order', 'quantity', 'status']} empty="Verification details will appear here after GET /api/runs/{run_id}/verify." />
          <JsonPanel title="Verification response" value={verification} />
        </div>
      </section>

      <section className="panel history-panel"><div className="panel-heading"><div><span className="section-kicker">PERSISTENT GRAPH HISTORY</span><h2>Incident timeline</h2></div><span className="panel-meta"><Clock3 size={14} />Retrieved from API</span></div>
        <div className="history-columns"><div><div className="panel-subheading"><span>INCIDENTS</span><b>{incidents.length}</b></div><DataTable title="Incident history" rows={incidents.slice(0, 5)} columns={incidents.length ? Object.keys(incidents[0]).slice(0, 5) : ['id', 'status', 'entity_id', 'created_at']} empty="No persisted incidents returned." /></div><div><div className="panel-subheading"><span>PLANS & ACTIONS</span><b>{plans.length + actions.length}</b></div><DataTable title="Plan and action history" rows={[...plans, ...actions].slice(0, 8)} columns={[...plans, ...actions].length ? Object.keys([...plans, ...actions][0]).slice(0, 5) : ['kind', 'id', 'status', 'created_at']} empty="No persisted plans or actions returned." /></div></div>
        <JsonPanel title="Raw session history" value={snapshot.history} empty="Waiting for GET /api/history." />
      </section>

      <footer><span>ANCHOR <i>·</i> SIMULATION ONLY</span><span><Database size={13} />Live state from the connected service</span><span>STATUS: {healthRecord ? 'CONNECTED' : 'AWAITING SERVICE'} <ArrowRight size={13} /></span></footer>
    </main>
  </div>
}

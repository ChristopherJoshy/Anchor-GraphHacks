import { Check, CircleHelp } from 'lucide-react'
import { asArray, asRecord } from './data'
import { recordName } from './geography'
import type { RecordValue } from './types'

export const money = (minor: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(minor / 100)
export const rows = (value: unknown) => asArray(value).map(asRecord).filter((row): row is RecordValue => row !== null)

interface Props { plan: unknown; assessment: unknown; verification: unknown; execution: unknown; byId: Map<string, RecordValue> }

export function RecoveryResults({ plan, assessment, verification, execution, byId }: Props) {
  const result = asRecord(plan)
  const allocations = rows(result?.allocations)
  const objective = asRecord(result?.objective)
  const unmet = asRecord(result?.unmet_by_order)
  const shortfall = unmet ? Object.values(unmet).reduce<number>((sum, qty) => sum + (typeof qty === 'number' ? qty : 0), 0) : null
  const allocated = allocations.reduce((sum, row) => sum + Number(row.quantity ?? 0), 0)
  const verified = asRecord(verification)?.verified
  const allocationCaption = verified === true ? 'Executed allocations · verified by ERP read-back' : verified === false ? 'Attempted allocation · ERP verification failed' : execution ? 'Submitted allocations · waiting for ERP read-back' : 'Proposed sources · planned, not executed'
  const stressCases = asArray(result?.tested_scenarios)
  const paths = rows(asRecord(assessment)?.shared_dependency_paths)
  const receipts = rows(asRecord(execution)?.receipts)
  return <div className="recovery-results">
    <section className="result-section"><div className="section-heading"><span className="section-label">01 / What is at risk?</span><h2>{assessment ? 'The dependency paths explain the exposure.' : 'Start with the hidden connection.'}</h2></div>
      <p>Two suppliers can look like separate backups while depending on the same failed foundry. Anchor follows the recorded connections before using their capacity.</p>
      {paths.length ? <div className="evidence-paths">{paths.slice(0, 8).map((row, index) => <div className="evidence-path" key={index}><span className="exposure-dot" /><div>{asArray(row.path).map((id, i) => <span key={`${id}:${i}`}>{i > 0 && <b className="path-arrow">depends on</b>}{recordName(byId.get(String(id)), String(id)).replace(' (synthetic)', '')}</span>)}</div><small>Exposed to this incident</small></div>)}</div>
        : <div className="composed-empty"><CircleHelp size={20} /><div><strong>Which backups share the failure?</strong><p>Run “Trace the disruption” to reveal the actual paths from FalkorDB.</p></div></div>}
    </section>
    <section className="result-section"><div className="section-heading"><span className="section-label">{verified === true ? '02 / What Anchor did' : verified === false ? '02 / What Anchor attempted' : execution ? '02 / What Anchor submitted' : '02 / What will Anchor do?'}</span><h2>{plan ? 'A computed allocation, with explicit limits.' : 'The recovery plan will appear here.'}</h2></div>
      {plan ? <><div className="business-metrics"><div><span>Supply allocated</span><strong>{allocated.toLocaleString()}<small> units</small></strong></div><div><span>Still unfilled</span><strong>{shortfall === null ? 'Not reported' : shortfall.toLocaleString()}<small>{shortfall === null ? '' : ' units'}</small></strong></div><div><span>Modeled supply cost</span><strong>{typeof objective?.incremental_cost_minor === 'number' ? money(objective.incremental_cost_minor) : 'Not reported'}</strong></div></div>
      <div className="allocation-track" aria-hidden="true">{allocations.map((row, index) => <span key={index} className={`allocation-color color-${index % 4}`} style={{ flexGrow: Number(row.quantity ?? 0) }} />)}</div>
      <table className="allocation-table"><caption>{allocationCaption}</caption><thead><tr><th>Supply source</th><th>Quantity</th><th>Delivery lead time</th><th>Modeled cost</th></tr></thead><tbody>{allocations.map((row, index) => <tr key={`${row.source_id}:${index}`}><td><i className={`allocation-dot color-${index % 4}`} />{recordName(byId.get(String(row.source_id)), String(row.source_id)).replace(' (synthetic)', '')}</td><td>{Number(row.quantity).toLocaleString()} units</td><td>{row.lead_days === 0 ? 'Existing stock' : `${row.lead_days} days`}</td><td>{money(Number(row.quantity) * Number(row.unit_price_minor))}</td></tr>)}</tbody></table>
      <div className={`stress-summary ${result?.stress_passed === true ? 'good' : 'warning'}`}><strong>{result?.stress_passed === true ? 'Passed the modeled follow-on failures' : 'Residual risk needs attention'}</strong><span>{stressCases.length} declared cases evaluated. This is a bounded simulation, not a guarantee against every future disruption.</span></div></>
        : <div className="composed-empty"><span className="empty-number">∑</span><div><strong>Quantities, cost, and remaining shortage</strong><p>Anchor calculates a feasible allocation from the graph’s qualified supply sources.</p></div></div>}
    </section>
    <section className="result-section"><div className="section-heading"><span className="section-label">03 / Did it work?</span><h2>{verified === true ? 'The simulated changes were read back.' : verified === false ? 'The changes did not pass verification.' : 'A plan is not an execution result.'}</h2></div>
      <div className={`verification-banner ${verified === true ? 'good' : ''}`}><span className="verification-symbol">{verified === true ? <Check size={22} /> : '—'}</span><div><strong>{verified === true ? 'ERP read-back verified' : verified === false ? 'Verification failed · recovery is incomplete' : execution ? 'Applied · waiting for independent read-back' : 'No verified action in this session yet'}</strong><p>{verified === true ? 'Anchor checked persisted operational state against the expected allocations.' : 'Apply the plan, then check the result. Anchor will report the actual outcome.'}</p></div></div>
      {Boolean(execution) && <p className="muted">Execution reported: {String(asRecord(execution)?.status ?? 'No status returned').replaceAll('_', ' ').toLowerCase()} · {receipts.length} receipts returned.</p>}
      {Boolean(verification) && <details className="technical-details"><summary>Inspect the verification response</summary><pre>{JSON.stringify(verification, null, 2)}</pre></details>}
    </section>
  </div>
}

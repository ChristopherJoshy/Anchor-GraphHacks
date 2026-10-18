import { ArrowRight, Check, LoaderCircle, RotateCcw } from 'lucide-react'

const steps = [
  ['Simulate a disruption', 'Introduce an outage at the upstream foundry.'],
  ['Understand the impact', 'Follow the connections to exposed suppliers and orders.'],
  ['Choose a recovery', 'Allocate eligible supply and test further failures.'],
  ['Apply the plan', 'Reserve resources in the local simulated ERP.'],
  ['Verify the result', 'Read the ERP back to check what actually changed.'],
]
const actions = ['Simulate foundry outage', 'Trace the disruption', 'Find a recovery', 'Apply the recovery', 'Check the result']

interface Props {
  step: number
  busy: string | null
  canAct: boolean
  previousRecovery: boolean
  demand: number | null
  onAdvance: () => void
  onReset: () => void
  capacity: number
  onCapacity: (value: number) => void
  onApplyCapacity: () => void
}

export function RecoveryPanel({ step, busy, canAct, previousRecovery, demand, onAdvance, onReset, capacity, onCapacity, onApplyCapacity }: Props) {
  const complete = step === 5
  return <section className="recovery-controls" aria-label="Guided order recovery">
    <span className="section-label">The Silicon Cascade</span>
    <h2>{complete ? 'Recovery checked.' : 'Protect the production order.'}</h2>
    <p className="panel-intro">A foundry outage can expose several suppliers at once. See which alternatives can still deliver.</p>
    <div className="order-brief"><span>Order to protect</span><strong>{demand === null ? 'Loading order…' : `${demand.toLocaleString()} microcontrollers`}</strong><small>Fictional electronics manufacturer · synthetic scenario</small></div>
    <ol className="recovery-steps">{steps.map(([title, description], index) => <li key={title} className={step > index ? 'completed' : step === index ? 'current' : ''} aria-current={step === index ? 'step' : undefined}>
      <span className="step-number">{step > index ? <Check size={13} /> : index + 1}</span><div><strong>{title}</strong><p>{description}</p></div>
    </li>)}</ol>
    {previousRecovery && step === 0 && <p className="inline-notice">A previous run was recovered. Start a fresh scenario to replay the disruption.</p>}
    <button className="primary-button" disabled={!canAct || Boolean(busy)} onClick={complete || previousRecovery && step === 0 ? onReset : onAdvance}>
      {busy ? <LoaderCircle size={16} className="spin" /> : complete ? <RotateCcw size={16} /> : <ArrowRight size={16} />}
      {busy ?? (complete || previousRecovery && step === 0 ? 'Start a fresh scenario' : actions[step])}
    </button>
    {!canAct && <p className="inline-notice">Connect a healthy backend in simulation mode to run this scenario.</p>}
    <p className="simulation-note">All actions change local demo data only. No real orders are placed.</p>
    <details className="scenario-controls"><summary>Change the scenario</summary><div>
      <label htmlFor="supplier-capacity">Independent supplier D capacity<output>{capacity} units</output></label>
      <input id="supplier-capacity" type="range" min="0" max="650" step="50" value={capacity} onChange={event => onCapacity(Number(event.target.value))} />
      <p>Reduce this source to see whether another supplier becomes necessary.</p>
      <button className="secondary-button" disabled={!canAct || Boolean(busy)} onClick={onApplyCapacity}>Apply capacity change</button>
      <button className="text-button" disabled={!canAct || Boolean(busy)} onClick={onReset}><RotateCcw size={13} />Reset the demo</button>
    </div></details>
  </section>
}

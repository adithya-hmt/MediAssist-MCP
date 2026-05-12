'use client'
import { useState } from 'react'
import { DEMO_PATIENT, apiPost } from '../../lib/demo'

type AgentStep = {
  agent_name: string
  action: string
  output_summary: string
  handoff_to: string
  confidence: string
  safety_note: string
}

export default function AgentsPage() {
  const [loading, setLoading] = useState(false)
  const [steps, setSteps] = useState<AgentStep[]>([])
  const [traceId, setTraceId] = useState('')
  const [error, setError] = useState<string | null>(null)

  const AGENT_INITIALS: Record<string, string> = {
    'Intake Agent': 'IN',
    'Safety Agent': 'SA',
    'SHARP Context Agent': 'SC',
    'Triage Support Agent': 'TR',
    'Care Gap Agent': 'CG',
    'FHIR Mapping Agent': 'FM',
    'Handoff Agent': 'HA',
    'Audit Agent': 'AU',
  }

  async function generate() {
    setLoading(true)
    setError(null)
    try {
      const data = await apiPost('/api/agent-replay/generate', DEMO_PATIENT)
      setSteps(data.steps ?? [])
      setTraceId(data.trace_id ?? '')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const confidenceColor = (c: string) => {
    if (c === 'high') return 'tag-green'
    if (c === 'medium') return 'tag-yellow'
    return 'tag-gray'
  }

  return (
    <>
      <div className="page-header">
        <h1>Agent Team Replay</h1>
        <p>Deterministic 8-step multi-agent workflow showing how agents hand off through the care pipeline.</p>
      </div>

      <div className="card">
        <div className="btn-row">
          <button className="btn-primary" onClick={generate} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Agent Replay'}
          </button>
          {traceId && <span className="tag tag-gray" style={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>{traceId}</span>}
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {steps.length > 0 && (
        <div className="card">
          <h2>Agent Timeline</h2>
          {steps.map((step, i) => (
            <div key={i}>
              <div className="agent-step">
                <div className="agent-icon">
                  {AGENT_INITIALS[step.agent_name] ?? step.agent_name.slice(0, 2).toUpperCase()}
                </div>
                <div className="agent-info">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span className="agent-name">{step.agent_name}</span>
                    <span className={`tag ${confidenceColor(step.confidence)}`}>{step.confidence}</span>
                  </div>
                  <div className="agent-action">{step.action}</div>
                  <div className="agent-output">{step.output_summary}</div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.3rem' }}>
                    Safety: {step.safety_note}
                  </div>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#94a3b8', flexShrink: 0, paddingTop: '10px' }}>
                  {step.handoff_to !== 'complete' ? `→ ${step.handoff_to}` : '✓ Done'}
                </div>
              </div>
              {i < steps.length - 1 && (
                <div style={{ textAlign: 'center', color: '#e2e8f0', fontSize: '1rem', margin: '-0.25rem 0' }}>↓</div>
              )}
            </div>
          ))}
          <div className="disclaimer">
            Synthetic demo only. Not medical advice. Clinician review required. No real PHI.
          </div>
        </div>
      )}
    </>
  )
}

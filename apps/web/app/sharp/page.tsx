'use client'
import { useState } from 'react'
import { apiPost } from '../../lib/demo'

const DEFAULT_CONTEXT = JSON.stringify({
  patient_id: "synthetic-patient-001",
  encounter_id: "synthetic-encounter-001",
  user_role: "clinician",
  scopes: ["summarize", "triage_support", "generate_handoff", "create_follow_up_plan", "export_synthetic_fhir_bundle"],
  source: "synthetic-demo"
}, null, 2)

export default function SharpPage() {
  const [context, setContext] = useState(DEFAULT_CONTEXT)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [parseError, setParseError] = useState<string | null>(null)

  async function validate() {
    setParseError(null)
    let parsed: Record<string, unknown>
    try {
      parsed = JSON.parse(context)
    } catch {
      setParseError('Invalid JSON — check your input.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await apiPost('/api/sharp/validate', parsed)
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const valid = result?.context_valid as boolean | undefined
  const missing = result?.missing_fields as string[] | undefined
  const allowed = result?.allowed_actions as string[] | undefined
  const blocked = result?.blocked_actions as string[] | undefined

  return (
    <>
      <div className="page-header">
        <h1>SHARP Context Validation</h1>
        <p>Validate access context fields and determine which actions are allowed or blocked.</p>
      </div>

      <div className="card">
        <h3>Context Input</h3>
        <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.5rem' }}>
          Edit the JSON context below. The pre-filled values represent a valid synthetic demo context.
        </p>
        <textarea
          value={context}
          onChange={e => setContext(e.target.value)}
          rows={10}
          style={{ fontFamily: 'monospace' }}
        />
        {parseError && <div className="error-box">{parseError}</div>}
        <div className="btn-row" style={{ marginTop: '0.75rem' }}>
          <button className="btn-primary" onClick={validate} disabled={loading}>
            {loading ? 'Validating...' : 'Validate Context'}
          </button>
          <button className="btn-secondary" onClick={() => setContext(DEFAULT_CONTEXT)}>Reset to Default</button>
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <h3>Validation Result</h3>
              <span className={`tag ${valid ? 'tag-green' : 'tag-red'}`}>
                {valid ? 'Valid' : 'Invalid'}
              </span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Privacy Status</span>
              <span className="kv-value">{String(result.privacy_status ?? '')}</span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Note</span>
              <span className="kv-value" style={{ fontSize: '0.8rem' }}>{String(result.note ?? '')}</span>
            </div>
            {missing && missing.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', color: '#dc2626', marginBottom: '0.4rem' }}>Missing Fields</div>
                <div className="chip-row">
                  {missing.map((f: string) => <span key={f} className="tag tag-red">{f}</span>)}
                </div>
              </div>
            )}
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>Allowed Actions</h3>
              <div className="chip-row">
                {(allowed ?? []).map((a: string) => <span key={a} className="tag tag-green">{a}</span>)}
              </div>
            </div>
            <div className="card">
              <h3>Blocked Actions</h3>
              <div className="chip-row">
                {(blocked ?? []).map((b: string) => <span key={b} className="tag tag-red">{b}</span>)}
              </div>
            </div>
          </div>

          <div className="disclaimer">
            Synthetic demo only. Not medical advice. Clinician review required. No real PHI.
          </div>
        </>
      )}
    </>
  )
}

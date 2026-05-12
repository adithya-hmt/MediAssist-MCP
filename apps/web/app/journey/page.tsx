'use client'
import { useState } from 'react'
import { DEMO_PATIENT, apiPost } from '../../lib/demo'

export default function JourneyPage() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showRaw, setShowRaw] = useState(false)

  async function run() {
    setLoading(true)
    setError(null)
    try {
      const data = await apiPost('/api/care-journey/run', DEMO_PATIENT)
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  function download() {
    if (!result) return
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'care-journey.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  const journey = result as Record<string, unknown> | null
  const triage = journey?.triage_result as Record<string, unknown> | null
  const safety = journey?.safety_status as Record<string, unknown> | null
  const sharp = journey?.sharp_context_status as Record<string, unknown> | null
  const gaps = journey?.care_gaps as Record<string, unknown> | null
  const followUp = journey?.follow_up_plan as Record<string, unknown> | null
  const audit = journey?.audit_trace as Record<string, unknown> | null
  const fhirResources = journey?.fhir_resources_generated as string[] | null

  return (
    <>
      <div className="page-header">
        <h1>Care Journey</h1>
        <p>Full synthetic care coordination pipeline — privacy gate, triage, care gaps, FHIR, audit.</p>
      </div>

      <div className="card">
        <div className="btn-row">
          <button className="btn-primary" onClick={run} disabled={loading}>
            {loading ? 'Running...' : 'Run Synthetic Care Journey'}
          </button>
          {result && (
            <>
              <button className="btn-secondary" onClick={() => setShowRaw(!showRaw)}>
                {showRaw ? 'Hide Raw JSON' : 'Show Raw JSON'}
              </button>
              <button className="btn-secondary" onClick={download}>Download JSON</button>
            </>
          )}
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <>
          <div className="grid-2">
            <div className="card">
              <h3>Safety Status</h3>
              <div className="kv-row">
                <span className="kv-label">PHI Safe</span>
                <span className={`tag ${safety?.safe_to_process ? 'tag-green' : 'tag-red'}`}>
                  {safety?.safe_to_process ? 'Safe' : 'Blocked'}
                </span>
              </div>
              <div className="kv-row">
                <span className="kv-label">Recommendation</span>
                <span className="kv-value" style={{ fontSize: '0.8rem' }}>{String(safety?.recommendation ?? '')}</span>
              </div>
            </div>
            <div className="card">
              <h3>SHARP Context</h3>
              <div className="kv-row">
                <span className="kv-label">Context Valid</span>
                <span className={`tag ${sharp?.context_valid ? 'tag-green' : 'tag-red'}`}>
                  {sharp?.context_valid ? 'Valid' : 'Invalid'}
                </span>
              </div>
              <div className="kv-row">
                <span className="kv-label">Privacy Status</span>
                <span className="kv-value">{String(sharp?.privacy_status ?? '')}</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Triage Result</h3>
            <div className="grid-2">
              <div>
                <div className="kv-row">
                  <span className="kv-label">Triage Level</span>
                  <span className={`tag tag-yellow`}>{String(triage?.triage_level ?? '')}</span>
                </div>
                <div className="kv-row">
                  <span className="kv-label">Risk Level</span>
                  <span className="kv-value">{String(triage?.risk_level ?? '')}</span>
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.25rem' }}>Risk Flags</div>
                <div className="chip-row">
                  {(triage?.risk_flags as string[] ?? []).map((f: string) => (
                    <span key={f} className="tag tag-yellow">{f}</span>
                  ))}
                  {(triage?.red_flags as string[] ?? []).map((f: string) => (
                    <span key={f} className="tag tag-red">{f}</span>
                  ))}
                </div>
              </div>
            </div>
            {triage?.doctor_handoff_brief ? (
              <div style={{ marginTop: '0.75rem', background: '#f8fafc', padding: '0.75rem', borderRadius: 8, fontSize: '0.8rem', whiteSpace: 'pre-wrap' }}>
                {String(triage.doctor_handoff_brief)}
              </div>
            ) : null}
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>Care Gaps</h3>
              {(gaps?.care_gaps as string[] ?? []).map((g: string, i: number) => (
                <div key={i} className="kv-row">
                  <span style={{ fontSize: '0.8rem' }}>{g}</span>
                </div>
              ))}
              <div className="kv-row">
                <span className="kv-label">Priority</span>
                <span className={`tag ${gaps?.priority === 'high' ? 'tag-red' : 'tag-yellow'}`}>{String(gaps?.priority ?? '')}</span>
              </div>
            </div>
            <div className="card">
              <h3>Follow-up Plan</h3>
              <div className="kv-row">
                <span className="kv-label">Type</span>
                <span className="kv-value">{String(followUp?.recommended_follow_up_type ?? '')}</span>
              </div>
              <div className="kv-row">
                <span className="kv-label">Timeframe</span>
                <span className="kv-value" style={{ fontSize: '0.8rem' }}>{String(followUp?.suggested_timeframe ?? '')}</span>
              </div>
            </div>
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>Doctor Handoff</h3>
              <p style={{ fontSize: '0.8rem', whiteSpace: 'pre-wrap', color: '#334155' }}>{String(journey?.doctor_handoff_brief ?? '')}</p>
            </div>
            <div className="card">
              <h3>Patient Summary</h3>
              <p style={{ fontSize: '0.8rem', color: '#334155' }}>{String(journey?.patient_friendly_summary ?? '')}</p>
            </div>
          </div>

          <div className="grid-2">
            <div className="card">
              <h3>FHIR Resources</h3>
              <div className="chip-row">
                {(fhirResources ?? []).map((r: string) => (
                  <span key={r} className="tag tag-blue">{r}</span>
                ))}
              </div>
              <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>{(fhirResources ?? []).length} resources generated</p>
            </div>
            <div className="card">
              <h3>Audit Trace</h3>
              <div className="kv-row">
                <span className="kv-label">Trace ID</span>
                <span className="kv-value" style={{ fontSize: '0.8rem', fontFamily: 'monospace' }}>{String(audit?.trace_id ?? '')}</span>
              </div>
              <div className="kv-row">
                <span className="kv-label">AI Provider</span>
                <span className="kv-value">{String(audit?.ai_provider_used ?? '')}</span>
              </div>
              <div className="chip-row">
                {(audit?.tools_called as string[] ?? []).map((t: string) => (
                  <span key={t} className="tag tag-gray" style={{ fontSize: '0.65rem' }}>{t}</span>
                ))}
              </div>
            </div>
          </div>

          {showRaw && (
            <div className="card">
              <h3>Raw JSON</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}

          <div className="disclaimer">
            Synthetic demo only. Not medical advice. Clinician review required. No real PHI.
          </div>
        </>
      )}
    </>
  )
}

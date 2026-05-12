'use client'
import { useEffect, useState } from 'react'
import { DEMO_PATIENT, apiGet, apiPost } from '../../lib/demo'

export default function GeminiPage() {
  const [readiness, setReadiness] = useState<Record<string, unknown> | null>(null)
  const [loading, setLoading] = useState(true)
  const [polishing, setPolishing] = useState(false)
  const [polishResult, setPolishResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet('/api/gemini/readiness')
      .then((data: Record<string, unknown>) => setReadiness(data))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function polish() {
    setPolishing(true)
    setError(null)
    try {
      const data = await apiPost('/api/gemini/polish', DEMO_PATIENT)
      setPolishResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setPolishing(false)
    }
  }

  const enabled = readiness?.gemini_enabled as boolean | undefined
  const configured = readiness?.gemini_configured as boolean | undefined
  const safeTocall = readiness?.safe_to_call as boolean | undefined

  return (
    <>
      <div className="page-header">
        <h1>Gemini Assist</h1>
        <p>Optional AI polish for care brief summaries. Disabled by default. Server-side only — no key input here.</p>
      </div>

      {loading && <div className="card"><p style={{ color: '#64748b' }}>Checking Gemini readiness...</p></div>}
      {error && <div className="error-box">{error}</div>}

      {readiness && (
        <div className="card">
          <h3>Gemini Readiness</h3>
          <div className="kv-row">
            <span className="kv-label">Enabled</span>
            <span className={`tag ${enabled ? 'tag-green' : 'tag-gray'}`}>{enabled ? 'Yes' : 'No (default)'}</span>
          </div>
          <div className="kv-row">
            <span className="kv-label">API Key Configured</span>
            <span className={`tag ${configured ? 'tag-green' : 'tag-gray'}`}>{configured ? 'Yes' : 'No'}</span>
          </div>
          <div className="kv-row">
            <span className="kv-label">Safe to Call</span>
            <span className={`tag ${safeTocall ? 'tag-green' : 'tag-gray'}`}>{safeTocall ? 'Yes' : 'No'}</span>
          </div>
          <div className="kv-row">
            <span className="kv-label">Status</span>
            <span className="kv-value">{String(readiness.status ?? '')}</span>
          </div>
          <div className="kv-row">
            <span className="kv-label">Model</span>
            <span className="kv-value">{String(readiness.default_model ?? '')}</span>
          </div>
          <div className="kv-row">
            <span className="kv-label">Mode</span>
            <span className="kv-value">{String(readiness.model_mode ?? '')}</span>
          </div>
          {readiness.note ? (
            <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: '#64748b' }}>{String(readiness.note)}</div>
          ) : null}
        </div>
      )}

      <div className="card">
        <h3>Polish Handoff Summary</h3>
        <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '0.75rem' }}>
          Generates a care brief locally, then optionally polishes the prose with Gemini (if enabled).
          Falls back to local deterministic output when Gemini is not configured.
        </p>
        <button className="btn-primary" onClick={polish} disabled={polishing}>
          {polishing ? 'Generating...' : 'Polish Handoff Summary'}
        </button>
        {error && <div className="error-box">{error}</div>}
      </div>

      {polishResult && (
        <>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <h3>Result</h3>
              <span className={`tag ${polishResult.ai_provider_used ? 'tag-green' : 'tag-gray'}`}>
                {polishResult.ai_provider_used ? `Gemini: ${polishResult.ai_model}` : 'Local Fallback'}
              </span>
            </div>
            <div className="kv-row">
              <span className="kv-label">AI Provider</span>
              <span className="kv-value">{String(polishResult.ai_provider ?? '')}</span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Status</span>
              <span className="kv-value">{String(polishResult.ai_provider_status ?? '')}</span>
            </div>
            {polishResult.patient_summary ? (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>Patient Summary</div>
                <p style={{ fontSize: '0.8rem', color: '#334155' }}>{String(polishResult.patient_summary)}</p>
              </div>
            ) : null}
            {polishResult.doctor_handoff_brief ? (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>Doctor Handoff Brief</div>
                <p style={{ fontSize: '0.8rem', color: '#334155', whiteSpace: 'pre-wrap' }}>{String(polishResult.doctor_handoff_brief)}</p>
              </div>
            ) : null}
          </div>
          <div className="disclaimer">
            No Gemini API key is accepted from the frontend. Keys are server-side only (GEMINI_API_KEY env var).
            Synthetic demo only. Not medical advice. Clinician review required.
          </div>
        </>
      )}
    </>
  )
}

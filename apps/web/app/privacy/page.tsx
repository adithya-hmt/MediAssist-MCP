'use client'
import { useState } from 'react'
import { apiPost } from '../../lib/demo'

const SAMPLE_TEXT = `Patient name: John Doe, DOB: 01/01/1980
Contact: john.doe@example.com, Phone: 555-123-4567
MRN: 1234567890123456
This is a synthetic demo text with fake PHI-like strings for testing.`

export default function PrivacyPage() {
  const [text, setText] = useState(SAMPLE_TEXT)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function check() {
    setLoading(true)
    setError(null)
    try {
      const data = await apiPost('/api/privacy/check', { text })
      setResult(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const safe = result?.safe_to_process as boolean | undefined
  const risks = result?.detected_risks as string[] | undefined
  const redacted = result?.redacted_preview as string | undefined

  return (
    <>
      <div className="page-header">
        <h1>Privacy & PHI Safety</h1>
        <p>Deterministic regex-based PHI detection. No LLM required. All checks run locally.</p>
      </div>

      <div className="card">
        <h3>Sample Text</h3>
        <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.5rem' }}>
          Pre-filled with fake PHI-like strings for demonstration. Edit to test your own synthetic text.
        </p>
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          rows={6}
        />
        <div className="btn-row" style={{ marginTop: '0.75rem' }}>
          <button className="btn-primary" onClick={check} disabled={loading || !text.trim()}>
            {loading ? 'Checking...' : 'Check Safety'}
          </button>
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {result && (
        <>
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <h3>Safety Result</h3>
              <span className={`tag ${safe ? 'tag-green' : 'tag-red'}`}>
                {safe ? 'Safe to Process' : 'Blocked — PHI Detected'}
              </span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Recommendation</span>
              <span className="kv-value" style={{ fontSize: '0.8rem' }}>{String(result.recommendation ?? '')}</span>
            </div>
            {risks && risks.length > 0 && (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.4rem' }}>Detected Risks</div>
                <div className="chip-row">
                  {risks.map((r: string) => (
                    <span key={r} className="tag tag-red">{r}</span>
                  ))}
                </div>
              </div>
            )}
            {risks && risks.length === 0 && (
              <div className="success-box">No PHI patterns detected in the provided text.</div>
            )}
          </div>

          {redacted && (
            <div className="card">
              <h3>Redacted Preview</h3>
              <pre>{redacted}</pre>
            </div>
          )}

          <div className="disclaimer">
            PHI check is deterministic — no AI/LLM is used. Patterns: email, phone, URL, Aadhaar/12-digit IDs, credit card numbers, API tokens, MRNs.
            Synthetic demo only. Not medical advice. Clinician review required.
          </div>
        </>
      )}
    </>
  )
}

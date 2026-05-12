'use client'
import { useState } from 'react'
import { DEMO_PATIENT, apiPost } from '../../lib/demo'

type FhirResource = Record<string, unknown>
type FhirEntry = { resource: FhirResource }

export default function FhirPage() {
  const [loading, setLoading] = useState(false)
  const [bundle, setBundle] = useState<Record<string, unknown> | null>(null)
  const [expanded, setExpanded] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)

  async function exportBundle() {
    setLoading(true)
    setError(null)
    try {
      const data = await apiPost('/api/fhir/export', DEMO_PATIENT)
      setBundle(data)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  function download() {
    if (!bundle) return
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'fhir-bundle.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  function toggleExpand(i: number) {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i)
      else next.add(i)
      return next
    })
  }

  const entries: FhirEntry[] = (bundle?.entry as FhirEntry[]) ?? []
  const resourceTypes = entries.map(e => e.resource?.resourceType as string)

  return (
    <>
      <div className="page-header">
        <h1>FHIR Bundle Viewer</h1>
        <p>Export a synthetic FHIR-style bundle from the demo patient case.</p>
      </div>

      <div className="card">
        <div className="btn-row">
          <button className="btn-primary" onClick={exportBundle} disabled={loading}>
            {loading ? 'Exporting...' : 'Export FHIR Bundle'}
          </button>
          {bundle && <button className="btn-secondary" onClick={download}>Download JSON</button>}
        </div>
        {error && <div className="error-box">{error}</div>}
      </div>

      {bundle && (
        <>
          <div className="card">
            <h3>Bundle Overview</h3>
            <div className="kv-row">
              <span className="kv-label">Resource Type</span>
              <span className="kv-value">{String(bundle.resourceType ?? '')}</span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Bundle Type</span>
              <span className="kv-value">{String(bundle.type ?? '')}</span>
            </div>
            <div className="kv-row">
              <span className="kv-label">Total Resources</span>
              <span className="kv-value">{entries.length}</span>
            </div>
            <div className="chip-row">
              {resourceTypes.map((rt, i) => (
                <span key={i} className="tag tag-blue">{rt}</span>
              ))}
            </div>
          </div>

          <div className="card">
            <h3>Resources</h3>
            {entries.map((entry, i) => {
              const res = entry.resource
              const rt = String(res?.resourceType ?? `Resource ${i}`)
              const rid = String(res?.id ?? '')
              return (
                <div key={i} className="fhir-resource">
                  <div className="fhir-resource-header" onClick={() => toggleExpand(i)}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="tag tag-blue">{rt}</span>
                      {rid && <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#64748b' }}>{rid}</span>}
                    </div>
                    <span style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{expanded.has(i) ? '▲' : '▼'}</span>
                  </div>
                  {expanded.has(i) && (
                    <div className="fhir-resource-body">
                      <pre>{JSON.stringify(res, null, 2)}</pre>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          <div className="disclaimer">
            FHIR-style demo mapping only. Not certified clinical FHIR. Synthetic demo only. Not medical advice. Clinician review required. No real PHI.
          </div>
        </>
      )}
    </>
  )
}

import Link from 'next/link'

const features = [
  { title: 'MCP Tools', desc: '10 deterministic tools for care workflows', href: '/mcp-tools', textColor: '#1d4ed8', bg: '#dbeafe' },
  { title: 'PHI Safety', desc: 'Regex-based PHI detection and redaction', href: '/privacy', textColor: '#15803d', bg: '#dcfce7' },
  { title: 'SHARP Context', desc: 'Access control validation for clinical actions', href: '/sharp', textColor: '#a16207', bg: '#fef9c3' },
  { title: 'Care Journey', desc: 'End-to-end synthetic care coordination', href: '/journey', textColor: '#7c3aed', bg: '#ede9fe' },
  { title: 'FHIR Bundle', desc: 'Synthetic FHIR-style resource export', href: '/fhir', textColor: '#be185d', bg: '#fce7f3' },
  { title: 'Audit Trace', desc: 'Full compliance trail for every workflow run', href: '/agents', textColor: '#c2410c', bg: '#fff7ed' },
]

export default function OverviewPage() {
  return (
    <>
      <div className="hero-banner">
        <h1>Cerelytic MediAssist</h1>
        <p>Interoperable Healthcare Agent Workspace — synthetic-only, PHI-safe, clinician-first</p>
        <div className="btn-row">
          <Link href="/journey">
            <button className="btn-primary" style={{ background: 'white', color: '#0ea5e9' }}>Run Demo</button>
          </Link>
          <Link href="/fhir">
            <button className="btn-secondary" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.4)' }}>View FHIR Bundle</button>
          </Link>
          <Link href="/privacy">
            <button className="btn-secondary" style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.4)' }}>Check Safety</button>
          </Link>
        </div>
        <div className="hero-feature-grid">
          <div className="hero-feature"><h3>Synthetic Only</h3><p>No real patient data — PHI-safe by design</p></div>
          <div className="hero-feature"><h3>MCP Protocol</h3><p>10 tools via Model Context Protocol</p></div>
          <div className="hero-feature"><h3>FHIR-style Output</h3><p>Structured bundles for interoperability</p></div>
          <div className="hero-feature"><h3>SHARP Context</h3><p>Clinical access control validation</p></div>
          <div className="hero-feature"><h3>Agent Replay</h3><p>8-step deterministic multi-agent workflow</p></div>
          <div className="hero-feature"><h3>Audit Trail</h3><p>Full compliance trace for every run</p></div>
        </div>
      </div>

      <div className="page-header">
        <h1>Explore the Workspace</h1>
        <p>Each module demonstrates a key capability of the healthcare agent system.</p>
      </div>

      <div className="grid-3">
        {features.map(f => (
          <Link key={f.title} href={f.href} style={{ textDecoration: 'none' }}>
            <div className="card" style={{ cursor: 'pointer', borderTop: `4px solid ${f.textColor}` }}>
              <div style={{ display: 'inline-block', background: f.bg, color: f.textColor, padding: '0.25rem 0.625rem', borderRadius: 6, fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                {f.title}
              </div>
              <p style={{ fontSize: '0.875rem', color: '#64748b' }}>{f.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <div className="disclaimer">
        Synthetic demo only. Not medical advice. Clinician review required. No real PHI is used in this system.
      </div>
    </>
  )
}

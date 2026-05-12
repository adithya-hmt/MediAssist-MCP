'use client';

import { useMemo, useState } from 'react';

type JourneyResult = Record<string, any>;

type PanelPayload = {
  cases: any[];
  journey: JourneyResult | null;
  fhir: any | null;
  safety: any | null;
  audit: any | null;
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8012';

const metrics = [
  { label: 'Synthetic-only', value: 'PHI-safe', note: 'No real patient data' },
  { label: 'Workflow', value: 'MCP → FHIR', note: 'Deterministic demo path' },
  { label: 'Evidence', value: 'Audit trail', note: 'Traceable handoffs' },
  { label: 'Safety', value: 'SHARP', note: 'Clinical guardrails' },
];

const timeline = [
  { step: '01', title: 'Intake', text: 'Synthetic case is selected, normalized, and queued.' },
  { step: '02', title: 'Coordination', text: 'MCP workflow produces a care brief and action plan.' },
  { step: '03', title: 'FHIR bundle', text: 'Structured bundle is generated for interoperability.' },
  { step: '04', title: 'Safety review', text: 'PHI and SHARP checks gate the release.' },
];

const modules = [
  { title: 'MCP tools', subtitle: 'Backend capability', x: 14, y: 18 },
  { title: 'Care brief', subtitle: 'Clinician handoff', x: 72, y: 9 },
  { title: 'FHIR bundle', subtitle: 'Interoperable output', x: 82, y: 62 },
  { title: 'Safety', subtitle: 'PHI + SHARP', x: 18, y: 67 },
];

export default function Page() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('Idle');
  const [error, setError] = useState<string | null>(null);
  const [payload, setPayload] = useState<PanelPayload>({ cases: [], journey: null, fhir: null, safety: null, audit: null });

  const summary = useMemo(() => {
    const entries = payload.fhir?.entry?.length ?? 0;
    return [
      { label: 'Case', value: payload.cases[0]?.id || '—' },
      { label: 'Journey', value: payload.journey?.request_id || '—' },
      { label: 'FHIR entries', value: String(entries) },
      { label: 'Audit trace', value: payload.audit?.request_id || '—' },
    ];
  }, [payload]);

  async function run() {
    try {
      setLoading(true);
      setError(null);
      setStatus('Fetching synthetic case...');

      const casesRes = await fetch(`${API}/api/cases`);
      const casesJson = await casesRes.json();
      const caseData = casesJson.items?.[0] ?? casesJson[0] ?? null;
      if (!caseData) throw new Error('No synthetic cases returned');

      setStatus('Generating care journey...');
      const journey = await (await fetch(`${API}/api/workflows/journey`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(caseData),
      })).json();

      setStatus('Building FHIR bundle...');
      const fhir = await (await fetch(`${API}/api/fhir/bundle`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(caseData),
      })).json();

      setStatus('Running safety checks...');
      const safety = await (await fetch(`${API}/api/safety/phi`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(caseData),
      })).json();

      setStatus('Writing audit trace...');
      const audit = await (await fetch(`${API}/api/audit`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(journey),
      })).json();

      setPayload({ cases: casesJson.items || [caseData], journey, fhir, safety, audit });
      setStatus('Complete');
    } catch (err: any) {
      setError(err?.message || 'Something failed');
      setStatus('Failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <div className="orb orb-a" />
      <div className="orb orb-b" />
      <div className="orb orb-c" />

      <section className="hero-card">
        <nav className="topbar">
          <div className="brand">
            <div className="brand-mark">C</div>
            <div>
              <div className="brand-title">Cerelytic MediAssist-MCP</div>
              <div className="brand-subtitle">Synthetic-only healthcare workflow platform</div>
            </div>
          </div>
          <div className="nav-pills">
            <span>MCP</span><span>FHIR</span><span>Safety</span><span>Audit</span>
          </div>
        </nav>

        <div className="hero-grid">
          <div className="copy-col">
            <div className="eyebrow"><span /> First-prize demo build</div>
            <h1>Command-center UI for synthetic care workflows.</h1>
            <p className="lede">
              Turn one synthetic case into a clinician-ready brief, structured FHIR output,
              safety validation, and an auditable workflow trail — all in a polished product shell.
            </p>

            <div className="cta-row">
              <button className="primary-btn" onClick={run} disabled={loading}>
                {loading ? 'Running…' : 'Run full journey'}
              </button>
              <a className="secondary-btn" href="#panels">Inspect output</a>
            </div>

            <div className="metric-grid">
              {metrics.map((m) => (
                <article className="metric-card" key={m.label}>
                  <span>{m.label}</span>
                  <strong>{m.value}</strong>
                  <p>{m.note}</p>
                </article>
              ))}
            </div>

            <div className="demo-band">
              <div className="demo-band-label">Demo pulse</div>
              <div className="demo-band-track">
                <span />
                <span />
                <span />
                <span />
              </div>
              <div className="demo-band-copy">Synthetic case → workflow engine → FHIR → safety → audit</div>
            </div>
          </div>

          <div className="visual-col" aria-label="Workflow illustration">
            <div className="visual-stage">
              <div className="scanner" />
              <div className="scanline" />
              <div className="hero-glow hero-glow-a" />
              <div className="hero-glow hero-glow-b" />
              <div className="dashboard-mock">
                <div className="dashboard-top">
                  <span className="dot red" /><span className="dot amber" /><span className="dot green" />
                  <strong>Live workflow cockpit</strong>
                </div>
                <div className="dashboard-body">
                  <div className="dashboard-left">
                    <div className="stack-card stack-a"><b>12</b><span>clinical signals</span></div>
                    <div className="stack-card stack-b"><b>FHIR</b><span>structured bundle</span></div>
                    <div className="stack-card stack-c"><b>SAFE</b><span>privacy review</span></div>
                  </div>
                  <div className="dashboard-right">
                    <div className="viz-row"><span style={{width:'28%'}} /><span style={{width:'52%'}} /><span style={{width:'36%'}} /></div>
                    <div className="viz-row"><span style={{width:'66%'}} /><span style={{width:'24%'}} /><span style={{width:'48%'}} /></div>
                    <div className="viz-row"><span style={{width:'40%'}} /><span style={{width:'74%'}} /><span style={{width:'18%'}} /></div>
                    <div className="viz-grid">
                      <div />
                      <div />
                      <div />
                      <div />
                    </div>
                  </div>
                </div>
              </div>
               {modules.map((m) => (
                 <div className="floating-chip" key={m.title} style={{ left: `${m.x}%`, top: `${m.y}%` }}>
-                  <span>{m.title}</span>
-                  <small>{m.subtitle}</small>
+                  <span className="chip-title">{m.title}</span>
+                  <small className="chip-subtitle">{m.subtitle}</small>
                 </div>
               ))}
              <div className="center-shield">
                <div className="shield-core">
                  <div className="plus" />
                </div>
                <div className="center-label">
                  <strong>SHARP</strong>
                  <span>Safety gate</span>
                </div>
              </div>
              <div className="data-ring data-ring-a" />
              <div className="data-ring data-ring-b" />
              <div className="status-puck puck-a"><b>10</b><span>FHIR entries</span></div>
              <div className="status-puck puck-b"><b>OK</b><span>PHI check</span></div>
              <div className="status-puck puck-c"><b>Trace</b><span>Audit record</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="content-grid" id="panels">
        <section className="panel glass tall">
          <div className="panel-head"><div><p>Workflow map</p><h2>How the system moves.</h2></div><div className="live-dot">Live demo</div></div>
          <div className="timeline">{timeline.map((item) => (<article className="timeline-item" key={item.step}><div className="timeline-step">{item.step}</div><div><h3>{item.title}</h3><p>{item.text}</p></div></article>))}</div>
        </section>

        <section className="panel glass">
          <div className="panel-head"><div><p>Control room</p><h2>Run state</h2></div></div>
          <div className="state-stack">
            <div className="state-row"><span>Status</span><strong>{status}</strong></div>
            <div className="state-row"><span>API</span><strong>{API}</strong></div>
            <div className="state-row"><span>Mode</span><strong>Synthetic-only</strong></div>
            <div className="state-row"><span>Guardrails</span><strong>PHI-safe</strong></div>
          </div>
          <div className="mini-chart">
            <span style={{ height: '42%' }} />
            <span style={{ height: '72%' }} />
            <span style={{ height: '58%' }} />
            <span style={{ height: '86%' }} />
          </div>
          {error ? <div className="error-box">{error}</div> : null}
        </section>

        <section className="panel glass wide" aria-live="polite">
          <div className="panel-head">
            <div>
              <p>Output</p>
              <h2>Journey + FHIR + Safety + Audit</h2>
            </div>
            <div className="mini-stats">
              {summary.map((item) => (
                <div key={item.label}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="result-grid">
            <article className="result-card result-highlight">
              <div className="result-header"><span>Journey summary</span><strong>{payload.journey?.request_id || 'Waiting'}</strong></div>
              <div className="result-facts">
                <div><small>Case</small><b>{payload.cases[0]?.id || '—'}</b></div>
                <div><small>FHIR resources</small><b>{payload.fhir?.entry?.length ?? 0}</b></div>
                <div><small>Safety</small><b>{payload.safety?.status || '—'}</b></div>
                <div><small>Audit</small><b>{payload.audit?.request_id || '—'}</b></div>
              </div>
              <div className="result-progress"><span /><span /><span /></div>
              <div className="log-view">
                <div><b>01</b><span>synthetic intake accepted</span></div>
                <div><b>02</b><span>care brief drafted</span></div>
                <div><b>03</b><span>FHIR bundle staged</span></div>
                <div><b>04</b><span>audit trace written</span></div>
              </div>
              <details>
                <summary>Raw journey JSON</summary>
                <pre>{payload.journey ? JSON.stringify(payload.journey, null, 2) : 'Click “Run full journey” to generate a care brief.'}</pre>
              </details>
            </article>
            <article className="result-card result-highlight alt">
              <div className="result-header"><span>Interoperability + governance</span><strong>{payload.fhir?.resourceType || 'FHIR Bundle'}</strong></div>
              <div className="result-facts two-col">
                <div><small>Bundle</small><b>{payload.fhir?.entry?.length ?? 0} entries</b></div>
                <div><small>Safety trace</small><b>{payload.safety?.status || '—'}</b></div>
                <div><small>Audit</small><b>{payload.audit?.request_id || '—'}</b></div>
                <div><small>Mode</small><b>Synthetic-only</b></div>
              </div>
              <div className="glass-note">Polished, privacy-first demo shell with live backend rendering.</div>
              <div className="bundle-preview">
                <div className="bundle-chip">Patient</div>
                <div className="bundle-chip">Encounter</div>
                <div className="bundle-chip">Observation</div>
                <div className="bundle-chip">Medication</div>
                <div className="bundle-chip">AuditEvent</div>
                <div className="bundle-chip">Consent</div>
              </div>
              <details>
                <summary>Raw interoperability JSON</summary>
                <pre>{payload.fhir || payload.safety || payload.audit ? JSON.stringify({ fhir: payload.fhir, safety: payload.safety, audit: payload.audit }, null, 2) : 'Waiting for the workflow to complete.'}</pre>
              </details>
            </article>
          </div>
        </section>
      </section>
    </main>
  );
}

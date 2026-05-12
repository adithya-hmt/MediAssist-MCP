'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const links = [
  { href: '/', label: 'Overview' },
  { href: '/journey', label: 'Care Journey' },
  { href: '/agents', label: 'Agent Replay' },
  { href: '/fhir', label: 'FHIR Bundle' },
  { href: '/privacy', label: 'Privacy & PHI' },
  { href: '/sharp', label: 'SHARP Context' },
  { href: '/mcp-tools', label: 'MCP Tools' },
  { href: '/gemini', label: 'Gemini Assist' },
  { href: '/checklist', label: 'Submission' },
]

export function Nav() {
  const pathname = usePathname()
  return (
    <div>
      <div className="brand-logo">
        <div className="brand-mark">C</div>
        <div>
          <div className="brand-name">Cerelytic</div>
          <div className="brand-sub">MediAssist</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {links.map(l => (
          <Link key={l.href} href={l.href} style={{
            display: 'block',
            padding: '0.5rem 0.75rem',
            borderRadius: 8,
            textDecoration: 'none',
            color: pathname === l.href ? '#0ea5e9' : '#334155',
            background: pathname === l.href ? '#f0f9ff' : 'transparent',
            fontWeight: pathname === l.href ? 600 : 400,
            fontSize: '0.875rem',
            transition: 'background 0.1s',
          }}>{l.label}</Link>
        ))}
      </div>
      <div style={{ marginTop: 'auto', paddingTop: '2rem', fontSize: '0.7rem', color: '#94a3b8' }}>
        Synthetic demo only.<br />Not medical advice.
      </div>
    </div>
  )
}

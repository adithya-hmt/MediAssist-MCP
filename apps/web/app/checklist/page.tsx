'use client'
import { useState } from 'react'

type CheckItem = { id: string; label: string }
type Section = { title: string; items: CheckItem[] }

const SECTIONS: Section[] = [
  {
    title: 'Devpost Submission',
    items: [
      { id: 'dp1', label: 'Project title: Cerelytic MediAssist' },
      { id: 'dp2', label: 'Short description submitted' },
      { id: 'dp3', label: 'Team members listed' },
      { id: 'dp4', label: 'GitHub repository linked' },
      { id: 'dp5', label: 'Demo video URL submitted' },
      { id: 'dp6', label: 'Hackathon track selected (Healthcare AI)' },
      { id: 'dp7', label: 'All required fields completed' },
      { id: 'dp8', label: 'Submitted before deadline' },
    ],
  },
  {
    title: 'Prompt / AI Usage Opinion',
    items: [
      { id: 'po1', label: 'Care brief prompt: SBAR-style, deterministic' },
      { id: 'po2', label: 'Privacy prompt: PHI detection, no LLM' },
      { id: 'po3', label: 'SHARP context prompt: access control validation' },
      { id: 'po4', label: 'FHIR export: structured bundle generation' },
      { id: 'po5', label: 'Agent replay: 8-step deterministic pipeline' },
      { id: 'po6', label: 'Gemini: optional polish, disabled by default' },
    ],
  },
  {
    title: 'Safety & Compliance',
    items: [
      { id: 'sc1', label: 'All patient data is synthetic — no real PHI' },
      { id: 'sc2', label: 'PHI safety check gates every workflow run' },
      { id: 'sc3', label: 'SHARP context validation enforced' },
      { id: 'sc4', label: 'All outputs include clinical disclaimers' },
      { id: 'sc5', label: 'Gemini disabled by default — requires explicit env var' },
      { id: 'sc6', label: 'Audit trail generated for every run' },
    ],
  },
  {
    title: 'Demo Video Checklist',
    items: [
      { id: 'dv1', label: 'Overview page / hero shown' },
      { id: 'dv2', label: 'Care Journey run demonstrated end-to-end' },
      { id: 'dv3', label: 'Agent Team Replay walkthrough shown' },
      { id: 'dv4', label: 'FHIR Bundle export demonstrated' },
      { id: 'dv5', label: 'Privacy check with PHI detection shown' },
    ],
  },
]

export default function ChecklistPage() {
  const allIds = SECTIONS.flatMap(s => s.items.map(i => i.id))
  const [checked, setChecked] = useState<Set<string>>(new Set())

  function toggle(id: string) {
    setChecked(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function toggleSection(section: Section) {
    const sectionIds = section.items.map(i => i.id)
    const allChecked = sectionIds.every(id => checked.has(id))
    setChecked(prev => {
      const next = new Set(prev)
      if (allChecked) sectionIds.forEach(id => next.delete(id))
      else sectionIds.forEach(id => next.add(id))
      return next
    })
  }

  const percent = Math.round((checked.size / allIds.length) * 100)

  return (
    <>
      <div className="page-header">
        <h1>Submission Checklist</h1>
        <p>Track your hackathon submission readiness. Progress is saved in browser state.</p>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
          <h3>Overall Progress</h3>
          <span style={{ fontWeight: 700, color: percent === 100 ? '#15803d' : '#0ea5e9', fontSize: '1.25rem' }}>{percent}%</span>
        </div>
        <div className="progress-bar-bg">
          <div className="progress-bar-fill" style={{ width: `${percent}%` }} />
        </div>
        <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{checked.size} of {allIds.length} items complete</p>
        <div className="btn-row" style={{ marginTop: '0.75rem' }}>
          <button className="btn-secondary" onClick={() => setChecked(new Set(allIds))}>Check All</button>
          <button className="btn-secondary" onClick={() => setChecked(new Set())}>Uncheck All</button>
        </div>
      </div>

      {SECTIONS.map(section => {
        const sectionIds = section.items.map(i => i.id)
        const sectionChecked = sectionIds.filter(id => checked.has(id)).length
        const allDone = sectionChecked === sectionIds.length
        return (
          <div key={section.title} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3>{section.title}</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className={`tag ${allDone ? 'tag-green' : 'tag-gray'}`}>{sectionChecked}/{sectionIds.length}</span>
                <button
                  className="btn-secondary"
                  style={{ padding: '0.25rem 0.625rem', fontSize: '0.75rem' }}
                  onClick={() => toggleSection(section)}
                >
                  {allDone ? 'Uncheck All' : 'Check All'}
                </button>
              </div>
            </div>
            {section.items.map(item => (
              <label key={item.id} className="checklist-item" style={{ cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={checked.has(item.id)}
                  onChange={() => toggle(item.id)}
                />
                <span className={`checklist-label ${checked.has(item.id) ? 'checked' : ''}`}>
                  {item.label}
                </span>
              </label>
            ))}
          </div>
        )
      })}

      {percent === 100 && (
        <div className="success-box" style={{ textAlign: 'center', padding: '1.5rem', borderRadius: 12 }}>
          All items checked. Good luck with the submission!
        </div>
      )}
    </>
  )
}

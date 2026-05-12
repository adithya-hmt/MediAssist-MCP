'use client'
import { useEffect, useState } from 'react'
import { apiGet } from '../../lib/demo'

type Tool = {
  name: string
  description: string
  input: string
  output: string
  demo_relevance: string
}

export default function McpToolsPage() {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet('/api/mcp/tools')
      .then((data: { tools: Tool[] }) => setTools(data.tools ?? []))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <>
      <div className="page-header">
        <h1>MCP Tools</h1>
        <p>All {tools.length} Model Context Protocol tools available in the Cerelytic MediAssist server.</p>
      </div>

      {loading && <div className="card"><p style={{ color: '#64748b' }}>Loading tools...</p></div>}
      {error && <div className="error-box">{error}</div>}

      {!loading && !error && (
        <div className="grid-2">
          {tools.map(tool => (
            <div key={tool.name} className="tool-card">
              <div className="tool-name">{tool.name}</div>
              <div className="tool-desc">{tool.description}</div>
              <div className="tool-meta">
                <span className="tag tag-blue" style={{ fontSize: '0.7rem' }}>in: {tool.input}</span>
                <span className="tag tag-green" style={{ fontSize: '0.7rem' }}>out: {tool.output}</span>
              </div>
              <div style={{ marginTop: '0.5rem' }}>
                <span className="tag tag-yellow">{tool.demo_relevance}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="disclaimer">
        Tools are deterministic and run locally without external AI calls (unless Gemini is explicitly enabled server-side).
        Synthetic demo only. Not medical advice.
      </div>
    </>
  )
}

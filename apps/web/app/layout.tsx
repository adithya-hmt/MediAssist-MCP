import type { Metadata } from 'next'
import '../globals.css'
import { Nav } from '../components/nav'

export const metadata: Metadata = {
  title: 'Cerelytic MediAssist',
  description: 'Interoperable Healthcare Agent Workspace',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="page-layout">
          <aside className="sidebar">
            <Nav />
          </aside>
          <main className="main-content">{children}</main>
        </div>
      </body>
    </html>
  )
}

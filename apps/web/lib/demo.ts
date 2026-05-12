export const DEMO_PATIENT = {
  patient_id: "synthetic-patient-001",
  encounter_id: "synthetic-encounter-001",
  name: "Demo Patient",
  source: "synthetic-demo",
  synthetic_only: true,
  age: 42,
  sex: "not specified",
  symptoms: ["persistent cough", "mild fever", "fatigue"],
  observations: { temperature_c: 38.1, heart_rate: 92, spo2: 97, respiratory_rate: 18 },
  history: ["synthetic asthma history"],
  medications: ["synthetic inhaler record"],
  notes: "Synthetic demo case for workflow testing only."
}

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export async function apiPost(path: string, body: unknown) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

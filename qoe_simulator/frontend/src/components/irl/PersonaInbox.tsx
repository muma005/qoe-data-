// Level 5 persona inbox (spec Section 2): management emails + interview scheduler.

import { useState } from 'react'

interface Email {
  from: string
  subject: string
  body: string
  simDay: number
}

const INBOX: Email[] = [
  { from: 'Arthur Pendelton (CFO)', subject: 'Rebate treatment', body: 'Rebates are already credited to COGS.', simDay: 8 },
  { from: 'Marcus Bell (Banker)', subject: 'Process note', body: 'Please consolidate all questions through me.', simDay: 9 },
  { from: 'Linda Park (Bookkeeper)', subject: 'Cash clearing', body: 'We still have unmatched cash receipts.', simDay: 10 },
]

export function PersonaInbox() {
  const [scheduled, setScheduled] = useState<string[]>([])

  function schedule(persona: string) {
    setScheduled((s) => [...s, persona])
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Communication Hub</h3>
      <div style={{ fontSize: 12 }}>
        {INBOX.map((e, i) => (
          <div key={i} style={{ border: '1px solid #ddd', marginBottom: 4, padding: 4 }}>
            <strong>{e.from}</strong> — {e.subject} (Day {e.simDay})
            <div style={{ color: '#555' }}>{e.body}</div>
          </div>
        ))}
      </div>
      <h4 style={{ marginTop: 8 }}>Interview Scheduler</h4>
      {['Frank Miller (VP Ops)', 'James Whitfield (VP Sales)', 'Arthur Pendelton (CFO)'].map((p) => (
        <button key={p} onClick={() => schedule(p)} style={{ display: 'block', margin: 2 }}>
          Schedule {p}
        </button>
      ))}
      {scheduled.length > 0 && (
        <div style={{ fontSize: 12, marginTop: 4 }}>
          Scheduled: {scheduled.join(', ')}
        </div>
      )}
    </div>
  )
}

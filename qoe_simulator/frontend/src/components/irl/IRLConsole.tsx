// Level 5 IRL console (spec Section 4): full 8-column grid, priorities, latency,
// multi-turn threads.

import { useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

interface LocalRequest {
  req: string
  wkst: string
  priority: string
  owner: string
  subject: string
  status: string
  latency: number
  doc: string
  thread: Array<{ sender_display_name: string; message_text: string }>
}

const PRIORITY_LABEL = ['', 'P1 Critical', 'P2 High', 'P3 Routine']

export function IRLConsole() {
  const { engagementId } = useWorkspaceStore()
  const [requests, setRequests] = useState<LocalRequest[]>([])
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [priority, setPriority] = useState(2)

  async function submit() {
    const r = await workspaceClient.submitIRLInquiry({
      engagement_id: engagementId,
      workstream_code: 'W03',
      priority,
      target_persona_id: 'P07_CONTROLLER',
      subject,
      inquiry_body: body,
      cited_vdr_doc_ids: [],
    })
    setRequests((prev) => [...prev, {
      req: r.request_id,
      wkst: 'W03',
      priority: PRIORITY_LABEL[priority],
      owner: 'P07 Controller',
      subject: subject || r.request_id,
      status: r.status,
      latency: r.estimated_latency_hours,
      doc: r.thread_history.length ? 'Pending' : 'None',
      thread: r.thread_history.map((t) => ({ sender_display_name: t.sender_display_name, message_text: t.message_text })),
    }])
    setSubject('')
    setBody('')
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Information Request List</h3>
      <div>
        <select value={priority} onChange={(e) => setPriority(Number(e.target.value))}>
          <option value={1}>P1 Critical</option>
          <option value={2}>P2 High</option>
          <option value={3}>P3 Routine</option>
        </select>
        <input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} style={{ width: '100%' }} />
        <textarea placeholder="Inquiry body" value={body} onChange={(e) => setBody(e.target.value)} rows={2} style={{ width: '100%' }} />
        <button onClick={submit}>Submit</button>
      </div>

      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 11, marginTop: 8 }}>
        <thead>
          <tr>
            {['Req', 'WkSt', 'Priority', 'Owner', 'Subject', 'Status', 'Latency (h)', 'VDR Doc'].map((c) => (
              <th key={c} style={{ border: '1px solid #ccc', textAlign: 'left', padding: 2 }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.req}>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.req}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.wkst}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.priority}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.owner}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.subject}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.status}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.latency.toFixed(1)}</td>
              <td style={{ border: '1px solid #ccc', padding: 2 }}>{r.doc}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {requests.map((r) => r.thread.length > 1 && (
        <div key={r.req} style={{ fontSize: 11, color: '#555', marginTop: 4 }}>
          {r.thread.map((t, i) => <div key={i}>[{t.sender_display_name}] {t.message_text}</div>)}
        </div>
      ))}
    </div>
  )
}

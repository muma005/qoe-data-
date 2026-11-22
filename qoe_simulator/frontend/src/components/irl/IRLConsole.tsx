// Level 5 IRL console (spec Section 4): priorities, latency, multi-turn threads.

import { useState } from 'react'
import { workspaceClient, IRLInquiryResponse } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

export function IRLConsole() {
  const { engagementId } = useWorkspaceStore()
  const [requests, setRequests] = useState<IRLInquiryResponse[]>([])
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')

  async function submit() {
    const r = await workspaceClient.submitIRLInquiry({
      engagement_id: engagementId,
      workstream_code: 'W03',
      priority: 2,
      target_persona_id: 'P07_CONTROLLER',
      subject,
      inquiry_body: body,
      cited_vdr_doc_ids: [],
    })
    setRequests((prev) => [...prev, r])
    setSubject('')
    setBody('')
  }

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Information Request List</h3>
      <div>
        <input placeholder="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} style={{ width: '100%' }} />
        <textarea placeholder="Inquiry body" value={body} onChange={(e) => setBody(e.target.value)} rows={3} style={{ width: '100%' }} />
        <button onClick={submit}>Submit Inquiry</button>
      </div>
      {requests.map((r) => (
        <div key={r.request_id} style={{ border: '1px solid #ddd', marginTop: 8, padding: 6, fontSize: 12 }}>
          <strong>{r.request_id}</strong> — {r.status} · {r.pushback_tier_triggered}
          <div>Thread turns: {r.thread_history.length}</div>
          {r.thread_history.map((t) => (
            <div key={t.turn_id} style={{ paddingLeft: 8, color: '#444' }}>
              [{t.sender_display_name}] {t.message_text}
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}

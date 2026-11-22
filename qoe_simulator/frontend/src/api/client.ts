// Level 5 API client — talks to the ui-workspace backend gateway over REST.
// Zero-knowledge: this client only requests released, non-ground-truth data.

export interface VDRNode {
  node_id: string
  parent_node_id: string
  title: string
  node_type: number
  release_wave: number
  unlock_sim_day: number
  is_locked: boolean
  file_size_bytes: number
  sha256_checksum: string
  canonical_json_ref: string
  children: VDRNode[]
}

export interface VDRTreeResponse {
  engagement_id: string
  current_sim_day: number
  root_nodes: VDRNode[]
  total_unlocked_documents: number
  total_locked_documents: number
}

export interface IRLThreadTurn {
  turn_id: number
  sender_persona_id: string
  sender_display_name: string
  sent_at: string
  message_text: string
  attached_document_ids: string[]
}

export interface IRLInquiryResponse {
  request_id: string
  status: string
  sim_day_submitted: number
  estimated_latency_hours: number
  pushback_tier_triggered: string
  thread_history: IRLThreadTurn[]
}

const BASE = '/api/v1/workspace'

async function post<T>(path: string, body: object): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
  return res.json() as Promise<T>
}

export const workspaceClient = {
  getVDRTree: (engagementId: string, userId: string, simDay: number) =>
    post<VDRTreeResponse>('/vdr/tree', { engagement_id: engagementId, user_id: userId, current_sim_day: simDay }),

  getVDRDocument: (engagementId: string, documentId: string, userId: string) =>
    post<object>('/vdr/document', { engagement_id: engagementId, document_id: documentId, user_id: userId }),

  submitIRLInquiry: (payload: object) =>
    post<IRLInquiryResponse>('/irl/submit', payload),

  syncWorkspaceState: (payload: object) =>
    post<object>('/state/sync', payload),

  compileDeliverables: (payload: object) =>
    post<object>('/deliverables/compile', payload),

  getDatabookTab: (packageDir: string, tabId: string) =>
    post<{ tab_id: string; data: Record<string, unknown> }>('/databook/tab',
      { package_dir: packageDir, tab_id: tabId }),

  searchVDR: (query: string) =>
    post<{ results: Array<Record<string, unknown>> }>('/vdr/search', { query }),

  getSPA: (packageDir: string) =>
    post<Record<string, unknown>>('/spa/exhibit-b', { package_dir: packageDir }),

  getReport: (packageDir: string) =>
    post<{ sections: Record<string, unknown> }>('/report/assemble', { package_dir: packageDir }),
}

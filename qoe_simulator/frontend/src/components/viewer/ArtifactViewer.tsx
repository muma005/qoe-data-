// Level 5 source artifact viewer: render JSON as text so document data cannot
// be interpreted as HTML.

import { useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

interface DocResponse {
  document_id?: string
  file_name?: string
  watermark?: { watermark_text?: string }
  canonical_json_payload?: string
}

export function ArtifactViewer() {
  const { engagementId, userId, activeVdrDocId } = useWorkspaceStore()
  const [doc, setDoc] = useState<DocResponse | null>(null)
  const [content, setContent] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  function render(canonicalJson: string) {
    setContent(JSON.stringify(JSON.parse(canonicalJson), null, 2))
  }

  async function load(docId: string) {
    try {
      const d = await workspaceClient.getVDRDocument(engagementId, docId, userId) as DocResponse
      setDoc(d)
      setError(null)
      render(d.canonical_json_payload ?? JSON.stringify(d))
    } catch (e) {
      setError((e as Error).message)
      setDoc(null)
      setContent(null)
    }
  }

  return (
    <div>
      <h3>Source Artifact Viewer</h3>
      {activeVdrDocId ? (
        <div style={{ position: 'relative' }}>
          <button onClick={() => load(activeVdrDocId)}>Load {activeVdrDocId}</button>
          {/* Dynamic watermark overlay (diagonal) */}
          {doc?.watermark?.watermark_text && (
            <div style={{
              position: 'absolute', inset: 0, pointerEvents: 'none',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              transform: 'rotate(-45deg)', opacity: 0.18, fontSize: 16,
              fontWeight: 'bold', whiteSpace: 'pre-line', textAlign: 'center',
            }}>
              {doc.watermark.watermark_text}
            </div>
          )}
          {content && <pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{content}</pre>}
          {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
      ) : (
        <div style={{ color: '#888' }}>Open a document from the VDR tree.</div>
      )}
    </div>
  )
}

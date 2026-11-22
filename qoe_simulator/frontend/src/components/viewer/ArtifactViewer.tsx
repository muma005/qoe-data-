// Level 5 source artifact viewer (spec Section 5.1): JSON-first, DOM anchors, watermark.

import { useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

export function ArtifactViewer() {
  const { engagementId, userId, activeVdrDocId } = useWorkspaceStore()
  const [doc, setDoc] = useState<Record<string, unknown> | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function load(docId: string) {
    try {
      const d = await workspaceClient.getVDRDocument(engagementId, docId, userId)
      setDoc(d as Record<string, unknown>)
      setError(null)
    } catch (e) {
      setError((e as Error).message)
      setDoc(null)
    }
  }

  return (
    <div>
      <h3>Source Artifact Viewer</h3>
      {activeVdrDocId ? (
        <div>
          <button onClick={() => load(activeVdrDocId)}>Load {activeVdrDocId}</button>
          {doc && (
            <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, background: '#fafafa', padding: 8 }}>
              {JSON.stringify(doc, null, 2)}
            </pre>
          )}
          {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
      ) : (
        <div style={{ color: '#888' }}>Open a document from the VDR tree.</div>
      )}
    </div>
  )
}

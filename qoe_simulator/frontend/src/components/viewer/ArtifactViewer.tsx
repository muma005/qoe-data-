// Level 5 source artifact viewer (spec Section 5.1/9.3): JSON-first, watermark
// overlay, worker-pooled rendering with graceful JSON fallback.

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
  const [html, setHtml] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  function render(canonicalJson: string) {
    // Worker pool with 1000ms cap; fallback to the raw JSON view on timeout.
    let rendered = false
    const worker = new Worker(new URL('../../workers/docRenderer.worker.ts', import.meta.url), { type: 'module' })
    worker.postMessage({ canonicalJson })
    const timer = setTimeout(() => {
      if (!rendered) {
        worker.terminate()
        setHtml(`<pre>${canonicalJson}</pre>`) // graceful JSON fallback
      }
    }, 1000)
    worker.onmessage = (e) => {
      rendered = true
      clearTimeout(timer)
      setHtml(e.data.html)
      worker.terminate()
    }
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
      setHtml(null)
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
          {html && <div dangerouslySetInnerHTML={{ __html: html }} />}
          {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
      ) : (
        <div style={{ color: '#888' }}>Open a document from the VDR tree.</div>
      )}
    </div>
  )
}

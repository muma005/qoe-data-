// Level 5 escrow / SPA Exhibit B builder (spec Section 6.2).

import { useEffect, useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

export function EscrowBuilder() {
  const { packageDir } = useWorkspaceStore()
  const [spa, setSpa] = useState<Record<string, unknown> | null>(null)

  useEffect(() => {
    if (!packageDir) { setSpa(null); return }
    workspaceClient.getSPA(packageDir).then(setSpa).catch(() => setSpa(null))
  }, [packageDir])

  return (
    <div style={{ marginTop: 16 }}>
      <h3>SPA Exhibit B Builder</h3>
      {!packageDir ? (
        <div style={{ color: '#888', fontSize: 12 }}>Set a package_dir to compile Exhibit B.</div>
      ) : spa ? (
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(spa, null, 2)}</pre>
      ) : (
        <div>Loading…</div>
      )}
    </div>
  )
}

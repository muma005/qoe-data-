// Level 5 VDR tree (spec Section 3): folder hierarchy, release-wave gating, locked/unlocked.

import { useEffect, useState } from 'react'
import { workspaceClient, VDRNode } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

function renderNode(node: VDRNode, depth: number, onOpen: (id: string) => void) {
  const lock = node.is_locked ? '🔒' : '📄'
  const folder = node.node_type === 1 ? '📁' : lock
  return (
    <div key={node.node_id} style={{ paddingLeft: depth * 14 }}>
      <span style={{ cursor: node.is_locked ? 'not-allowed' : 'pointer', opacity: node.is_locked ? 0.5 : 1 }}
            onClick={() => !node.is_locked && node.node_type !== 1 && onOpen(node.node_id)}>
        {folder} {node.title}
      </span>
      {node.children.map((c) => renderNode(c, depth + 1, onOpen))}
    </div>
  )
}

export function VDRTree() {
  const { engagementId, userId, currentSimDay, setActiveVdrDoc } = useWorkspaceStore()
  const [tree, setTree] = useState<VDRNode[]>([])
  const [unlocked, setUnlocked] = useState(0)
  const [locked, setLocked] = useState(0)

  useEffect(() => {
    workspaceClient.getVDRTree(engagementId, userId, currentSimDay)
      .then((r) => {
        setTree(r.root_nodes)
        setUnlocked(r.total_unlocked_documents)
        setLocked(r.total_locked_documents)
      })
      .catch(() => {/* offline / no backend */})
  }, [engagementId, userId, currentSimDay])

  return (
    <div>
      <h3>Virtual Data Room</h3>
      <div style={{ fontSize: 12, color: '#666' }}>
        {unlocked} unlocked · {locked} locked
      </div>
      {tree.map((n) => renderNode(n, 0, setActiveVdrDoc))}
    </div>
  )
}

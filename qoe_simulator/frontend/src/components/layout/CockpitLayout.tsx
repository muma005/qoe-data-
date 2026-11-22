// Level 5 three-pane diligence cockpit layout (spec Section 2).

import { useEffect } from 'react'
import { useWorkspaceStore } from '../../state/workspace_store'
import { snapshotState, restoreState } from '../../state/offline_cache'
import { VDRTree } from '../vdr/VDRTree'
import { IRLConsole } from '../irl/IRLConsole'
import { PersonaInbox } from '../irl/PersonaInbox'
import { DatabookGrid } from '../databook/DatabookGrid'
import { ArtifactViewer } from '../viewer/ArtifactViewer'
import { EscrowBuilder } from '../viewer/EscrowBuilder'

const CACHE_KEY = 'workspace-snapshot'
const CACHE_SECRET = 'qoe-session-secret'

export function CockpitLayout() {
  const { currentSimDay, checkBarStatus } = useWorkspaceStore()

  // NFR-04: restore on mount, then snapshot every 500ms (event-sourced rehydration).
  useEffect(() => {
    restoreState(CACHE_KEY, CACHE_SECRET).then((state) => {
      if (state) {
        const s = state as { currentSimDay?: number; checkBarStatus?: string }
        if (s.currentSimDay !== undefined) useWorkspaceStore.getState().setSimDay(s.currentSimDay)
        if (s.checkBarStatus !== undefined) useWorkspaceStore.getState().setCheckBarStatus(s.checkBarStatus)
      }
    })
    const interval = setInterval(() => {
      const s = useWorkspaceStore.getState()
      snapshotState(CACHE_KEY, { currentSimDay: s.currentSimDay, checkBarStatus: s.checkBarStatus }, CACHE_SECRET)
    }, 500)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* Top navigation & status bar */}
      <header style={{ display: 'flex', gap: 24, padding: '8px 16px', borderBottom: '1px solid #ccc', background: '#f7f7f7' }}>
        <strong>Clock:</strong> Day {currentSimDay} | Milestone: MS04 Flash Readout | 5.5h Remaining
        <span style={{ color: checkBarStatus.startsWith('OK') ? 'green' : 'red', fontWeight: 'bold' }}>
          Check Bars: {checkBarStatus}
        </span>
        <strong>Deal Track:</strong> AUCTION_COMPRESSED
      </header>

      {/* Three panes */}
      <main style={{ display: 'grid', gridTemplateColumns: '280px 1fr 380px', flex: 1, overflow: 'hidden' }}>
        <section style={{ borderRight: '1px solid #ccc', overflowY: 'auto', padding: 8 }}>
          <VDRTree />
          <IRLConsole />
          <PersonaInbox />
        </section>
        <section style={{ overflow: 'auto', padding: 8 }}>
          <DatabookGrid />
        </section>
        <section style={{ borderLeft: '1px solid #ccc', overflowY: 'auto', padding: 8 }}>
          <ArtifactViewer />
          <EscrowBuilder />
        </section>
      </main>
    </div>
  )
}

// Level 5 three-pane diligence cockpit layout (spec Section 2).

import { useWorkspaceStore } from '../../state/workspace_store'
import { VDRTree } from '../vdr/VDRTree'
import { IRLConsole } from '../irl/IRLConsole'
import { DatabookGrid } from '../databook/DatabookGrid'
import { ArtifactViewer } from '../viewer/ArtifactViewer'

export function CockpitLayout() {
  const { currentSimDay, checkBarStatus } = useWorkspaceStore()

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
        </section>
        <section style={{ overflow: 'auto', padding: 8 }}>
          <DatabookGrid />
        </section>
        <section style={{ borderLeft: '1px solid #ccc', overflowY: 'auto', padding: 8 }}>
          <ArtifactViewer />
        </section>
      </main>
    </div>
  )
}

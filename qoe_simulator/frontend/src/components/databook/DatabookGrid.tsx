// Level 5 databook grid (spec Section 5): canvas grid, RGB, pinned Row 1 check
// bar, live data + full formula tracer (source JE ID + VDR hash).

import { useEffect, useRef, useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

const TABS = ['01_Summary', '02_EBITDA_Bridges', '03_Income_Statement', '04_Revenue_PVM',
  '05_Gross_Margin', '06_OPEX_Detail', '07_Working_Capital', '08_Net_Debt',
  '09_Cash_Flow_Capex', '10_Debt_Like_Items', '11_SPA_Exhibit_B']

const RGB = { BLUE: '#0000FF', BLACK: '#000000', GREEN: '#008000', RED: '#FF0000' }
const ROW_H = 24

interface Trace {
  source_accounts: string[]
  source_je_id: string
  vdr_document_id: string
  vdr_file_hash: string
}

export function DatabookGrid() {
  const { activeTabIndex, setActiveTab, checkBarStatus, packageDir } = useWorkspaceStore()
  const [rows, setRows] = useState<Array<[string, unknown]>>([])
  const [selected, setSelected] = useState<[string, unknown] | null>(null)
  const [trace, setTrace] = useState<Trace | null>(null)
  const [anchorSelector, setAnchorSelector] = useState('')
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const activeTab = TABS[activeTabIndex]

  useEffect(() => {
    if (!packageDir) { setRows([]); return }
    workspaceClient.getDatabookTab(packageDir, activeTab)
      .then((r) => setRows(Object.entries(r.data)))
      .catch(() => setRows([]))
  }, [packageDir, activeTab])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const w = canvas.width
    ctx.clearRect(0, 0, w, canvas.height)
    ctx.font = '12px monospace'
    rows.forEach(([name, value], i) => {
      const y = i * ROW_H
      if (selected?.[0] === name) ctx.fillStyle = '#eef'
      else ctx.fillStyle = i % 2 ? '#fff' : '#fafafa'
      ctx.fillRect(0, y, w, ROW_H)
      ctx.fillStyle = RGB.BLACK
      ctx.fillText(name, 6, y + 16)
      ctx.fillStyle = typeof value === 'number' ? RGB.BLUE : RGB.BLACK
      ctx.fillText(String(value).slice(0, 60), w / 2, y + 16)
      ctx.strokeStyle = '#ccc'
      ctx.strokeRect(0, y, w, ROW_H)
    })
  }, [rows, selected])

  function onCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const rect = e.currentTarget.getBoundingClientRect()
    const y = e.clientY - rect.top
    const idx = Math.floor(y / ROW_H)
    const cell = rows[idx]
    if (cell) {
      setSelected(cell)
      workspaceClient.getTrace(activeTab, cell[0])
        .then(setTrace).catch(() => setTrace(null))
      // DOM linkage resolver worker: JSON anchor -> CSS selector
      const worker = new Worker(new URL('../../workers/domLinkage.worker.ts', import.meta.url), { type: 'module' })
      worker.postMessage({ jsonAnchor: `databook/${activeTab}#${cell[0]}` })
      worker.onmessage = (ev) => setAnchorSelector(ev.data.selector)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
        {TABS.map((t, i) => (
          <button key={t} onClick={() => { setActiveTab(i); setSelected(null); setTrace(null) }}
                  style={{ fontWeight: i === activeTabIndex ? 'bold' : 'normal' }}>
            {t}
          </button>
        ))}
      </div>

      <div style={{
        background: checkBarStatus.startsWith('OK') ? '#E2EFDA' : '#C00000',
        color: checkBarStatus.startsWith('OK') ? '#375623' : '#FFFFFF',
        fontWeight: 'bold', padding: 6, marginBottom: 8,
      }}>
        {checkBarStatus}
      </div>

      {!packageDir ? (
        <div style={{ color: '#888' }}>Set a scenario package_dir to load the databook.</div>
      ) : (
        <canvas ref={canvasRef} width={640} height={Math.max(rows.length * ROW_H, 200)}
                onClick={onCanvasClick} style={{ border: '1px solid #ccc', width: '100%' }} />
      )}

      {/* Formula tracer / audit trail */}
      {selected && (
        <div style={{ border: '1px solid #999', marginTop: 8, padding: 8, background: '#f9f9f9' }}>
          <strong>Formula Tracer</strong>
          <div>Cell: {activeTab}!{selected[0]}</div>
          <div style={{ color: RGB.GREEN }}>Formula: ={activeTab}!{selected[0]}</div>
          <div style={{ color: RGB.GREEN }}>JSON anchor: databook/{activeTab}#{selected[0]}</div>
          {anchorSelector && <div style={{ color: RGB.GREEN }}>DOM selector: {anchorSelector}</div>}
          {trace && (
            <>
              <div style={{ color: RGB.BLACK }}>Source accounts: {trace.source_accounts.join(', ')}</div>
              <div style={{ color: RGB.BLACK }}>Source JE ID: {trace.source_je_id}</div>
              <div style={{ color: RGB.BLACK }}>VDR doc: {trace.vdr_document_id} · SHA-256: {trace.vdr_file_hash.slice(0, 16)}…</div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

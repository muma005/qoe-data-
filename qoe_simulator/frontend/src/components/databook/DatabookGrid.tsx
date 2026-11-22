// Level 5 databook grid (spec Section 5): 11 tabs, RGB, pinned Row 1 check bar,
// wired to the backend databook tab endpoint.

import { useEffect, useState } from 'react'
import { workspaceClient } from '../../api/client'
import { useWorkspaceStore } from '../../state/workspace_store'

const TABS = ['01_Summary', '02_EBITDA_Bridges', '03_Income_Statement', '04_Revenue_PVM',
  '05_Gross_Margin', '06_OPEX_Detail', '07_Working_Capital', '08_Net_Debt',
  '09_Cash_Flow_Capex', '10_Debt_Like_Items', '11_SPA_Exhibit_B']

// RGB font color coding (Level 4 spec Section 3): blue = inputs, black = formulas.
const RGB = { BLUE: '#0000FF', BLACK: '#000000', GREEN: '#008000', RED: '#FF0000' }

function formatValue(v: unknown): { text: string; color: string } {
  if (typeof v === 'number') return { text: v.toLocaleString(undefined, { maximumFractionDigits: 2 }), color: RGB.BLUE }
  if (typeof v === 'string') return { text: v, color: RGB.BLACK }
  if (Array.isArray(v) || typeof v === 'object') return { text: JSON.stringify(v), color: RGB.BLACK }
  return { text: String(v), color: RGB.BLACK }
}

export function DatabookGrid() {
  const { activeTabIndex, setActiveTab, checkBarStatus, packageDir } = useWorkspaceStore()
  const [rows, setRows] = useState<Array<[string, unknown]>>([])
  const [loading, setLoading] = useState(false)

  const activeTab = TABS[activeTabIndex]

  useEffect(() => {
    if (!packageDir) { setRows([]); return }
    setLoading(true)
    workspaceClient.getDatabookTab(packageDir, activeTab)
      .then((r) => setRows(Object.entries(r.data)))
      .catch(() => setRows([]))
      .finally(() => setLoading(false))
  }, [packageDir, activeTab])

  return (
    <div>
      <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginBottom: 8 }}>
        {TABS.map((t, i) => (
          <button key={t} onClick={() => setActiveTab(i)}
                  style={{ fontWeight: i === activeTabIndex ? 'bold' : 'normal' }}>
            {t}
          </button>
        ))}
      </div>

      {/* Row 1 pinned check bar */}
      <div style={{
        background: checkBarStatus.startsWith('OK') ? '#E2EFDA' : '#C00000',
        color: checkBarStatus.startsWith('OK') ? '#375623' : '#FFFFFF',
        fontWeight: 'bold', padding: 6, marginBottom: 8,
      }}>
        {checkBarStatus}
      </div>

      {!packageDir ? (
        <div style={{ color: '#888' }}>Set a scenario package_dir to load the databook.</div>
      ) : loading ? (
        <div>Loading {activeTab}…</div>
      ) : (
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <tbody>
            {rows.map(([name, value]) => {
              const { text, color } = formatValue(value)
              return (
                <tr key={name}>
                  <td style={{ border: '1px solid #ccc', padding: 2, color: RGB.BLACK, fontWeight: 'bold' }}>{name}</td>
                  <td style={{ border: '1px solid #ccc', padding: 2, color }}>{text}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  )
}

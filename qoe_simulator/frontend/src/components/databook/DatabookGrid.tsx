// Level 5 databook grid (spec Section 5): 11 tabs, RGB, pinned Row 1 check bar.

import { useWorkspaceStore } from '../../state/workspace_store'

const TABS = ['01_Summary', '02_EBITDA_Bridges', '03_Income_Statement', '04_Revenue_PVM',
  '05_Gross_Margin', '06_OPEX_Detail', '07_Working_Capital', '08_Net_Debt',
  '09_Cash_Flow_Capex', '10_Debt_Like_Items', '11_SPA_Exhibit_B']

// RGB font color coding (Level 4 spec Section 3)
const RGB = { BLUE: '#0000FF', BLACK: '#000000', GREEN: '#008000', RED: '#FF0000' }

export function DatabookGrid() {
  const { activeTabIndex, setActiveTab, checkBarStatus } = useWorkspaceStore()

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
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>{['A', 'B', 'C', 'D'].map((c) => <th key={c} style={{ border: '1px solid #ccc' }}>{c}</th>)}</tr>
        </thead>
        <tbody>
          {Array.from({ length: 20 }).map((_, r) => (
            <tr key={r}>
              {Array.from({ length: 4 }).map((_, c) => (
                <td key={c} style={{ border: '1px solid #ccc', color: r === 0 ? RGB.BLUE : RGB.BLACK, padding: 2 }}>
                  {r === 0 ? `B${c + 1}` : ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

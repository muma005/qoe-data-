import { describe, it, expect, beforeEach } from 'vitest'
import { useWorkspaceStore } from './workspace_store'

describe('workspace store', () => {
  beforeEach(() => {
    useWorkspaceStore.setState({
      currentSimDay: 8,
      checkBarStatus: 'OK (0 Breaks across 11 Tabs)',
      tabStates: [],
      activeTabIndex: 0,
    })
  })

  it('advances the sim day', () => {
    useWorkspaceStore.getState().setSimDay(14)
    expect(useWorkspaceStore.getState().currentSimDay).toBe(14)
  })

  it('updates check bar status', () => {
    useWorkspaceStore.getState().setCheckBarStatus('DISCREPANCY: $310,000')
    expect(useWorkspaceStore.getState().checkBarStatus).toContain('DISCREPANCY')
  })

  it('deduplicates tab state by tab_id', () => {
    useWorkspaceStore.getState().updateTabState(
      { tab_id: '01', active_cell: 'B2', scroll_row: 0, scroll_col: 0, check_bar_passed: true })
    useWorkspaceStore.getState().updateTabState(
      { tab_id: '01', active_cell: 'C3', scroll_row: 1, scroll_col: 1, check_bar_passed: false })
    expect(useWorkspaceStore.getState().tabStates.length).toBe(1)
    expect(useWorkspaceStore.getState().tabStates[0].active_cell).toBe('C3')
  })
})

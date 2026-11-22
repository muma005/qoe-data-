// Level 5 workspace state (Zustand). Zero-knowledge (NFR-03/LP-05):
// this store never holds ground-truth adjustments, fraud markers, or unreleased paths.

import { create } from 'zustand'

export interface TabState {
  tab_id: string
  active_cell: string
  scroll_row: number
  scroll_col: number
  check_bar_passed: boolean
}

interface WorkspaceState {
  engagementId: string
  userId: string
  currentSimDay: number
  activeTabIndex: number
  packageDir: string
  tabStates: TabState[]
  activeVdrDocId: string | null
  checkBarStatus: string
  setSimDay: (day: number) => void
  setActiveTab: (index: number) => void
  setPackageDir: (dir: string) => void
  setActiveVdrDoc: (docId: string | null) => void
  setCheckBarStatus: (status: string) => void
  updateTabState: (ts: TabState) => void
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  engagementId: 'sim_apex_001',
  userId: 'USR_8921',
  currentSimDay: 8,
  activeTabIndex: 0,
  packageDir: '',
  tabStates: [],
  activeVdrDocId: null,
  checkBarStatus: 'OK (0 Breaks across 11 Tabs)',
  setSimDay: (day) => set({ currentSimDay: day }),
  setActiveTab: (index) => set({ activeTabIndex: index }),
  setPackageDir: (dir) => set({ packageDir: dir }),
  setActiveVdrDoc: (docId) => set({ activeVdrDocId: docId }),
  setCheckBarStatus: (status) => set({ checkBarStatus: status }),
  updateTabState: (ts) =>
    set((s) => ({
      tabStates: [...s.tabStates.filter((t) => t.tab_id !== ts.tab_id), ts],
    })),
}))

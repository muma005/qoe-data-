// Level 5 DOM linkage resolver worker (spec Section 9): resolves a canonical JSON
// anchor path into a DOM selector for the artifact viewer.

/// <reference lib="webworker" />

self.onmessage = (e: MessageEvent) => {
  const { jsonAnchor } = e.data
  // e.g. "databook/07_Working_Capital#nwc" -> "#anchor-nwc"
  const hash = String(jsonAnchor || '').split('#')[1] || ''
  const selector = hash ? `#anchor-${hash.replace(/[^a-zA-Z0-9_-]/g, '-')}` : ''
  ;(self as unknown as Worker).postMessage({ selector })
}

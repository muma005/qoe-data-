// Level 5 document renderer worker (spec Section 9.3): renders canonical JSON
// into an HTML presentation view in a dedicated Web Worker thread.

/// <reference lib="webworker" />

self.onmessage = (e: MessageEvent) => {
  const { canonicalJson } = e.data
  try {
    const html = `<pre style="white-space:pre-wrap;font-size:12px">${JSON.stringify(canonicalJson, null, 2)}</pre>`
    ;(self as unknown as Worker).postMessage({ html })
  } catch (err) {
    ;(self as unknown as Worker).postMessage({ error: String(err) })
  }
}

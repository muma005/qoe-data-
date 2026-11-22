// Level 5 offline cache — IndexedDB snapshotting + HMAC-SHA256 state guard (NFR-04).

const DB_NAME = 'qoe-workspace'
const STORE = 'snapshots'

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = () => req.result.createObjectStore(STORE, { keyPath: 'key' })
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function hmacSha256Hex(message: string, secret: string): Promise<string> {
  const enc = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign'])
  const sig = await crypto.subtle.sign('HMAC', key, enc.encode(message))
  return Array.from(new Uint8Array(sig)).map((b) => b.toString(16).padStart(2, '0')).join('')
}

export async function snapshotState(key: string, value: unknown, secret: string): Promise<void> {
  const json = JSON.stringify(value)
  const signature = await hmacSha256Hex(json, secret)
  const db = await openDB()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    tx.objectStore(STORE).put({ key, json, signature })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function restoreState(key: string, secret: string): Promise<unknown | null> {
  const db = await openDB()
  const record = await new Promise<{ key: string; json: string; signature: string } | undefined>(
    (resolve, reject) => {
      const tx = db.transaction(STORE, 'readonly')
      const req = tx.objectStore(STORE).get(key)
      req.onsuccess = () => resolve(req.result)
      req.onerror = () => reject(req.error)
    })
  if (!record) return null
  const expected = await hmacSha256Hex(record.json, secret)
  if (expected !== record.signature) {
    // LP-05 / NFR-04: tampered cache -> purge and return null (fetch fresh from server).
    const tx = db.transaction(STORE, 'readwrite')
    tx.objectStore(STORE).delete(key)
    return null
  }
  return JSON.parse(record.json)
}

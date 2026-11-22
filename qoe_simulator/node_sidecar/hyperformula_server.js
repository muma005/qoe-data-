// HyperFormula Node.js sidecar for the QoE simulator.
// Exposes POST /evaluate {formula, cells} -> {result} and GET /health.
// License: HyperFormula is GPL-3.0-only (licenseKey: 'gpl-v3').
'use strict';

const http = require('http');
const { HyperFormula } = require('hyperformula');

const ROWS = 300;
const COLS = 120;
const PORT = Number(process.env.HF_PORT || 4417);

function colIndex(letters) {
  let col = 0;
  for (const ch of letters) col = col * 26 + (ch.charCodeAt(0) - 64);
  return col - 1;
}

// "B2" -> {row, col}; "C28:AN28" -> start cell {row, col}.
function parseStart(addr) {
  const m = /^([A-Z]+)(\d+)/.exec(addr.split(':')[0]);
  if (!m) throw new Error('Bad address: ' + addr);
  return { col: colIndex(m[1]), row: parseInt(m[2], 10) - 1 };
}

function toPlain(v) {
  // HyperFormula returns a DetailedCellError object for errors; expose its code.
  if (v && typeof v === 'object' && v.value !== undefined && v.type !== undefined) {
    return v.value; // e.g. "#VALUE!", "#N/A"
  }
  return v;
}

function evaluate(formula, cells) {
  const hf = HyperFormula.buildFromSheets(
    { Sheet1: Array.from({ length: ROWS }, () => Array(COLS).fill(null)) },
    { licenseKey: 'gpl-v3' }
  );
  for (const [addr, val] of Object.entries(cells || {})) {
    const { col, row } = parseStart(addr);
    hf.setCellContents({ sheet: 0, row, col }, val);
  }
  const target = { sheet: 0, row: 0, col: 1 }; // B1
  hf.setCellContents(target, formula);
  let result = hf.getCellValue(target);
  // Array range arithmetic needs ARRAYFORMULA; retry transparently.
  if (result && typeof result === 'object' && result.message === 'Cell range not allowed.') {
    hf.setCellContents(target, '=ARRAYFORMULA(' + formula.slice(1) + ')');
    result = hf.getCellValue(target);
  }
  return toPlain(result);
}

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ ok: true, engine: 'hyperformula' }));
  }
  if (req.method === 'POST' && req.url === '/evaluate') {
    let body = '';
    req.on('data', (c) => { body += c; });
    req.on('end', () => {
      try {
        const { formula, cells } = JSON.parse(body);
        const result = evaluate(formula, cells);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ result }));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'not found' }));
});

server.listen(PORT, () => console.log('HyperFormula sidecar listening on :' + PORT));

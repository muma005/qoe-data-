// HyperFormula Node.js sidecar for the QoE simulator (stateful workbook).
// Endpoints:
//   GET  /health                     -> {ok, engine}
//   POST /evaluate {formula, cells}  -> {result}   (standalone one-shot)
//   POST /build     {sheets}         -> {sheetNames} (build the full workbook)
//   POST /get-cell  {sheet,row,col}  -> {value}
//   POST /get-sheet {sheet}          -> {values}   (full computed 2D grid)
// License: HyperFormula is GPL-3.0-only (licenseKey: 'gpl-v3').
'use strict';

const http = require('http');
const { HyperFormula } = require('hyperformula');

const PORT = Number(process.env.HF_PORT || 4417);
const ROWS = 300;
const COLS = 120;

let hf = null;   // stateful workbook
let sheetNames = [];

function colIndex(letters) {
  let col = 0;
  for (const ch of letters) col = col * 26 + (ch.charCodeAt(0) - 64);
  return col - 1;
}

function parseStart(addr) {
  const m = /^([A-Z]+)(\d+)/.exec(addr.split(':')[0]);
  if (!m) throw new Error('Bad address: ' + addr);
  return { col: colIndex(m[1]), row: parseInt(m[2], 10) - 1 };
}

function toPlain(v) {
  if (v && typeof v === 'object' && v.value !== undefined && v.type !== undefined) {
    return v.value; // "#VALUE!", "#N/A", ...
  }
  return v;
}

function build(sheets) {
  const padded = {};
  sheetNames = [];
  for (const [name, grid] of Object.entries(sheets || {})) {
    sheetNames.push(name);
    const rows = grid.map((row) => row.concat(Array(COLS - row.length).fill(null)));
    padded[name] = rows;
  }
  hf = HyperFormula.buildFromSheets(padded, { licenseKey: 'gpl-v3' });
  return sheetNames;
}

function sheetId(nameOrIndex) {
  if (typeof nameOrIndex === 'number') return nameOrIndex;
  return sheetNames.indexOf(nameOrIndex);
}

function evaluate(formula, cells) {
  const h = HyperFormula.buildFromSheets(
    { Sheet1: Array.from({ length: ROWS }, () => Array(COLS).fill(null)) },
    { licenseKey: 'gpl-v3' }
  );
  for (const [addr, val] of Object.entries(cells || {})) {
    const { col, row } = parseStart(addr);
    h.setCellContents({ sheet: 0, row, col }, val);
  }
  const target = { sheet: 0, row: 0, col: 1 };
  h.setCellContents(target, formula);
  let result = h.getCellValue(target);
  if (result && typeof result === 'object' && result.message === 'Cell range not allowed.') {
    h.setCellContents(target, '=ARRAYFORMULA(' + formula.slice(1) + ')');
    result = h.getCellValue(target);
  }
  return toPlain(result);
}

function readBody(req, cb) {
  let body = '';
  req.on('data', (c) => { body += c; });
  req.on('end', () => {
    try { cb(JSON.parse(body || '{}')); }
    catch (e) { cb(null, e); }
  });
}

function json(res, code, obj) {
  res.writeHead(code, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/health') {
    return json(res, 200, { ok: true, engine: 'hyperformula' });
  }

  if (req.method === 'POST' && req.url === '/evaluate') {
    return readBody(req, (body, err) => {
      if (err) return json(res, 400, { error: err.message });
      try {
        json(res, 200, { result: evaluate(body.formula, body.cells) });
      } catch (e) { json(res, 400, { error: e.message }); }
    });
  }

  if (req.method === 'POST' && req.url === '/build') {
    return readBody(req, (body, err) => {
      if (err) return json(res, 400, { error: err.message });
      try {
        json(res, 200, { sheetNames: build(body.sheets) });
      } catch (e) { json(res, 400, { error: e.message }); }
    });
  }

  if (req.method === 'POST' && req.url === '/get-cell') {
    return readBody(req, (body, err) => {
      if (err) return json(res, 400, { error: err.message });
      try {
        const sid = sheetId(body.sheet);
        json(res, 200, { value: toPlain(hf.getCellValue({ sheet: sid, row: body.row, col: body.col })) });
      } catch (e) { json(res, 400, { error: e.message }); }
    });
  }

  if (req.method === 'POST' && req.url === '/get-sheet') {
    return readBody(req, (body, err) => {
      if (err) return json(res, 400, { error: err.message });
      try {
        const sid = sheetId(body.sheet);
        const values = hf.getSheetValues(sid).map((row) => row.map(toPlain));
        json(res, 200, { values });
      } catch (e) { json(res, 400, { error: e.message }); }
    });
  }

  json(res, 404, { error: 'not found' });
});

server.listen(PORT, () => console.log('HyperFormula sidecar listening on :' + PORT));

"""Workbook parsing, independent calculation, and evidentiary verification."""
from __future__ import annotations


# ========================================================================
# Formula syntax and safe evaluation
# ========================================================================

import re
from decimal import Decimal, ROUND_HALF_UP

TOKEN = re.compile(r"""\s*(?:(\$?[A-Za-z]{1,3}\$?\d+)|((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)|([A-Za-z_][A-Za-z_0-9]*)|('(?:[^']|'')*')|("(?:[^"]|"")*")|(<=|>=|<>|[+*/^%=<>()!,:-]))""")

class FormulaError(ValueError):
    pass

class Parser:
    def __init__(self, formula):
        if len(formula) > 32768:
            raise FormulaError("Formula too long")
        self.tokens = []
        pos = 0
        text = formula.lstrip().removeprefix("=").strip()
        while pos < len(text):
            m = TOKEN.match(text, pos)
            if not m:
                raise FormulaError("Unsupported formula syntax")
            self.tokens.append(next((i, v) for i, v in enumerate(m.groups()) if v is not None))
            pos = m.end()
        self.i = 0
        self.depth = 0
    def peek(self):
        return self.tokens[self.i][1] if self.i < len(self.tokens) else None
    def take(self):
        if self.i >= len(self.tokens): raise FormulaError("Unexpected end")
        t = self.tokens[self.i]; self.i += 1; return t
    def require(self, value):
        if self.take()[1] != value: raise FormulaError("Expected " + value)
    def parse(self):
        result = self.expr()
        if self.peek() is not None: raise FormulaError("Trailing tokens")
        return result
    def expr(self, minimum=0):
        self.depth += 1
        if self.depth > 100: raise FormulaError("Formula nesting limit")
        kind, value = self.take()
        if value in ("+", "-"):
            left = ("unary", value, self.expr(4))
        elif value == "(":
            left = self.expr(); self.require(")")
        elif kind == 1:
            left = ("number", Decimal(value))
        elif kind == 4:
            left = ("text", value[1:-1].replace('""', '"'))
        elif self.peek() == "!":
            self.take(); coord = self.take()[1]
            if not re.fullmatch(r"\$?[A-Za-z]{1,3}\$?\d+", coord): raise FormulaError("Invalid reference")
            left = ("ref", value.strip("'").replace("''", "'"), coord.replace("$", "").upper())
        elif kind == 0:
            left = ("ref", None, value.replace("$", "").upper())
        elif kind == 2 and self.peek() == "(":
            self.take(); args = []
            if self.peek() != ")":
                args.append(self.expr())
                while self.peek() == ",": self.take(); args.append(self.expr())
            self.require(")"); left = ("call", value.upper(), args)
        elif value.upper() in ("TRUE", "FALSE"):
            left = ("boolean", value.upper() == "TRUE")
        else: raise FormulaError("Unsupported name " + value)
        if self.peek() == ":":
            self.take(); end = self.take()[1].replace("$", "").upper()
            if left[0] != "ref" or not re.fullmatch(r"[A-Z]{1,3}\d+", end): raise FormulaError("Invalid range")
            left = ("range", left, end)
        if self.peek() == "%": self.take(); left = ("percent", left)
        levels = {"=":1,"<>":1,"<":1,">":1,"<=":1,">=":1,"+":2,"-":2,"*":3,"/":3,"^":4}
        while self.peek() in levels and levels[self.peek()] >= minimum:
            op = self.take()[1]; right = self.expr(levels[op] + (0 if op == "^" else 1)); left = ("binary", op, left, right)
        self.depth -= 1
        return left

def constants(node, allowed=False):
    if node[0] == "number": return [] if allowed else [str(node[1])]
    if node[0] == "call":
        return [x for i,a in enumerate(node[2]) for x in constants(a, node[1] == "ROUND" and i == 1 and a[0] == "number" and a[1] in (0, 2, 4))]
    result = []
    for child in node[1:]:
        if isinstance(child, tuple): result.extend(constants(child))
    return result

def evaluate(node, resolve):
    kind = node[0]
    if kind in ("number", "text", "boolean"): return node[1]
    if kind == "ref": return resolve(node[1], node[2])
    if kind == "range":
        def split(c):
            m=re.fullmatch(r"([A-Z]+)([0-9]+)", c); n=0
            for ch in m[1]: n=n*26+ord(ch)-64
            return n,int(m[2])
        def col(n):
            s=""
            while n: n,r=divmod(n-1,26); s=chr(65+r)+s
            return s
        a,b=split(node[1][2]); c,d=split(node[2])
        if c<a or d<b or (c-a+1)*(d-b+1)>100000: raise FormulaError("Range limit")
        return [resolve(node[1][1],col(x)+str(y)) for y in range(b,d+1) for x in range(a,c+1)]
    if kind == "unary":
        v=evaluate(node[2],resolve); return -v if node[1]=="-" else v
    if kind == "percent": return evaluate(node[1],resolve)/Decimal(100)
    if kind == "binary":
        a=evaluate(node[2],resolve); b=evaluate(node[3],resolve); op=node[1]
        if op=="+": return a+b
        if op=="-": return a-b
        if op=="*": return a*b
        if op=="/": return a/b
        if op=="^":
            if abs(b)>100: raise FormulaError("Exponent limit")
            return a**b
        return {"=":lambda:a==b,"<>":lambda:a!=b,"<":lambda:a<b,">":lambda:a>b,"<=":lambda:a<=b,">=":lambda:a>=b}[op]()
    name,args=node[1:]
    if name=="IF" and len(args)==3: return evaluate(args[1] if evaluate(args[0],resolve) else args[2],resolve)
    values=[evaluate(a,resolve) for a in args]
    flat=[x for v in values for x in (v if isinstance(v,list) else [v])]
    if name in ("SUMIF", "SUMIFS"):
        if name=="SUMIF":
            if len(values) not in (2,3): raise FormulaError("SUMIF arity")
            ranges=[values[0]]; criteria=[values[1]]; amounts=values[2] if len(values)==3 else values[0]
        else:
            if len(values)<3 or len(values)%2!=1: raise FormulaError("SUMIFS arity")
            amounts=values[0]; ranges=values[1::2]; criteria=values[2::2]
        if not isinstance(amounts,list) or any(not isinstance(r,list) or len(r)!=len(amounts) for r in ranges): raise FormulaError("SUMIFS range dimensions")
        def matches(value,criterion):
            if not isinstance(criterion,str): return value==criterion
            match=re.fullmatch(r"(<=|>=|<>|=|<|>)?(.*)",criterion)
            op=match[1] or "="; target=match[2]
            try: target=Decimal(target)
            except Exception: pass
            if op=="=": return value==target
            if op=="<>": return value!=target
            if op=="<": return value<target
            if op==">": return value>target
            if op=="<=": return value<=target
            return value>=target
        return sum((v for i,v in enumerate(amounts) if all(matches(r[i],c) for r,c in zip(ranges,criteria))),Decimal(0))
    if name=="SUM": return sum(flat,Decimal(0))
    if name=="MIN": return min(flat)
    if name=="MAX": return max(flat)
    if name=="ABS" and len(values)==1: return abs(values[0])
    if name=="ROUND" and len(values)==2:
        if values[1]!=int(values[1]) or abs(values[1])>20: raise FormulaError("Invalid rounding")
        return values[0].quantize(Decimal(1).scaleb(-int(values[1])),rounding=ROUND_HALF_UP)
    if name=="AND": return all(flat)
    if name=="OR": return any(flat)
    raise FormulaError("Unsupported function " + name)


# ========================================================================
# OpenXML ingestion and workbook audit
# ========================================================================

from decimal import Decimal
from io import BytesIO
from zipfile import ZipFile
import posixpath
import xml.etree.ElementTree as ET

NS = {"s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"

class WorkbookAudit:
    def __init__(self, data):
        self.cells={}; self.values={}; self.dependencies={}; self.findings=[]; self.sheets=[]
        if len(data)>64*1024*1024: raise ValueError("Workbook compressed size limit")
        with ZipFile(BytesIO(data)) as z:
            infos=z.infolist()
            if len(infos)>10000 or sum(i.file_size for i in infos)>128*1024*1024: raise ValueError("Workbook expansion limit")
            if len({i.filename for i in infos})!=len(infos): raise ValueError("Duplicate archive members")
            def xml(path):
                raw=z.read(path)
                if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper(): raise ValueError("XML entities prohibited")
                return ET.fromstring(raw)
            rels={r.attrib["Id"]:r.attrib["Target"] for r in xml("xl/_rels/workbook.xml.rels") if r.attrib.get("TargetMode")!="External"}
            strings=[]
            if "xl/sharedStrings.xml" in z.namelist():
                strings=["".join(n.itertext()) for n in xml("xl/sharedStrings.xml").findall("s:si",NS)]
            for sheet in xml("xl/workbook.xml").findall("s:sheets/s:sheet",NS):
                name=sheet.attrib["name"]; self.sheets.append(name)
                target=rels[sheet.attrib[RID]]
                path=posixpath.normpath(posixpath.join("xl",target)) if not target.startswith("/") else target[1:]
                if not path.startswith("xl/"): raise ValueError("Invalid sheet path")
                for c in xml(path).findall(".//s:sheetData/s:row/s:c",NS):
                    key=name+"!"+c.attrib["r"]
                    if key in self.cells: raise ValueError("Duplicate cell")
                    f=c.find("s:f",NS); v=c.findtext("s:v",default="",namespaces=NS); typ=c.attrib.get("t", "n")
                    if typ=="s": value=strings[int(v)]
                    elif typ=="inlineStr": value="".join(c.find("s:is",NS).itertext())
                    elif typ in ("str","e"): value=v
                    elif typ=="b": value=v=="1"
                    else: value=Decimal(v) if v else None
                    formula="="+(f.text or "") if f is not None else None
                    self.cells[key]={"value":value,"formula":formula,"type":typ}
                    if len(self.cells)>100000: raise ValueError("Cell count limit")
        if len(set(self.sheets))!=len(self.sheets): raise ValueError("Duplicate sheets")
    def value(self,key,active=None):
        if key in self.values: return self.values[key]
        active=set() if active is None else active
        if key in active: raise FormulaError("Circular reference: "+key)
        if len(active)>100: raise FormulaError("Dependency depth limit")
        if key not in self.cells: raise FormulaError("Unresolved reference: "+key)
        cell=self.cells[key]
        if not cell["formula"]:
            if cell["type"]=="e" or cell["value"] is None: raise FormulaError("Invalid input: "+key)
            value=cell["value"]
        else:
            sheet=key.rsplit("!",1)[0]; active.add(key)
            try:
                def resolve(tab,coord):
                    dep=(tab or sheet)+"!"+coord
                    self.dependencies.setdefault(key,set()).add(dep)
                    return self.value(dep,active)
                value=evaluate(Parser(cell["formula"]).parse(),resolve)
            finally: active.remove(key)
        if isinstance(value,Decimal) and not value.is_finite(): raise FormulaError("Non-finite cell")
        self.values[key]=value
        return value
    def audit(self, policy):
        findings=[]
        def fail(code,cell,detail):
            findings.append({"violation_type":code,"cell_coordinate":cell,"rationale":detail,
                             "formula_raw":self.cells.get(cell,{}).get("formula") or ""})
        required=policy.get("required_sheets",[])
        if len(required)!=11: fail("INVALID_POLICY","","Eleven required sheets must be configured")
        for sheet in required:
            if sheet not in self.sheets: fail("MISSING_SHEET",sheet,"Required sheet absent")
        calculation=set(policy.get("calculation_cells",[]))
        for key,cell in sorted(self.cells.items()):
            try:
                if key in calculation and not cell["formula"]: fail("RAW_HARDCODE",key,"Calculation cell has no formula")
                if cell["formula"]:
                    ast=Parser(cell["formula"]).parse()
                    if constants(ast): fail("VIO_EMBEDDED_CONSTANT",key,", ".join(constants(ast)))
                    actual=self.value(key)
                    # OpenXML formula caches are optional; openpyxl emits none. Recalculate
                    # all formulas and compare any cache that is actually supplied.
                    if cell["value"] is not None and actual!=cell["value"]: fail("RECALCULATION_MISMATCH",key,"Independent result differs from submitted result")
            except (ValueError,ArithmeticError,TypeError,KeyError) as e: fail("FORMULA_ERROR",key,str(e))
        for key in calculation-set(self.cells): fail("MISSING_CALCULATION",key,"Required calculation absent")
        checks=policy.get("check_bars",[]); passed=0
        if len(checks)!=11 or len({x.rsplit("!",1)[0] for x in checks})!=11: fail("CHECK_BAR_COVERAGE","","Require one check on each of eleven sheets")
        for key in checks:
            try:
                expected=policy.get("check_bar_formulas",{}).get(key)
                if expected is not None and self.cells[key]["formula"]!=expected:
                    raise ValueError("Check-bar formula differs from trusted calculation")
                result=self.value(key)
                if not self.cells[key]["formula"] or not isinstance(result,str) or not result.startswith("OK"): raise ValueError("Check must independently calculate OK")
                passed+=1
            except (ValueError,ArithmeticError,KeyError,TypeError) as e: fail("CHECK_BAR_FAILURE",key,str(e))
        for item in policy.get("pvm",[]):
            try:
                for source_cell,expected in item.get("source_cells",{}).items():
                    if self.cells[source_cell]["formula"] or self.value(source_cell)!=Decimal(str(expected)):
                        fail("PVM_SOURCE_MISMATCH",source_cell,"PVM source differs from transaction-linked sales evidence")
                vals=[self.value(item[k]) for k in ("delta","price","volume","mix")]
                if abs(vals[0]-sum(vals[1:]))>=Decimal("0.01"): fail("PVM_NON_ADDITIVE",item["delta"],"PVM does not reconcile")
                for label,actual in zip(("delta","price","volume","mix"),vals):
                    if "expected_"+label in item and actual!=Decimal(str(item["expected_"+label])):
                        fail("PVM_COMPONENT_MISMATCH",item[label],"PVM component differs from trusted decomposition")
            except (ValueError,KeyError,TypeError,ArithmeticError) as e: fail("PVM_ERROR","",str(e))
        for key in policy.get("whole_dollar_cells",[]):
            try:
                tree=Parser(self.cells[key]["formula"] or "").parse()
                if tree[0]!="call" or tree[1]!="ROUND" or len(tree[2])!=2 or tree[2][1]!=("number",Decimal(0)): fail("ROUNDING_REQUIRED",key,"Whole-dollar summary must use ROUND(expression,0)")
            except (ValueError,KeyError) as e: fail("ROUNDING_REQUIRED",key,str(e))
        self.findings=findings
        formulas={key for key,cell in self.cells.items() if cell["formula"]}
        failed={finding["cell_coordinate"] for finding in findings
                if finding["violation_type"] in ("VIO_EMBEDDED_CONSTANT","FORMULA_ERROR","RECALCULATION_MISMATCH")}
        cycles={finding["cell_coordinate"] for finding in findings
                if finding["violation_type"]=="FORMULA_ERROR" and "Circular reference" in finding["rationale"]}
        return {"total_cells_scanned":len(self.cells),"findings":findings,"check_bars_reconciled":passed,
                "formulas_verified_reproducible":len(formulas-failed),
                "circular_references_trapped":len(cycles),"passed":not findings}


# ========================================================================
# Formula audit facade
# ========================================================================

import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple


class AuditSeverity(Enum):
    AUDIT_SEVERITY_UNSPECIFIED = 0
    INFO = 1
    MINOR_OBSERVATION = 2
    MATERIAL_DEFECT = 3
    CRITICAL_DISQUALIFIER = 4


@dataclass
class CellAuditFinding:
    sheet_name: str
    cell_coordinate: str
    formula_raw: str
    violation_type: str
    severity: AuditSeverity
    rationale: str

    def to_dict(self) -> dict:
        return {
            "sheet_name": self.sheet_name,
            "cell_coordinate": self.cell_coordinate,
            "formula_raw": self.formula_raw,
            "violation_type": self.violation_type,
            "severity": self.severity.value,
            "rationale": self.rationale,
        }


# Numeric literal not part of a cell reference (e.g. "=C14*1.08 + 50000").
_HARDCODE_RE = re.compile(r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?")


def find_hardcodes(formula: str) -> List[str]:
    """Return embedded numeric literals in a formula (LP-06 / FA01)."""
    if not (formula or "").lstrip().startswith("="):
        return []
    return constants(Parser(formula).parse())


class ASTAuditor:
    """Multi-pass formula auditor (FA01-FA04)."""

    def audit_formulas(self, cells: Sequence[Tuple[str, str, str]]) -> List[CellAuditFinding]:
        """FA01: flag every formula cell with embedded numeric constants."""
        findings: List[CellAuditFinding] = []
        for sheet, coord, formula in cells:
            hardcodes = find_hardcodes(formula)
            if hardcodes:
                findings.append(CellAuditFinding(
                    sheet_name=sheet, cell_coordinate=coord, formula_raw=formula,
                    violation_type="VIO_EMBEDDED_CONSTANT",
                    severity=AuditSeverity.CRITICAL_DISQUALIFIER,
                    rationale=("Embedded constant(s) " + ", ".join(hardcodes) +
                               " found in formula. All adjustments must reference "
                               "supporting schedules or explicit assumption cells under "
                               "PCAOB AS 1215."),
                ))
        return findings

    def verify_pvm_additive(self, total_delta: Decimal, price: Decimal,
                            volume: Decimal, mix: Decimal, tolerance: Decimal = Decimal("0.01")) -> Tuple[bool, Decimal]:
        """FA02: |Delta - (P + V + M)| < tolerance."""
        residual = total_delta - (price + volume + mix)
        return abs(residual) < tolerance, residual

    def verify_check_bars(self, check_bar_results: Sequence[Tuple[str, bool, Decimal]]) -> Tuple[bool, int]:
        """FA03: every Row 1 check bar must be OK."""
        passed = sum(1 for _, ok, _ in check_bar_results if ok)
        return (passed == len(check_bar_results)), passed

    def verify_recalculation(self, submitted: Dict[str, Decimal],
                             recomputed: Dict[str, Decimal]) -> Tuple[bool, Decimal]:
        """FA04: recomputed totals must match submitted totals to $0.0000."""
        max_delta = Decimal("0")
        for key in submitted:
            delta = abs(submitted[key] - recomputed.get(key, Decimal("0")))
            if delta > max_delta:
                max_delta = delta
        return max_delta == Decimal("0"), max_delta

    def run(self, cells: Sequence[Tuple[str, str, str]],
            pvm: Optional[Tuple[Decimal, Decimal, Decimal, Decimal]] = None,
            check_bars: Sequence[Tuple[str, bool, Decimal]] = (),
            submitted: Optional[Dict[str, Decimal]] = None,
            recomputed: Optional[Dict[str, Decimal]] = None) -> dict:
        """Run the full AST audit and return a proto-shaped ASTAuditReport."""
        findings = self.audit_formulas(cells)
        hardcodes = len(findings)
        check_ok, check_passed = self.verify_check_bars(check_bars)
        recalc_ok, recalc_delta = (True, Decimal("0"))
        if submitted is not None and recomputed is not None:
            recalc_ok, recalc_delta = self.verify_recalculation(submitted, recomputed)
        pvm_ok = True
        if pvm is not None:
            pvm_ok, _ = self.verify_pvm_additive(*pvm)

        return {
            "engagement_id": "",
            "total_cells_scanned": len(cells),
            "formulas_verified_reproducible": len(cells) - hardcodes,
            "hardcoded_constants_flagged": hardcodes,
            "circular_references_trapped": 0,
            "check_bars_reconciled": check_passed,
            "check_bars_ok": check_ok,
            "pvm_additive_ok": pvm_ok,
            "recalculation_ok": recalc_ok,
            "recalculation_max_delta": float(recalc_delta),
            "findings": [f.to_dict() for f in findings],
        }


# ========================================================================
# Canonical evidence and cross-schedule verification
# ========================================================================

def money(value):
    result=Decimal(str(value).replace("$", "").replace(",", ""))
    if not result.is_finite(): raise ValueError("Non-finite amount")
    return result

def path_value(obj,path):
    for part in path.split("."):
        obj=obj[int(part)] if isinstance(obj,list) else obj[part]
    return obj

def verify_submission_evidence(workbook, report, scenario):
    findings=[]
    def defect(q,code,detail):
        findings.append({"quadrant":q,"violation_type":code,"rationale":detail})
    for key,line in scenario["ledger"].items():
        if "cell" in line:
            try:
                if workbook.cells[line["cell"]]["formula"] or workbook.value(line["cell"])!=money(line["amount"]):
                    defect(2,"LEDGER_INPUT_MISMATCH",key)
            except (KeyError,ValueError,ArithmeticError): defect(2,"LEDGER_INPUT_MISSING",key)
    verified=[]
    claim_rows=report.get("sections",{}).get("03_Quality_of_Earnings",{}).get("anomalies",[])
    claims={}; duplicated=set()
    for claim in claim_rows:
        if not isinstance(claim,dict) or not isinstance(claim.get("anomaly_id"),str):
            defect(1,"UNSUPPORTED_ANOMALY","Malformed anomaly claim")
            continue
        identifier=claim["anomaly_id"]
        if identifier in claims or identifier in duplicated:
            defect(1,"UNSUPPORTED_ANOMALY","Duplicate claim: "+identifier)
            claims.pop(identifier,None)
            duplicated.add(identifier)
        else:
            claims[identifier]=claim
    for aid,expected in sorted(scenario["anomalies"].items()):
        try:
            claim=claims[aid]; cell=claim["cell"]
            if cell!=expected["cell"] or money(claim["amount"])!=workbook.value(cell): raise ValueError("Claim differs from schedule")
            if workbook.value(cell)!=money(expected["amount"]): raise ValueError("Incorrect adjustment")
            pending=[cell]; visited=set()
            while pending:
                node=pending.pop()
                if node in visited: continue
                visited.add(node); pending.extend(workbook.dependencies.get(node,()))
            for lid in expected["ledger_ids"]:
                line=scenario["ledger"][lid]
                if line["cell"] not in visited: raise ValueError("Ledger disconnected")
                if workbook.cells[line["cell"]]["formula"]: raise ValueError("Ledger input is a formula")
                if path_value(scenario["documents"][line["document_id"]],line["document_path"])!=line["document_value"]: raise ValueError("Document evidence mismatch")
            if not expected["ledger_ids"]: raise ValueError("No supporting ledger")
            verified.append(aid)
        except (KeyError,ValueError,TypeError,ArithmeticError) as e: defect(1,"UNVERIFIED_ANOMALY",aid+": "+str(e))
    for aid in sorted(set(claims)-set(scenario["anomalies"])): defect(1,"UNSUPPORTED_ANOMALY",aid)
    for item in scenario["replacement_costs"]:
        try:
            if workbook.value(item["net_cell"])!=workbook.value(item["gross_cell"])-money(item["replacement_cost"]): defect(3,"REPLACEMENT_COST",item["net_cell"])
        except (KeyError,ValueError,ArithmeticError): defect(3,"REPLACEMENT_COST",str(item))
    for exposure,cells in scenario["allocations"].items():
        try:
            if sum(workbook.value(c)!=0 for c in cells)>1: defect(3,"DOUBLE_DIPPING",exposure)
        except (ValueError,KeyError,ArithmeticError): defect(3,"ALLOCATION_UNVERIFIED",exposure)
    for item in scenario["reconciliations"]:
        try:
            left=money(path_value(report,item["report_path"]))
            right=workbook.value(item["cell"])
            tolerance=Decimal(1) if item.get("display_only") else Decimal(0)
            if abs(left-right)>tolerance: defect(2,"CROSS_SCHEDULE_MISMATCH",item["report_path"])
        except (KeyError,ValueError,ArithmeticError,TypeError): defect(2,"CROSS_SCHEDULE_MISSING",str(item))
    return findings, verified


def build_scenario_evidence(entries, anomalies):
    """Export compiler provenance, without claiming GL records are primary evidence.

    Stable occurrence keys preserve repeated anomaly types across periods. This
    artifact is private ground truth, not a learner document or grading policy.
    """
    ledger={}
    by_document={}
    for entry in entries:
        for index,line in enumerate(entry.lines):
            identifier=f"{entry.entry_id}-{index:03d}"
            if identifier in ledger: raise ValueError("Duplicate ledger identifier: "+identifier)
            ledger[identifier]={"journal_entry_id":entry.entry_id,
                "sim_year":entry.sim_year,"sim_month":entry.sim_month,
                "account_number":line.account_number,"account_category":line.category.value,
                "debit":str(line.debit),"credit":str(line.credit),
                "signed_amount":str(line.debit-line.credit),"document_ref":entry.document_ref}
            by_document.setdefault((entry.sim_year,entry.sim_month,entry.document_ref),[]).append(identifier)
    occurrences={}
    documents={}
    unresolved=[]
    for anomaly in anomalies:
        required=("anomaly_id","sim_year","sim_month","document_ref","target_gl_accounts","amount")
        if any(key not in anomaly for key in required): raise ValueError("Anomaly lacks explicit compiler provenance")
        key=f"{anomaly['anomaly_id']}:{anomaly['sim_year']}:{anomaly['sim_month']:02d}:{anomaly['document_ref']}"
        if key in occurrences: raise ValueError("Duplicate anomaly occurrence: "+key)
        candidates=by_document.get((anomaly["sim_year"],anomaly["sim_month"],anomaly["document_ref"]),[])
        linked=sorted(identifier for identifier in candidates if ledger[identifier]["account_number"] in anomaly["target_gl_accounts"])
        if not linked: raise ValueError("No matching ledger provenance for "+key)
        document=anomaly.get("source_evidence")
        if document:
            documents[key]={"document_ref":anomaly["document_ref"],"origin":"simulated_operational_source",**document}
        occurrences[key]={**anomaly,"source_document_id":key if document else None,"ledger_ids":linked,
                          "missing_bindings":["workbook_calculation_cell"] + ([] if document else ["primary_document_json_path"])}
        unresolved.append(key)
    return {"schema_version":"1.0","ledger":ledger,"documents":documents,"anomaly_occurrences":occurrences,
            "unresolved_occurrences":unresolved,"ready_for_certification":False,
            "provenance_kind":"compiler_ledger_lineage"}

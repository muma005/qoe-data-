"""Read-only Stage 2 checksum handoff verification for two compiled packages."""

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


SEED = "0x4a9f82c1e703bd55"
SCENARIO = "target_apex_supply"
ORIGINAL = (
    "ground_truth.duckdb", "manifest.json", "operational_trajectory.json",
    "injected_anomalies.json", "sales_lines.json", "audit_evidence.json",
    "audit_policy.json", "vdr_artifacts/operational_source_documents.json",
    "vdr_artifacts/product_sales_lines.json",
)


def checksum_file(package):
    entries = {}
    seen_casefold = set()
    for number, line in enumerate((package / "checksum.sha256").read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([a-fA-F0-9]{64})  ([^\r\n]+)", line)
        if not match:
            raise ValueError(f"Invalid checksum format at line {number}")
        digest, relative = match.groups()
        path = PurePosixPath(relative)
        if (path.is_absolute() or not relative or "\\" in relative or ":" in relative
                or any(segment in (".", "..") for segment in relative.split("/"))
                or relative.startswith("/") or "//" in relative):
            raise ValueError(f"Unsafe checksum path at line {number}: {relative}")
        if relative.casefold() in seen_casefold:
            raise ValueError(f"Duplicate checksum path at line {number}: {relative}")
        seen_casefold.add(relative.casefold())
        entries[relative] = digest.lower()
    return entries


def hash_file(path):
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def verify(package, expected_count):
    root = package.resolve(strict=True)
    entries = checksum_file(root)
    problems = []
    if len(entries) != expected_count:
        problems.append(f"Expected {expected_count} checksum entries; found {len(entries)}")
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("scenario_id") != SCENARIO or manifest.get("random_seed") != int(SEED, 16):
        problems.append("Manifest scenario ID or seed differs from the intended Apex run")
    results = {}
    for relative, expected in entries.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            problems.append(f"Path escapes package: {relative}")
            results[relative] = (expected, "-", 0, "UNSAFE")
        elif not path.is_file():
            problems.append(f"File missing or not a regular file: {relative}")
            results[relative] = (expected, "-", 0, "MISSING")
        else:
            actual, size = hash_file(path)
            status = "PASS" if actual == expected else "MISMATCH"
            if status != "PASS":
                problems.append(f"Hash mismatch: {relative}")
            results[relative] = (expected, actual, size, status)
    return entries, results, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--rebuilt", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    baseline, base_rows, base_problems = verify(args.baseline, 9)
    rebuilt, new_rows, new_problems = verify(args.rebuilt, 43)
    problems = base_problems + new_problems
    if set(baseline) != set(ORIGINAL):
        problems.append("Stage 1 nine-entry list differs from the compiler's original nine")
    for name in ORIGINAL:
        if name not in baseline or name not in rebuilt:
            problems.append(f"Original entry absent from one package: {name}")
        elif baseline[name] != rebuilt[name] or base_rows[name][1] != new_rows[name][1]:
            problems.append(f"Stage 1 and rebuilt package differ: {name}")

    catalog_path = args.rebuilt / "vdr_artifacts" / "json" / "catalog.json"
    if "vdr_artifacts/json/catalog.json" not in rebuilt or not catalog_path.is_file():
        problems.append("Catalog is missing or unsealed")
        catalog_paths = set()
    elif new_rows["vdr_artifacts/json/catalog.json"][3] != "PASS":
        problems.append("Catalog checksum failed; catalog coverage cannot be trusted")
        catalog_paths = set()
    else:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog_paths = [record["path"] for record in catalog["documents"]]
        if len(catalog_paths) != len(set(catalog_paths)) or len(catalog_paths) != 25:
            problems.append("Expected 25 unique cataloged VDR documents")
        for name in catalog_paths:
            if name not in rebuilt:
                problems.append(f"Cataloged VDR document has no checksum entry: {name}")

    unlisted = sorted(path.relative_to(args.rebuilt).as_posix()
                      for path in args.rebuilt.rglob("*")
                      if path.is_file() and path.relative_to(args.rebuilt).as_posix() not in rebuilt)

    lines = ["# Stage 2, step 5: package-wide checksum verification", "",
             "## Inputs and method", "",
             f"- Stage 1 baseline: `{args.baseline.resolve()}`",
             f"- Rebuilt handoff: `{args.rebuilt.resolve()}`",
             f"- Expected scenario: `{SCENARIO}`; seed: `{SEED}`.",
             "- Parsed the compiler's `SHA-256  relative/path` lines; rejected unsafe and duplicate paths.",
             "- Streamed each existing file's bytes through SHA-256; compared with its recorded digest.",
             "- Compared the original nine paths and hashes across packages and checked VDR catalog coverage.",
             "- The verification did not modify either package.", "",
             "## Observed results", "",
             "| Check | Observed |", "| --- | --- |",
             f"| Baseline sealed files | {sum(r[3] == 'PASS' for r in base_rows.values())}/{len(base_rows)} matching |",
             f"| Rebuilt sealed files | {sum(r[3] == 'PASS' for r in new_rows.values())}/{len(new_rows)} matching |",
             f"| Shared original files | {len(ORIGINAL)} paths compared |",
             f"| Catalog coverage | {len(catalog_paths)} document paths; catalog itself sealed |",
             f"| Package files outside checksum list | {len(unlisted)} (named below) |",
             f"| Overall step 5 | {'PASS' if not problems else 'FAIL'} |", "",
             "## Rebuilt package: each listed file", "",
             "| Listed path | Bytes | Recorded SHA-256 | Calculated SHA-256 | Result |",
             "| --- | ---: | --- | --- | --- |"]
    for name, (expected, actual, size, status) in new_rows.items():
        lines.append(f"| `{name}` | {size:,} | `{expected}` | `{actual}` | {status} |")
    lines.extend(["", "## Stage 1 baseline: each listed file", "",
                  "| Listed path | Bytes | Recorded SHA-256 | Calculated SHA-256 | Result |",
                  "| --- | ---: | --- | --- | --- |"])
    for name, (expected, actual, size, status) in base_rows.items():
        lines.append(f"| `{name}` | {size:,} | `{expected}` | `{actual}` | {status} |")
    lines.extend(["", "## Discrepancies", ""])
    lines.extend(f"- {problem}" for problem in problems)
    if not problems:
        lines.append("None in the checks above.")
    lines.extend(["", "## Package files not named in the checksum list", ""])
    lines.extend(f"- `{name}`" for name in unlisted)
    lines.extend(["", "## Scope", "",
                  "This confirms the files listed in the checksum manifests, not every file in either package. "
                  "The checksum file itself cannot practically include its own hash. In the rebuilt package, "
                  "all other package files are now listed and checked. "
                  "It does not assess source realism or prove that an external document exists. "
                  "Negative rejection cases belong to Stage 2 step 6. The sibling `.tar.gz` archive is outside these checksum lists.", ""])
    args.report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Baseline {sum(r[3] == 'PASS' for r in base_rows.values())}/{len(base_rows)}; "
          f"rebuilt {sum(r[3] == 'PASS' for r in new_rows.values())}/{len(new_rows)}; "
          f"catalog {len(catalog_paths)}; discrepancies {len(problems)}; "
          f"result {'PASS' if not problems else 'FAIL'}")
    for problem in problems:
        print("FAIL:", problem)
    raise SystemExit(1 if problems else 0)


if __name__ == "__main__":
    main()

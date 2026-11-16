#!/usr/bin/env python3
"""Parse requirement cards out of docs/01-requirements.md into build/requirements.json.

Keeps the Word document and the PDF/Markdown from drifting apart: the Markdown
file is the single source of truth, and build_docx.js reads the JSON this emits.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
md = (ROOT / "docs/01-requirements.md").read_text()


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def rows_after(text):
    """Read a pipe table that starts at the top of `text`; return its data rows."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if out:
                break
            continue
        if re.fullmatch(r"\|[\s:|-]+\|", line):
            continue
        out.append(cells(line))
    return out


def strip_bold(s):
    return re.sub(r"^\*\*(.+)\*\*$", r"\1", s.strip())


# --- requirement cards: "### FR-001 — Title" followed by a Field|Detail table ---
cards = []
for m in re.finditer(r"^### ((?:N?FR)-\d{3}) — (.+?)$", md, flags=re.M):
    rid, title = m.group(1), m.group(2).strip()
    body = md[m.end():]
    table = rows_after(body)
    table = [r for r in table if len(r) == 2 and strip_bold(r[0]) != "Field"]
    cards.append({"id": rid, "title": title,
                  "rows": [[strip_bold(a), b] for a, b in table]})

# --- named tables, located by their section heading ---
def section_table(heading):
    m = re.search(r"^## " + re.escape(heading) + r"\s*$", md, flags=re.M)
    if not m:
        raise SystemExit(f"section not found: {heading}")
    return rows_after(md[m.end():])


data = {
    "actors":       section_table("1. Actors in Scope"),
    "frSummary":    section_table("2. Functional Requirements — Summary Table"),
    "nfrSummary":   section_table("3. Non-Functional Requirements — Summary Table"),
    "traceability": section_table("6. Requirements Traceability Matrix"),
    "fr":  [c for c in cards if c["id"].startswith("FR-")],
    "nfr": [c for c in cards if c["id"].startswith("NFR-")],
}

note = re.search(r"^> (\*\*Scope note\.\*\*.+)$", md, flags=re.M)
data["scopeNote"] = note.group(1) if note else ""

(ROOT / "build/requirements.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
print(f"parsed {len(data['fr'])} FRs, {len(data['nfr'])} NFRs, "
      f"{len(data['actors'])} actors, {len(data['traceability'])} traceability rows")

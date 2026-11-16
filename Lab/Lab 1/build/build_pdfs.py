#!/usr/bin/env python3
"""Assemble the two Google-Form submission PDFs for Lab 1 (PS #53)."""
import re, subprocess, sys, pathlib, base64

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
OUT = ROOT / "submission"
OUT.mkdir(exist_ok=True)

NAME = sys.argv[1] if len(sys.argv) > 1 else "________________________"
SRN  = sys.argv[2] if len(sys.argv) > 2 else "________________________"

CSS = (BUILD / "print.css").read_text()

HDR = ('<table class="hdr"><tr>'
       f'<td><b>Name:</b> {NAME} &nbsp;&nbsp;|&nbsp;&nbsp; <b>SRN:</b> {SRN}</td>'
       '<td>PES University · Dept. of CSE · Software Engineering Lab 1</td>'
       '</tr></table>')


def md_to_html(path):
    return subprocess.run(
        ["pandoc", str(path), "-f", "gfm", "-t", "html5"],
        capture_output=True, text=True, check=True).stdout


def polish(html):
    """Drop pandoc's h1/lead paragraph, tag Field/Detail tables, tidy rules."""
    html = re.sub(r"<h1 .*?</h1>", "", html, count=1, flags=re.S)
    html = re.sub(r"^\s*<p><strong>System:.*?</p>", "", html, count=1, flags=re.S)
    html = re.sub(r"^\s*<p><strong>System:.*?</p>", "", html, count=1, flags=re.S)
    html = html.replace("<hr />", "")
    # Two-column "Field | Detail" tables get fixed label-column width
    html = re.sub(
        r"<table>(\s*<thead>\s*<tr class=\"header\">\s*<th>Field</th>)",
        r'<table class="idcard">\1', html)
    # Requirement/use-case IDs must never break across lines
    html = re.sub(r"\b((?:NFR|FR|UC|BR)-\d{2,3})\b", r'<span class="nb">\1</span>', html)
    # Keep each heading glued to the block it introduces (no orphaned headings)
    html = re.sub(
        r"(<h[23][^>]*>.*?</h[23]>)\s*(<(?:table|figure|p)\b.*?</(?:table|figure|p)>)",
        r'<div class="keep">\1\2</div>', html, flags=re.S)
    return html


def embed(img: pathlib.Path):
    b64 = base64.b64encode(img.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def page(title, sub, body):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<title>{title}</title><style>{CSS}</style></head><body>
{HDR}
<h1>{title}</h1>
<p class="sub">{sub}</p>
{body}
</body></html>"""


def render(html_path, pdf_path):
    subprocess.run([
        "wkhtmltopdf", "--enable-local-file-access", "--page-size", "A4",
        "--margin-top", "14mm", "--margin-bottom", "14mm",
        "--margin-left", "13mm", "--margin-right", "13mm",
        str(html_path), str(pdf_path)],
        capture_output=True, check=True)
    data = pdf_path.read_bytes()
    return data.count(b"/Type /Page") - data.count(b"/Type /Pages")


# ---------------------------------------------------------------- PDF 1
req_body = polish(md_to_html(ROOT / "docs/01-requirements.md"))
p1 = BUILD / "requirements.html"
p1.write_text(page(
    "Requirements Table — CreatorEscrow",
    "Freelance Content Creator Escrow Platform · Problem Statement #53 (Media, Events &amp; Community) · "
    "Lab 1 Deliverable: 5 Functional + 2 Non-Functional Requirements",
    req_body))
n1 = render(p1, OUT / "Requirements-Table_PS53.pdf")

# ---------------------------------------------------------------- PDF 2
uml_md = polish(md_to_html(ROOT / "docs/02-use-case-diagram.md"))
# strip everything from "## 1. Diagram" heading through the regeneration code block,
# and the mermaid block (replaced by a rendered PlantUML state diagram)
uml_md = re.sub(r"<h2 id=\"1-diagram\">.*?<h2 id=\"2-actor-catalogue\">",
                '<h2 id="2-actor-catalogue">', uml_md, flags=re.S)
uml_md = re.sub(r"<div class=\"sourceCode\".*?</div>\s*", "", uml_md, flags=re.S)
uml_md = re.sub(r"<pre class=\"mermaid\">.*?</pre>", "", uml_md, flags=re.S)
uml_md = re.sub(r"<pre><code class=\"mermaid\">.*?</code></pre>", "", uml_md, flags=re.S)
uml_md = re.sub(r"<div class=\"keep\">\\s*<h2 id=\"5-milestone-state-model-supporting-view\">.*$",
                "", uml_md, flags=re.S)
uml_md = uml_md.replace("<b>Detailed in Deliverable 3.</b>",
                        "<b>Detailed in Section 6 of this document.</b>")
uml_md = uml_md.replace("<strong>Detailed in Deliverable 3.</strong>",
                        "<strong>Detailed in Section 6 of this document.</strong>")

diagram = f"""
<div class="keep">
<h2>1. Use-Case Diagram</h2>
<figure>
  <img src="{embed(ROOT / 'build/hires/use-case-diagram.png')}" style="width:100%;">
  <figcaption>Figure 1 — CreatorEscrow use-case model: 2 primary actors, 2 supporting
  external actors, 12 use cases, 5 «include» and 2 «extend» relationships.</figcaption>
</figure>
"""

state = f"""
<div class="keep">
<h2>5. Milestone State Model (supporting view)</h2>
<p>The use cases above operate on a single milestone state machine, included here to make the
guard conditions in the flow specification unambiguous.</p>
<figure>
  <img src="{embed(ROOT / 'build/hires/milestone-state-machine.png')}" style="width:78%;">
  <figcaption>Figure 2 — Milestone lifecycle, annotated with the requirement or use case
  that drives each transition.</figcaption>
</figure>
</div>
"""

flow_html = (ROOT / "docs/03-use-case-flow-UC-05.html").read_text()
flow_body = re.search(r"<body>(.*?)</body>", flow_html, re.S).group(1)
flow_body = re.sub(r"<h1>.*?</h1>\s*<p class=\"sub\">.*?</p>", "", flow_body, flags=re.S)
flow = ('<h2>6. Use-Case Flow Specification — UC-05 (Appendix)</h2>'
        '<p class="note">Included for completeness: the detailed flow for the core use case '
        'UC-05 <i>Approve Milestone &amp; Release Escrow Payment</i>, the only use case that '
        'moves money.</p>' + flow_body)

p2 = BUILD / "uml-usecase.html"
p2.write_text(page(
    "UML Use-Case Model — CreatorEscrow",
    "Freelance Content Creator Escrow Platform · Problem Statement #53 (Media, Events &amp; Community) · "
    "Lab 1 Deliverable: Use-Case Diagram with «include» and «extend» relationships",
    diagram + uml_md + state + flow))
n2 = render(p2, OUT / "UML-UseCase_PS53.pdf")

print(f"Requirements-Table_PS53.pdf : {n1} page(s)")
print(f"UML-UseCase_PS53.pdf        : {n2} page(s)")

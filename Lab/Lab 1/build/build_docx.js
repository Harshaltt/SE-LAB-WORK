const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, HeadingLevel, BorderStyle,
  TabStopType, TabStopPosition,
} = require('docx');

const DATA = JSON.parse(fs.readFileSync(__dirname + '/requirements.json', 'utf8'));

const NAME = process.argv[2] || '________________________';
const SRN  = process.argv[3] || '________________________';

const W = 9746;                       // usable width (A4, 0.75" margins)
const HDR_FILL = 'EEF2F5';
const ALT_FILL = 'FAFBFC';
const LABEL_FILL = 'F5F7F9';
const RULE = '9AA7B2';
const ACCENT = '00463C';

/* ---------- inline markdown: **bold**, *italic*, `code` ---------- */
function runs(text, base = {}) {
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  for (const p of parts) {
    if (!p) continue;
    if (p.startsWith('**') && p.endsWith('**')) {
      out.push(new TextRun({ ...base, text: p.slice(2, -2), bold: true }));
    } else if (p.startsWith('`') && p.endsWith('`')) {
      out.push(new TextRun({ ...base, text: p.slice(1, -1), font: 'Consolas', size: 17 }));
    } else if (p.startsWith('*') && p.endsWith('*')) {
      out.push(new TextRun({ ...base, text: p.slice(1, -1), italics: true }));
    } else {
      out.push(new TextRun({ ...base, text: p }));
    }
  }
  return out;
}

function cell(text, width, opts = {}) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { type: ShadingType.CLEAR, color: 'auto', fill: opts.fill } : undefined,
    margins: { top: 60, bottom: 60, left: 90, right: 90 },
    children: [new Paragraph({
      spacing: { before: 0, after: 0, line: 232 },
      keepNext: opts.keepNext || undefined,
      children: runs(text, { size: 17, bold: opts.bold || undefined }),
    })],
  });
}

function table(widths, rows, opts = {}) {
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths,
    borders: {
      top:    { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
      bottom: { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
      left:   { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
      right:  { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
      insideVertical:   { style: BorderStyle.SINGLE, size: 3, color: 'B8C2CB' },
    },
    rows: rows.map((cells, r) => new TableRow({
      tableHeader: r === 0 && opts.header !== false,
      cantSplit: true,
      children: cells.map((t, c) => cell(t, widths[c], {
        keepNext: opts.keepTogether && r < rows.length - 1,
        bold: (r === 0 && opts.header !== false) || (opts.labelCol && c === 0),
        fill: (r === 0 && opts.header !== false) ? HDR_FILL
            : (opts.labelCol && c === 0) ? LABEL_FILL
            : (opts.zebra && r % 2 === 0) ? ALT_FILL : undefined,
      })),
    })),
  });
}

const gap = (after = 90) => new Paragraph({ spacing: { after }, children: [] });

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 260, after: 110 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RULE, space: 3 } },
    children: [new TextRun({ text, bold: true, size: 21, color: '0B1418' })],
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 150, after: 70 },
    keepNext: true,
    children: [new TextRun({ text, bold: true, size: 19, color: ACCENT })],
  });
}

/* ---------- requirement card ---------- */
function reqCard(id, title, rows) {
  return [h2(`${id} — ${title}`), table([1900, 7846], rows, { header: false, labelCol: true, keepTogether: true }), gap()];
}


const children = [];

/* running header line */
children.push(new Paragraph({
  spacing: { after: 60 },
  tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'D5DCE2', space: 4 } },
  children: [
    new TextRun({ text: 'Name: ', bold: true, size: 16 }),
    new TextRun({ text: NAME, size: 16 }),
    new TextRun({ text: '    |    SRN: ', bold: true, size: 16 }),
    new TextRun({ text: SRN, size: 16 }),
    new TextRun({ text: '\tPES University · Dept. of CSE · Software Engineering Lab 1', size: 16, color: '4A5560' }),
  ],
}));

children.push(new Paragraph({
  spacing: { before: 160, after: 40 },
  children: [new TextRun({ text: 'Requirements Table — CreatorEscrow', bold: true, size: 30, color: '0B1418' })],
}));
children.push(new Paragraph({
  spacing: { after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: '37474F', space: 4 } },
  children: [new TextRun({
    text: 'Freelance Content Creator Escrow Platform · Problem Statement #53 (Media, Events & Community) · Lab 1 Deliverable: 5 Functional + 2 Non-Functional Requirements',
    size: 16, color: '4A5560',
  })],
}));

children.push(h1('1. Actors in Scope'));
children.push(table([2200, 2000, 5546], DATA.actors, { zebra: true }));
children.push(gap());

children.push(h1('2. Functional Requirements — Summary Table'));
children.push(table([1000, 2300, 5246, 1200], DATA.frSummary, { zebra: true }));
children.push(gap());

children.push(h1('3. Non-Functional Requirements — Summary Table'));
children.push(table([1000, 2300, 5246, 1200], DATA.nfrSummary, { zebra: true }));
children.push(gap());

children.push(h1('4. Functional Requirements — Full Specification'));
DATA.fr.forEach((c) => children.push(...reqCard(c.id, c.title, c.rows)));

children.push(h1('5. Non-Functional Requirements — Full Specification'));
DATA.nfr.forEach((c) => children.push(...reqCard(c.id, c.title, c.rows)));

children.push(h1('6. Requirements Traceability Matrix'));
children.push(table([2900, 3200, 3646], DATA.traceability, { zebra: true }));

children.push(new Paragraph({
  spacing: { before: 140 },
  shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F6F8FA' },
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: RULE, space: 6 } },
  children: runs(DATA.scopeNote, { size: 16, color: '333C44' }),
}));

const doc = new Document({
  creator: NAME,
  title: 'Requirements Table — CreatorEscrow (Problem Statement #53)',
  description: 'Lab 1: Requirements Engineering & UML Use-Case Modelling',
  styles: {
    default: { document: { run: { font: 'Calibri', size: 19, color: '14181C' } } },
  },
  sections: [{
    properties: { page: { margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(process.argv[4] || 'Requirements-Table_PS53.docx', buf);
  console.log('written');
});

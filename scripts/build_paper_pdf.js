/**
 * CloudRescue Research Paper — IEEE-Style Publication PDF Generator
 * 
 * Complete publication-ready pipeline:
 * 1. Formats paper header, title, authors, affiliation, and abstract in authentic IEEE Transactions style
 * 2. Inlines all 6 high-res publication figures (Base64) and ASCII architecture diagram
 * 3. Pre-renders all 1,362+ LaTeX math formulas via KaTeX (MathML + HTML) with zero placeholders
 * 4. Structures formal IEEE Section numerals (I..IX), subsections (A..L), and sub-subsections (1..3)
 * 5. Formats IEEE booktabs styling for Tables I, II-A..D, III, IV, and V with two-column spanning
 * 6. Enforces IEEE typography (Times New Roman, two-column, 9.5pt, justified, running headers/footers)
 * 7. Compiles to paper/CloudRescue_Research_Paper_Final.pdf via Headless Chrome (Skia/PDF)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const DRAFT_PATH = path.join(PROJECT_ROOT, 'paper', 'CloudRescue_Research_Paper_Draft.md');
const HTML_OUTPUT_PATH = path.join(PROJECT_ROOT, 'paper', 'CloudRescue_Research_Paper_Final.html');
const PDF_OUTPUT_PATH = path.join(PROJECT_ROOT, 'paper', 'CloudRescue_Research_Paper_Final.pdf');

// Load KaTeX & MarkdownIt
const katex = require('/tmp/katex_tool/node_modules/katex');
const MarkdownIt = require('/tmp/katex_tool/node_modules/markdown-it');

console.log('Step 1: Reading markdown manuscript from:', DRAFT_PATH);
let rawMarkdown = fs.readFileSync(DRAFT_PATH, 'utf-8');

// Step 1b: Convert local file:/// URLs to public GitHub repository URLs for clickable links
rawMarkdown = rawMarkdown.replace(/file:\/\/\/home\/andesindica\/Downloads\/CloudRescue-Research\//g, 'https://github.com/hariprasadkishan/CloudRescue-Research/blob/main/');

// Step 2: Strip draft preamble metadata (Working Title, Document Stage, etc.)
rawMarkdown = rawMarkdown.replace(/^#\s+Autonomic Cloud Resilience[\s\S]*?---\s*\n/m, '');

// Step 3: Extract Abstract and Keywords to format in IEEE full-width header
const abstractRegex = /##\s*1\.\s*Abstract\s*\n\n([\s\S]*?)\n\n\*\*Keywords:\*\*\s*([^\n]+)\s*\n\n---\s*\n/m;
let rawAbstractBody = '';
let rawKeywords = '';
const abstractMatch = rawMarkdown.match(abstractRegex);

if (abstractMatch) {
  rawAbstractBody = abstractMatch[1].trim();
  rawKeywords = abstractMatch[2].trim();
  rawMarkdown = rawMarkdown.replace(abstractRegex, '');
}

// Step 4: Load base64 plots
console.log('Step 2: Encoding publication plots to Base64...');
const plotsDir = path.join(PROJECT_ROOT, 'results', 'experiment_360', 'plots');
const plotFiles = {
  'sla_violation_rates_bar.png': fs.readFileSync(path.join(plotsDir, 'sla_violation_rates_bar.png')).toString('base64'),
  'latency_cdf_comparison.png': fs.readFileSync(path.join(plotsDir, 'latency_cdf_comparison.png')).toString('base64'),
  'time_series_dynamics_compound.png': fs.readFileSync(path.join(plotsDir, 'time_series_dynamics_compound.png')).toString('base64'),
  'fairness_and_utilization_box.png': fs.readFileSync(path.join(plotsDir, 'fairness_and_utilization_box.png')).toString('base64'),
  'fidelity_vs_reliability_tradeoff.png': fs.readFileSync(path.join(plotsDir, 'fidelity_vs_reliability_tradeoff.png')).toString('base64'),
  'sensitivity_heatmap.png': fs.readFileSync(path.join(plotsDir, 'sensitivity_heatmap.png')).toString('base64'),
};

// Step 5: Structure Figures and Architecture Diagram BEFORE KaTeX pre-rendering
console.log('Step 3: Structuring figures and architecture diagram with LaTeX math...');

// Figure 1: Architecture ASCII Diagram
const fig1Regex = /CloudRescue models an autonomic cloud microservice cluster[\s\S]*?```text([\s\S]*?)```\s*\*Figure 1:.*?\*/;
rawMarkdown = rawMarkdown.replace(fig1Regex, (match, asciiContent) => {
  return `CloudRescue models an autonomic cloud microservice cluster consisting of an ingress load balancer dispatching requests to $M = 4$ independent worker instances. The overall architecture is depicted in Fig. 1.

\n\n<div class="figure-container figure-span-all">
  <div class="architecture-box">
    <pre class="architecture-pre">${asciiContent.trim()}</pre>
  </div>
  <div class="figure-caption"><strong>Fig. 1.</strong> Logical system architecture of the CloudRescue autonomic cloud resilience framework. Ingress requests are routed by BALB (CFG-C) using composite elasticity-backlog-utilization dispatch scoring. Individual workers execute a local velocity-form PI feedback controller modulating dimmer $\\theta_w$ to satisfy SLA response latency setpoint ($r_{\\text{target}} = 80\\text{ ms}$).</div>
</div>\n\n`;
});

// Figures 2 - 7: PNG Plot figures
const figureConfigs = [
  {
    num: 2,
    file: 'sla_violation_rates_bar.png',
    title: 'Overall SLA failure rates ($V_{\\text{overall}}$) and latency SLA violation rates ($V_{\\text{lat}}$) across configurations and stress scenarios.',
    spanAll: true,
  },
  {
    num: 3,
    file: 'latency_cdf_comparison.png',
    title: 'Empirical cumulative distribution functions (CDFs) of end-to-end response latency for successful requests across configurations under Compound Stress.',
    spanAll: false,
  },
  {
    num: 4,
    file: 'time_series_dynamics_compound.png',
    title: 'Detailed per-second time-series telemetry (seed 1001) under Compound Stress, illustrating the onset of failure ($t = 300\\text{ s}$), dimmer shedding, queue buffer dynamics, and post-repair recovery ($t = 450\\text{ s}$).',
    spanAll: true,
  },
  {
    num: 5,
    file: 'fidelity_vs_reliability_tradeoff.png',
    title: 'Scatter distribution of Service Fidelity ($F$) versus Overall SLA Failure Rate ($V_{\\text{overall}}$), characterizing the trade-off envelope between feature richness and SLA compliance.',
    spanAll: false,
  },
  {
    num: 6,
    file: 'fairness_and_utilization_box.png',
    title: 'Distribution of Jain\'s Fairness Index ($J$) evaluated across active zero-downtime workers and aggregate worker utilization ($\\bar{U}$).',
    spanAll: false,
  },
  {
    num: 7,
    file: 'sensitivity_heatmap.png',
    title: 'Exploratory parameter sensitivity heatmap of overall SLA failure rate ($V_{\\text{overall}}$) across combinations of dimmer weight $\\alpha$, queue penalty $\\beta$, and CPU utilization weight $\\gamma$ under Compound Stress.',
    spanAll: true,
  },
];

figureConfigs.forEach((cfg) => {
  const figPattern = new RegExp(`!\\[Figure ${cfg.num}:[^\\]]*\\]\\([^\\)]*${cfg.file}\\)\\s*\\n\\s*\\*Figure ${cfg.num}:[^*]*\\*`, 'g');
  const spanClass = cfg.spanAll ? 'figure-span-all' : '';
  const figHtml = `\n\n<div class="figure-container ${spanClass}">
  <img src="data:image/png;base64,${plotFiles[cfg.file]}" alt="Fig. ${cfg.num}" />
  <div class="figure-caption"><strong>Fig. ${cfg.num}.</strong> ${cfg.title}</div>
</div>\n\n`;
  rawMarkdown = rawMarkdown.replace(figPattern, figHtml);
});

// Step 6: Pre-render LaTeX mathematical equations with KaTeX
console.log('Step 4: Pre-rendering all LaTeX mathematical equations with KaTeX...');

let eqCounter = 1;
const displayMathList = [];
const inlineMathList = [];

// Helper function to render inline math
function renderInlineMath(formula) {
  const clean = formula.trim();
  try {
    return katex.renderToString(clean, {
      displayMode: false,
      throwOnError: false,
      output: 'htmlAndMathml',
    });
  } catch (err) {
    return `<span>${clean}</span>`;
  }
}

// 1. Replace display math $$ ... $$ with HTML tags surrounded by blank lines
// (Ensures CommonMark block termination so following markdown lines parse properly)
rawMarkdown = rawMarkdown.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
  const cleanFormula = formula.trim();
  const id = displayMathList.length;
  let rendered = '';
  try {
    rendered = katex.renderToString(cleanFormula, {
      displayMode: true,
      throwOnError: false,
      output: 'htmlAndMathml',
    });
  } catch (err) {
    rendered = `<div class="katex-error">${cleanFormula}</div>`;
  }
  displayMathList.push({
    rendered,
    eqNum: eqCounter++,
  });
  return `\n\n<div data-display-math="${id}"></div>\n\n`;
});

// 2. Replace inline math $ ... $ with placeholder tags
rawMarkdown = rawMarkdown.replace(/(?<!\\)\$((?:\\\$|[^\$\n])+?)(?<!\\)\$/g, (match, formula) => {
  const id = inlineMathList.length;
  const rendered = renderInlineMath(formula);
  inlineMathList.push(rendered);
  return `<span data-inline-math="${id}"></span>`;
});

console.log(`  Rendered ${displayMathList.length} display equations and ${inlineMathList.length} inline math expressions.`);

// Step 7: Configure MarkdownIt parser
console.log('Step 5: Converting Markdown to HTML with IEEE typography...');
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: false,
});

// Render Abstract text through MarkdownIt with math rendered
let renderedAbstractBody = rawAbstractBody.replace(/(?<!\\)\$((?:\\\$|[^\$\n])+?)(?<!\\)\$/g, (match, formula) => {
  return renderInlineMath(formula);
});
renderedAbstractBody = md.render(renderedAbstractBody);
// Inject "Abstract—" at start of first paragraph
renderedAbstractBody = renderedAbstractBody.replace('<p>', '<p class="ieee-abstract-para"><span class="ieee-abstract-head">Abstract</span>—');
renderedAbstractBody = renderedAbstractBody.replace(/<p>/g, '<p class="ieee-abstract-para">');

let renderedKeywords = rawKeywords.replace(/(?<!\\)\$((?:\\\$|[^\$\n])+?)(?<!\\)\$/g, (match, formula) => {
  return renderInlineMath(formula);
});
const keywordsHtml = `<p class="ieee-keywords-para"><span class="ieee-keywords-head">Index Terms</span>—${renderedKeywords}</p>`;

let htmlBody = md.render(rawMarkdown);

// Step 8: Restore KaTeX display math with IEEE equation numbers
htmlBody = htmlBody.replace(/<div data-display-math="(\d+)"><\/div>/g, (match, idx) => {
  const item = displayMathList[parseInt(idx, 10)];
  return `
    <div class="equation-row">
      <div class="equation-content">${item.rendered}</div>
      <div class="equation-num">(${item.eqNum})</div>
    </div>
  `;
});

// Step 9: Restore KaTeX inline math
htmlBody = htmlBody.replace(/<span data-inline-math="(\d+)"><\/span>/g, (match, idx) => {
  return inlineMathList[parseInt(idx, 10)];
});

// Step 10: Format Section Headers in IEEE Style (Roman numerals)
const sectionReplacements = [
  { from: '<h2>2. Introduction</h2>', to: '<h2 class="ieee-sec">I. INTRODUCTION</h2>' },
  { from: '<h2>3. Problem Statement and Research Objectives</h2>', to: '<h2 class="ieee-sec">II. PROBLEM STATEMENT AND RESEARCH OBJECTIVES</h2>' },
  { from: '<h2>4. Research Contributions</h2>', to: '<h2 class="ieee-sec">III. RESEARCH CONTRIBUTIONS</h2>' },
  { from: '<h2>5. Related Work</h2>', to: '<h2 class="ieee-sec">IV. RELATED WORK</h2>' },
  { from: '<h2>6. Proposed CloudRescue Architecture</h2>', to: '<h2 class="ieee-sec">V. PROPOSED CLOUDRESCUE ARCHITECTURE</h2>' },
  { from: '<h2>7. Experimental Methodology</h2>', to: '<h2 class="ieee-sec">VI. EXPERIMENTAL METHODOLOGY</h2>' },
  { from: '<h2>8. Results and Evaluation</h2>', to: '<h2 class="ieee-sec">VII. RESULTS AND EVALUATION</h2>' },
  { from: '<h2>9. Discussion and Limitations</h2>', to: '<h2 class="ieee-sec">VIII. DISCUSSION AND LIMITATIONS</h2>' },
  { from: '<h2>10. Conclusion and Future Work</h2>', to: '<h2 class="ieee-sec">IX. CONCLUSION AND FUTURE WORK</h2>' },
  { from: '<h2>References</h2>', to: '<h2 class="ieee-sec">REFERENCES</h2>' },
  { from: '<h2>Appendix: Repository Artifacts &amp; Verification Provenance</h2>', to: '<h2 class="ieee-sec">APPENDIX: REPOSITORY ARTIFACTS &amp; VERIFICATION PROVENANCE</h2>' },
];

sectionReplacements.forEach(({ from, to }) => {
  htmlBody = htmlBody.replace(from, to);
});

// Format Subsections: <h3>3.1 Problem Formulation...</h3> -> <h3 class="ieee-subsec"><em>A. Problem Formulation...</em></h3>
const subSecMap = {
  '3.1': 'A', '3.2': 'B', '3.3': 'C', '3.4': 'D',
  '5.1': 'A', '5.2': 'B', '5.3': 'C', '5.4': 'D',
  '6.1': 'A', '6.2': 'B', '6.3': 'C', '6.4': 'D',
  '7.1': 'A', '7.2': 'B', '7.3': 'C', '7.4': 'D', '7.5': 'E', '7.6': 'F',
  '7.7': 'G', '7.8': 'H', '7.9': 'I', '7.10': 'J', '7.11': 'K', '7.12': 'L',
  '8.1': 'A', '8.2': 'B', '8.3': 'C', '8.4': 'D', '8.5': 'E', '8.6': 'F', '8.7': 'G',
  '9.1': 'A', '9.2': 'B', '9.3': 'C', '9.4': 'D', '9.5': 'E', '9.6': 'F', '9.7': 'G',
  '10.1': 'A', '10.2': 'B',
};

Object.entries(subSecMap).forEach(([num, letter]) => {
  const pattern = new RegExp(`<h3>${num}\\s+([^<]+)</h3>`, 'g');
  htmlBody = htmlBody.replace(pattern, `<h3 class="ieee-subsec"><em>${letter}. $1</em></h3>`);
});

// Format Sub-subsections: <h4>1. Request Success Rate...</h4> -> <h4 class="ieee-subsubsec"><em>1) Request Success Rate...</em></h4>
htmlBody = htmlBody.replace(/<h4>(\d+)\.\s+([^<]+)<\/h4>/g, '<h4 class="ieee-subsubsec"><em>$1) $2</em></h4>');
htmlBody = htmlBody.replace(/<h4>([^<]+)<\/h4>/g, (match, title) => {
  // If it's a table, leave it for table replacement
  if (title.startsWith('Table ')) return match;
  return `<h4 class="ieee-paragraph-heading"><em>${title}</em></h4>`;
});

// Step 11: Format Tables in IEEE Booktabs Style
const tableTitles = {
  'Table 1:': { label: 'TABLE I', title: 'PRIMARY 360-RUN EXPERIMENTAL BENCHMARK (MEAN &plusmn; STD, MEDIAN [IQR])' },
  'Table 2a:': { label: 'TABLE II-A', title: 'NOMINAL SCENARIO PERFORMANCE BREAKDOWN' },
  'Table 2b:': { label: 'TABLE II-B', title: 'FLASH CROWD SCENARIO PERFORMANCE BREAKDOWN' },
  'Table 2c:': { label: 'TABLE II-C', title: 'SERVER CRASH SCENARIO PERFORMANCE BREAKDOWN' },
  'Table 2d:': { label: 'TABLE II-D', title: 'COMPOUND STRESS SCENARIO PERFORMANCE BREAKDOWN' },
  'Table 3:': { label: 'TABLE III', title: '30-SEED POST-RESTORATION RECOVERY METRICS UNDER DEC-010' },
  'Table 4:': { label: 'TABLE IV', title: 'PRIMARY PAIRED STATISTICAL COMPARISON BATTERY (N = 30 MATCHED SEEDS PER CELL)' },
  'Table 5:': { label: 'TABLE V', title: 'REPRESENTATIVE BALB PARAMETER CONFIGURATIONS UNDER COMPOUND STRESS (n = 3 SEEDS)' },
};

Object.entries(tableTitles).forEach(([key, val]) => {
  // Match across potential KaTeX spans inside h4
  const pattern = new RegExp(`<h4>${key}[\\s\\S]*?</h4>\\s*<table>`, 'g');
  const isDenseTable = (key === 'Table 4:' || key === 'Table 1:');
  const extraClass = isDenseTable ? 'table-dense' : '';
  htmlBody = htmlBody.replace(pattern, `
<div class="table-container table-span-all ${extraClass}">
  <div class="table-label">${val.label}</div>
  <div class="table-title">${val.title}</div>
  <table>
  `);
});
htmlBody = htmlBody.replace(/<\/table>/g, '</table></div>');

// Load KaTeX CSS and patch font URLs with jsdelivr CDN
const katexCssRaw = fs.readFileSync('/tmp/katex_tool/node_modules/katex/dist/katex.min.css', 'utf-8');
const katexCssPatched = katexCssRaw.replace(/fonts\//g, 'https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/fonts/');

// Complete IEEE Transactions HTML Document
const fullHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation</title>
<style>
${katexCssPatched}

/* ==========================================================================
   IEEE TRANSACTIONS & JOURNAL ACADEMIC STYLING
   ========================================================================== */

@page {
  size: letter;
  margin-top: 0.70in;
  margin-bottom: 0.75in;
  margin-left: 0.65in;
  margin-right: 0.65in;
  @top-left {
    font-family: 'Times New Roman', Times, 'Nimbus Roman', serif;
    font-size: 8pt;
    font-style: italic;
    color: #444;
    content: "HARIPRASAD ET AL.: AUTONOMIC CLOUD RESILIENCE THROUGH BROWNOUT-BASED GRACEFUL DEGRADATION";
  }
  @top-right {
    font-family: 'Times New Roman', Times, 'Nimbus Roman', serif;
    font-size: 8pt;
    color: #444;
    content: "NOVEMBER 2026";
  }
  @bottom-center {
    font-family: 'Times New Roman', Times, 'Nimbus Roman', serif;
    font-size: 8.5pt;
    content: counter(page);
  }
}

@page:first {
  @top-left {
    content: none;
  }
  @top-right {
    content: none;
  }
}

*, *:before, *:after {
  box-sizing: border-box;
}

body {
  font-family: 'Times New Roman', Times, 'Nimbus Roman', 'Liberation Serif', serif;
  font-size: 9.5pt;
  line-height: 1.22;
  color: #111;
  background-color: #fff;
  margin: 0;
  padding: 0;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
}

/* Document Header (Spans Full Page Width) */
.paper-header {
  text-align: center;
  margin-bottom: 12pt;
  padding-bottom: 10pt;
  border-bottom: 0.5pt solid #ddd;
}

.paper-title {
  font-size: 19pt;
  font-weight: bold;
  line-height: 1.15;
  margin: 0 0 8pt 0;
  letter-spacing: -0.01em;
}

.paper-authors {
  font-size: 10.5pt;
  margin: 0 0 3pt 0;
  line-height: 1.3;
}

.paper-authors strong {
  font-weight: bold;
}

.paper-affil {
  font-size: 9pt;
  font-style: italic;
  color: #333;
  margin: 0 0 5pt 0;
  line-height: 1.25;
}

.paper-meta-badge {
  font-size: 8pt;
  font-family: 'Courier New', Courier, monospace;
  color: #555;
  background-color: #f7f7f7;
  display: inline-block;
  padding: 2pt 8pt;
  border: 0.5pt solid #ccc;
  border-radius: 2pt;
  margin-top: 2pt;
  margin-bottom: 8pt;
}

/* IEEE Abstract & Keywords Box */
.ieee-abstract-container {
  margin: 8pt 24pt 2pt 24pt;
  text-align: justify;
  text-justify: inter-word;
  font-size: 9pt;
  line-height: 1.25;
}

.ieee-abstract-para {
  margin-top: 0;
  margin-bottom: 5pt;
  text-indent: 0;
}

.ieee-abstract-head {
  font-weight: bold;
  font-style: italic;
}

.ieee-keywords-para {
  margin-top: 4pt;
  margin-bottom: 0;
  text-indent: 0;
}

.ieee-keywords-head {
  font-weight: bold;
  font-style: italic;
}

/* Two-Column Body Layout */
.paper-body {
  column-count: 2;
  column-gap: 0.22in;
  text-align: justify;
  text-justify: inter-word;
}

/* Headings */
h1 { display: none; } /* Handled by .paper-header */

h2.ieee-sec {
  font-size: 10pt;
  font-weight: bold;
  font-variant: small-caps;
  text-align: center;
  letter-spacing: 0.05em;
  margin-top: 11pt;
  margin-bottom: 4pt;
  break-after: avoid;
  border-bottom: none;
}

h3.ieee-subsec {
  font-size: 9.5pt;
  font-weight: bold;
  font-style: italic;
  margin-top: 8pt;
  margin-bottom: 2pt;
  break-after: avoid;
}

h4.ieee-subsubsec {
  font-size: 9pt;
  font-weight: bold;
  font-style: italic;
  margin-top: 6pt;
  margin-bottom: 2pt;
  break-after: avoid;
}

h4.ieee-paragraph-heading {
  font-size: 9pt;
  font-weight: bold;
  font-style: italic;
  margin-top: 6pt;
  margin-bottom: 2pt;
  break-after: avoid;
}

/* Paragraphs & Indentation */
p {
  margin-top: 0;
  margin-bottom: 0;
  text-indent: 1.25em;
}

h2 + p, h3 + p, h4 + p, .no-indent, .figure-caption, .table-title, blockquote p, .ieee-abstract-para, .ieee-keywords-para {
  text-indent: 0;
}

/* Lists */
ul, ol {
  margin-top: 2pt;
  margin-bottom: 3pt;
  padding-left: 1.4em;
}

li {
  margin-bottom: 2pt;
}

/* Inline Code & Architecture Box */
code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 8.5pt;
  background-color: #f5f5f5;
  padding: 0.5pt 2pt;
  border-radius: 1.5pt;
}

.architecture-box {
  background-color: #fafafa;
  border: 0.5pt solid #aaa;
  padding: 6pt;
  margin: 6pt auto;
  max-width: 95%;
  text-align: left;
}

.architecture-pre {
  font-family: 'Courier New', Courier, monospace;
  font-size: 6.8pt;
  line-height: 1.1;
  margin: 0;
  white-space: pre;
}

/* Equations */
.equation-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 3.5pt 0;
  width: 100%;
  break-inside: avoid;
}

.equation-content {
  flex-grow: 1;
  text-align: center;
}

.equation-num {
  font-size: 8.5pt;
  font-family: 'Times New Roman', serif;
  padding-left: 6pt;
  white-space: nowrap;
}

/* Tables (IEEE Booktabs Style) */
.table-container {
  margin: 10pt 0;
  break-inside: avoid;
  text-align: center;
}

.table-span-all {
  column-span: all;
  margin: 8pt auto;
}

.table-label {
  font-size: 8.5pt;
  font-weight: bold;
  font-variant: small-caps;
  letter-spacing: 0.05em;
  margin-bottom: 1pt;
}

.table-title {
  font-size: 8pt;
  font-weight: bold;
  font-variant: small-caps;
  margin-bottom: 4pt;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 7.2pt;
  line-height: 1.15;
  border-top: 1.3pt solid #000;
  border-bottom: 1.3pt solid #000;
  margin: 0 auto;
}

th {
  font-weight: bold;
  font-size: 7.4pt;
  text-align: center;
  padding: 3pt 2pt;
  border-bottom: 0.6pt solid #000;
  background-color: #fafafa;
}

td {
  padding: 2.5pt 2pt;
  text-align: center;
  border-bottom: 0.3pt solid #e5e5e5;
}

tr:last-child td {
  border-bottom: none;
}

/* Dense table styling for 10-13 column benchmark tables */
.table-dense table {
  font-size: 6.7pt;
  line-height: 1.12;
}

.table-dense th {
  padding: 2.5pt 1.5pt;
  font-size: 7.0pt;
}

.table-dense td {
  padding: 2pt 1.5pt;
}

/* Figures */
.figure-container {
  margin: 5pt 0;
  break-inside: avoid;
  text-align: center;
}

.figure-span-all {
  column-span: all;
  margin: 8pt auto;
}

.figure-container img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto 3pt auto;
}

.figure-caption {
  font-size: 8pt;
  line-height: 1.18;
  color: #222;
  text-align: justify;
  margin: 3pt auto 6pt auto;
  max-width: 98%;
}

/* Callouts / Alerts */
blockquote {
  margin: 6pt 0;
  padding: 4pt 7pt;
  background-color: #f8f9fa;
  border-left: 2.5pt solid #2457E8;
  font-size: 8.5pt;
  line-height: 1.2;
  break-inside: avoid;
}

/* Horizontal Dividers */
hr {
  border: none;
  border-top: 0.5pt solid #ccc;
  margin: 8pt 0;
}

/* References Section */
.references-list p, ol li {
  font-size: 8pt;
  line-height: 1.22;
  margin-bottom: 3.5pt;
}

/* Hyperlinks */
a {
  color: #1a4b9c;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

</style>
</head>
<body>

<div class="paper-header">
  <div class="paper-title">Autonomic Cloud Resilience Through Brownout-Based Graceful Degradation: A Simulation-Based Evaluation of Brownout-Aware Load Balancing</div>
  <div class="paper-authors">
    <strong>Hari Prasad L</strong>, <strong>Yeruva Mahesh Reddy</strong>, and <strong>K. Ram Charan</strong>
  </div>
  <div class="paper-affil">
    Department of Computer Science and Engineering and Department of Data Science and AI Engineering, Indian Institute of Information Technology Dharwad, Karnataka 580009, India<br>
    <em>Email: {23bds022, 23bcs136, 23bds029}@iiitdwd.ac.in</em>
  </div>
  <div class="paper-meta-badge">
    Preprint Working Paper &bull; Target: IEEE Transactions on Cloud Computing / ACM TAAS &bull; Date: November 2026
  </div>
  
  <div class="ieee-abstract-container">
    ${renderedAbstractBody}
    ${keywordsHtml}
  </div>
</div>

<div class="paper-body">
${htmlBody}
</div>

</body>
</html>
`;

console.log('Step 6: Writing publication HTML to:', HTML_OUTPUT_PATH);
fs.writeFileSync(HTML_OUTPUT_PATH, fullHtml, 'utf-8');

console.log('Step 7: Compiling PDF via Headless Chrome with Skia/PDF...');
const chromeCmd = [
  'google-chrome',
  '--headless',
  '--disable-gpu',
  '--no-sandbox',
  '--allow-file-access-from-files',
  '--run-all-compositor-stages-before-draw',
  `--print-to-pdf="${PDF_OUTPUT_PATH}"`,
  '--no-pdf-header-footer',
  `"${HTML_OUTPUT_PATH}"`,
].join(' ');

try {
  execSync(chromeCmd, { stdio: 'inherit' });
  console.log('Step 8: PDF compiled successfully at:', PDF_OUTPUT_PATH);
} catch (err) {
  console.error('Error during Chrome PDF compilation:', err.message);
  process.exit(1);
}

// Verification via pdfinfo
console.log('Step 9: Verifying generated PDF metadata...');
try {
  const pdfInfo = execSync(`pdfinfo "${PDF_OUTPUT_PATH}"`, { encoding: 'utf-8' });
  console.log(pdfInfo);
} catch (err) {
  console.warn('pdfinfo check failed:', err.message);
}

console.log('Build pipeline completed successfully!');

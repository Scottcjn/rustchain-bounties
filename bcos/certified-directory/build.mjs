import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const dataPath = join(root, "data", "projects.json");
const outputPath = join(root, "dist", "index.html");

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function validateProject(project, index) {
  const required = ["name", "url", "githubRepo", "category", "bcosTier", "latestAttestedSha", "sbomHash", "reviewNote"];
  const missing = required.filter((key) => !project[key]);
  if (missing.length) {
    throw new Error(`Project entry ${index} is missing required fields: ${missing.join(", ")}`);
  }
  if (!/^L[0-2]$/.test(project.bcosTier)) {
    throw new Error(`Project entry ${index} has invalid bcosTier: ${project.bcosTier}`);
  }
  if (!/^sha256:[a-f0-9]{64}$/i.test(project.sbomHash)) {
    throw new Error(`Project entry ${index} has invalid sbomHash: ${project.sbomHash}`);
  }
}

function tierRank(tier) {
  return Number(tier.replace("L", ""));
}

function renderRows(projects) {
  return projects
    .map(
      (project) => `
        <article class="project-card" data-name="${escapeHtml(project.name.toLowerCase())}" data-category="${escapeHtml(
          project.category.toLowerCase()
        )}" data-tier="${escapeHtml(project.bcosTier)}">
          <div class="card-topline">
            <span class="tier tier-${escapeHtml(project.bcosTier.toLowerCase())}">${escapeHtml(project.bcosTier)}</span>
            <span class="category">${escapeHtml(project.category)}</span>
          </div>
          <h2><a href="${escapeHtml(project.url)}">${escapeHtml(project.name)}</a></h2>
          <dl>
            <div>
              <dt>GitHub</dt>
              <dd><a href="https://github.com/${escapeHtml(project.githubRepo)}">${escapeHtml(project.githubRepo)}</a></dd>
            </div>
            <div>
              <dt>Latest SHA</dt>
              <dd><code>${escapeHtml(project.latestAttestedSha)}</code></dd>
            </div>
            <div>
              <dt>SBOM Hash</dt>
              <dd><code>${escapeHtml(project.sbomHash)}</code></dd>
            </div>
          </dl>
          <p>${escapeHtml(project.reviewNote)}</p>
          <details>
            <summary>Badge embed</summary>
            <pre>[![BCOS ${escapeHtml(project.bcosTier)}](https://50.28.86.131/bcos/badge/${encodeURIComponent(
              project.githubRepo
            )}-${escapeHtml(project.bcosTier)}.svg)](${escapeHtml(project.url)})</pre>
          </details>
        </article>`
    )
    .join("\n");
}

function renderCategoryOptions(projects) {
  const categories = [...new Set(projects.map((project) => project.category))].sort((a, b) => a.localeCompare(b));
  return categories.map((category) => `<option value="${escapeHtml(category.toLowerCase())}">${escapeHtml(category)}</option>`).join("");
}

function renderHtml(projects) {
  const sortedProjects = [...projects].sort((a, b) => tierRank(b.bcosTier) - tierRank(a.bcosTier) || a.name.localeCompare(b.name));
  const generatedAt = new Date().toISOString();
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BCOS Certified Directory</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b0f14;
      --panel: #111923;
      --panel-strong: #172331;
      --text: #eef5f0;
      --muted: #94a8a0;
      --line: #263545;
      --green: #65d685;
      --cyan: #55c7e8;
      --amber: #e6c15c;
      --red: #f17474;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: #0f1720;
      padding: 32px 20px 24px;
    }
    main, .header-inner {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(2rem, 5vw, 3.6rem);
      letter-spacing: 0;
    }
    .lede {
      margin: 0;
      max-width: 760px;
      color: var(--muted);
      font-size: 1.04rem;
    }
    .toolbar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 190px;
      gap: 12px;
      margin: 24px 0;
    }
    input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--text);
      min-height: 44px;
      padding: 10px 12px;
      font: inherit;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0;
    }
    .stat {
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      padding: 16px;
    }
    .stat strong {
      display: block;
      font-size: 1.55rem;
      color: var(--green);
    }
    .stat span {
      color: var(--muted);
      font-size: .88rem;
    }
    .project-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }
    .project-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      padding: 18px;
    }
    .project-card[hidden] { display: none; }
    .card-topline {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      margin-bottom: 12px;
      color: var(--muted);
      font-size: .86rem;
      text-transform: uppercase;
    }
    .tier {
      border: 1px solid currentColor;
      border-radius: 999px;
      padding: 2px 9px;
      font-weight: 700;
    }
    .tier-l2 { color: var(--green); }
    .tier-l1 { color: var(--cyan); }
    .tier-l0 { color: var(--amber); }
    h2 {
      margin: 0 0 14px;
      font-size: 1.25rem;
    }
    a { color: var(--cyan); text-decoration: none; }
    a:hover { text-decoration: underline; }
    dl {
      display: grid;
      gap: 10px;
      margin: 0 0 14px;
    }
    dl div {
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }
    dt {
      color: var(--muted);
      font-size: .78rem;
      text-transform: uppercase;
      margin-bottom: 3px;
    }
    dd { margin: 0; overflow-wrap: anywhere; }
    code, pre {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: .86rem;
    }
    pre {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #0c1218;
      padding: 10px;
    }
    footer {
      color: var(--muted);
      border-top: 1px solid var(--line);
      padding: 18px 0 32px;
      font-size: .9rem;
    }
    @media (max-width: 720px) {
      .toolbar, .stats { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <h1>BCOS Certified Directory</h1>
      <p class="lede">Browse certified RustChain ecosystem projects with trust metadata upfront: tier, repo, latest attested SHA, SBOM hash, and a short review note.</p>
    </div>
  </header>
  <main>
    <section class="toolbar" aria-label="Directory filters">
      <input id="search" type="search" placeholder="Search project, repo, category, SHA, or review note">
      <select id="category">
        <option value="">All categories</option>
        ${renderCategoryOptions(sortedProjects)}
      </select>
    </section>
    <section class="stats" aria-label="Directory summary">
      <div class="stat"><strong>${sortedProjects.length}</strong><span>certified projects</span></div>
      <div class="stat"><strong>${sortedProjects.filter((project) => project.bcosTier === "L2").length}</strong><span>L2 projects</span></div>
      <div class="stat"><strong>${new Set(sortedProjects.map((project) => project.category)).size}</strong><span>categories</span></div>
      <div class="stat"><strong>${generatedAt.slice(0, 10)}</strong><span>generated</span></div>
    </section>
    <section id="projects" class="project-grid">
${renderRows(sortedProjects)}
    </section>
    <footer>
      Add a project by editing <code>data/projects.json</code> and running <code>node build.mjs</code>. Generated at ${escapeHtml(generatedAt)}.
    </footer>
  </main>
  <script>
    const search = document.getElementById("search");
    const category = document.getElementById("category");
    const cards = [...document.querySelectorAll(".project-card")];

    function applyFilters() {
      const query = search.value.trim().toLowerCase();
      const selectedCategory = category.value;
      for (const card of cards) {
        const matchesQuery = !query || card.textContent.toLowerCase().includes(query);
        const matchesCategory = !selectedCategory || card.dataset.category === selectedCategory;
        card.hidden = !(matchesQuery && matchesCategory);
      }
    }

    search.addEventListener("input", applyFilters);
    category.addEventListener("change", applyFilters);
  </script>
</body>
</html>
`;
}

const projects = JSON.parse(await readFile(dataPath, "utf8"));
projects.forEach(validateProject);
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, renderHtml(projects));
console.log(`Wrote ${outputPath}`);

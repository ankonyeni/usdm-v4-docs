const DIAGRAM_STORAGE_PREFIX = "mermaid-diagram-view:";
const mermaidSourceMap = new Map();
let mermaidDiagramCounter = 0;

function nextMermaidDiagramId(prefix = "mermaid-diagram") {
  mermaidDiagramCounter += 1;
  return `${prefix}-${mermaidDiagramCounter}`;
}

function extractDiagramType(source) {
  const firstContentLine = source
    .split(/\r?\n/u)
    .map((line) => line.trim())
    .find((line) => line.length > 0);

  if (!firstContentLine) {
    return "";
  }

  return firstContentLine.split(/\s+/u)[0] || "";
}

function getBaseUrl() {
  if (typeof base_url === "string" && base_url.length > 0) {
    return base_url;
  }

  return ".";
}

function getDiagramStorageCandidates() {
  const storages = [];

  try {
    if (window.localStorage) {
      storages.push(window.localStorage);
    }
  } catch (error) {
    // Ignore storage availability issues.
  }

  try {
    if (window.sessionStorage) {
      storages.push(window.sessionStorage);
    }
  } catch (error) {
    // Ignore storage availability issues.
  }

  return storages;
}

function pruneStoredDiagrams(storage) {
  const expiryCutoff = Date.now() - 24 * 60 * 60 * 1000;
  const staleKeys = [];

  for (let index = 0; index < storage.length; index += 1) {
    const key = storage.key(index);

    if (!key || !key.startsWith(DIAGRAM_STORAGE_PREFIX)) {
      continue;
    }

    try {
      const rawValue = storage.getItem(key);
      const payload = rawValue ? JSON.parse(rawValue) : null;

      if (!payload || typeof payload.storedAt !== "number" || payload.storedAt < expiryCutoff) {
        staleKeys.push(key);
      }
    } catch (error) {
      staleKeys.push(key);
    }
  }

  for (const key of staleKeys) {
    storage.removeItem(key);
  }
}

function storeDiagramPayload(payload) {
  const storageKey = `${DIAGRAM_STORAGE_PREFIX}${Date.now().toString(36)}-${Math.random()
    .toString(36)
    .slice(2, 8)}`;
  const serializedPayload = JSON.stringify({
    ...payload,
    storedAt: Date.now(),
  });

  for (const storage of getDiagramStorageCandidates()) {
    try {
      pruneStoredDiagrams(storage);
      storage.setItem(storageKey, serializedPayload);
      return storageKey;
    } catch (error) {
      // Try the next storage backend.
    }
  }

  return null;
}

function writeWindowNameDiagramPayload(payload) {
  try {
    window.name = JSON.stringify({
      type: "mermaid-diagram-view",
      payload,
    });
    return true;
  } catch (error) {
    return false;
  }
}

function readWindowNameDiagramPayload() {
  if (typeof window.name !== "string" || window.name.length === 0) {
    return null;
  }

  try {
    const parsed = JSON.parse(window.name);

    if (parsed && parsed.type === "mermaid-diagram-view" && parsed.payload) {
      window.name = "";
      return parsed.payload;
    }
  } catch (error) {
    // Ignore non-JSON window names.
  }

  return null;
}

function readStoredDiagramPayload(storageKey) {
  if (!storageKey) {
    return null;
  }

  for (const storage of getDiagramStorageCandidates()) {
    try {
      const rawValue = storage.getItem(storageKey);

      if (!rawValue) {
        continue;
      }

      const payload = JSON.parse(rawValue);

      if (payload && typeof payload.source === "string" && payload.source.trim().length > 0) {
        return payload;
      }
    } catch (error) {
      // Continue checking other storage backends.
    }
  }

  return null;
}

function readViewerDiagramPayload() {
  const windowPayload = readWindowNameDiagramPayload();

  if (windowPayload) {
    return windowPayload;
  }

  const viewerUrl = new URL(window.location.href);
  const storageKey = viewerUrl.searchParams.get("diagram");

  if (storageKey) {
    const storedPayload = readStoredDiagramPayload(storageKey);

    if (storedPayload) {
      return storedPayload;
    }
  }

  const source = viewerUrl.searchParams.get("source");

  if (!source) {
    return null;
  }

  return {
    source,
    title: viewerUrl.searchParams.get("title") || "",
  };
}

function getCurrentDiagramTitle() {
  const heading = document.querySelector("h1");

  if (heading && heading.textContent) {
    return heading.textContent.trim();
  }

  return document.title.replace(/\s*-\s*USDM v4\s*$/u, "").trim();
}

function getViewerUrl(storageKey) {
  const viewerUrl = new URL(`${getBaseUrl()}/diagram-viewer/`, window.location.href);

  if (storageKey) {
    viewerUrl.searchParams.set("diagram", storageKey);
  }

  return viewerUrl.toString();
}

function openDiagramViewer(diagramId) {
  const source = mermaidSourceMap.get(diagramId);
  const container = document.getElementById(diagramId);

  if (!source) {
    return;
  }

  const title = getCurrentDiagramTitle();
  const svgMarkup = container ? container.innerHTML.trim() : "";
  const payload = {
    source,
    svg: svgMarkup || null,
    title,
    diagramType: extractDiagramType(source),
    sourcePage: window.location.href,
  };
  const storageKey = storeDiagramPayload(payload);

  writeWindowNameDiagramPayload(payload);

  window.location.assign(getViewerUrl(storageKey));
}

function upgradeMermaidBlocks() {
  const blocks = document.querySelectorAll("pre code.language-mermaid");

  for (const codeBlock of blocks) {
    const preBlock = codeBlock.parentElement;

    if (!preBlock || preBlock.dataset.mermaidProcessed === "true") {
      continue;
    }

    const source = codeBlock.textContent.trim();
    preBlock.dataset.mermaidProcessed = "true";

    // LinkML can emit a top-level schema diagram fence containing only "None".
    if (!source || source === "None") {
      continue;
    }

    const diagramId = nextMermaidDiagramId();
    const diagramType = extractDiagramType(source);
    const figure = document.createElement("figure");
    const container = document.createElement("div");

    figure.className = "mermaid-figure";
    if (diagramType === "erDiagram") {
      figure.dataset.diagramViewer = "er";
    }

    container.className = "mermaid";
    container.id = diagramId;
    container.dataset.diagramId = diagramId;
    container.dataset.diagramType = diagramType;
    container.textContent = source;

    mermaidSourceMap.set(diagramId, source);

    figure.append(container);
    preBlock.replaceWith(figure);
  }
}

const mermaidTheme = {
  startOnLoad: false,
  securityLevel: "loose",
  theme: "base",
  darkMode: true,
  fontFamily: "Aptos, Segoe UI, Trebuchet MS, sans-serif",
  themeCSS: `
    .erDiagram .row-rect-odd path[fill]:not([fill="none"]) {
      fill: #1d2734 !important;
    }

    .erDiagram .row-rect-even path[fill]:not([fill="none"]) {
      fill: #18212d !important;
    }

    .erDiagram .label,
    .erDiagram .label span,
    .erDiagram .label p,
    .erDiagram .nodeLabel,
    .erDiagram .nodeLabel span,
    .erDiagram .nodeLabel p {
      color: #e7e0d5 !important;
      fill: #e7e0d5 !important;
    }
  `,
  themeVariables: {
    background: "#101720",
    primaryColor: "#1c2733",
    primaryTextColor: "#f8f1e7",
    primaryBorderColor: "#c7a46a",
    secondaryColor: "#18212d",
    secondaryTextColor: "#e7e0d5",
    secondaryBorderColor: "#86a7c1",
    tertiaryColor: "#15202b",
    tertiaryTextColor: "#e7e0d5",
    tertiaryBorderColor: "#6f8ba0",
    lineColor: "#c7a46a",
    textColor: "#e7e0d5",
    mainBkg: "#1c2733",
    secondBkg: "#18212d",
    tertiaryBkg: "#15202b",
    clusterBkg: "#131b25",
    clusterBorder: "#86a7c1",
    edgeLabelBackground: "#101720",
    nodeBorder: "#c7a46a",
    actorBorder: "#c7a46a",
    actorBkg: "#1c2733",
    actorTextColor: "#f8f1e7",
    labelBoxBkgColor: "#101720",
    labelBoxBorderColor: "#c7a46a",
    labelTextColor: "#f8f1e7",
    loopTextColor: "#f8f1e7",
    noteBkgColor: "#243243",
    noteBorderColor: "#86a7c1",
    noteTextColor: "#e7e0d5",
    activationBorderColor: "#c7a46a",
    activationBkgColor: "#203448",
    sequenceNumberColor: "#101720",
    sectionBkgColor: "#18212d",
    sectionBkgColor2: "#1c2733",
    sectionBorderColor: "#86a7c1",
    sectionTitleColor: "#f8f1e7",
    cScale0: "#18212d",
    cScale1: "#1c2733",
    cScale2: "#243243",
    cScale3: "#2d3d50",
    cScale4: "#384b61",
    cScale5: "#465b74",
    cScale6: "#56708b",
    cScale7: "#68849e",
  },
  flowchart: {
    curve: "linear",
    useMaxWidth: true,
  },
  er: {
    useMaxWidth: true,
  },
};

async function renderMermaid() {
  if (typeof mermaid === "undefined") {
    return;
  }

  upgradeMermaidBlocks();
  mermaid.initialize(mermaidTheme);
  await mermaid.run({
    querySelector: ".mermaid",
  });
  enhanceERDiagramViewers();
}

async function renderMermaidSource(targetElement, source, options = {}) {
  if (typeof mermaid === "undefined" || !targetElement || !source || source.trim().length === 0) {
    return null;
  }

  const diagramId = options.id || nextMermaidDiagramId(options.idPrefix || "mermaid-render");
  const diagramType = extractDiagramType(source);

  targetElement.id = diagramId;
  targetElement.classList.add("mermaid-render-surface");
  targetElement.dataset.diagramId = diagramId;
  targetElement.dataset.diagramType = diagramType;
  targetElement.textContent = source;

  mermaidSourceMap.set(diagramId, source);
  mermaid.initialize(mermaidTheme);

  const { svg } = await mermaid.render(`${diagramId}-svg`, source);
  targetElement.innerHTML = svg;

  return targetElement.querySelector("svg");
}

function enhanceERDiagramViewers() {
  const figures = document.querySelectorAll('.mermaid-figure[data-diagram-viewer="er"]');

  for (const figure of figures) {
    if (figure.dataset.viewerEnhanced === "true") {
      continue;
    }

    const container = figure.querySelector(".mermaid");

    if (!container || !mermaidSourceMap.has(container.id)) {
      continue;
    }

    figure.dataset.viewerEnhanced = "true";
    figure.classList.add("mermaid-figure--openable");
    container.classList.add("mermaid--openable");
    container.tabIndex = 0;
    container.setAttribute("role", "link");
    container.setAttribute("aria-label", "Open this entity relationship diagram in the full-screen viewer");

    const viewerLink = document.createElement("button");
    viewerLink.type = "button";
    viewerLink.className = "mermaid-viewer-link";
    viewerLink.textContent = "Open full-screen viewer";

    viewerLink.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      openDiagramViewer(container.id);
    });

    container.addEventListener("click", (event) => {
      if (event.defaultPrevented) {
        return;
      }

      const target = event.target;

      if (target instanceof Element && target.closest("a")) {
        return;
      }

      openDiagramViewer(container.id);
    });

    container.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }

      event.preventDefault();
      openDiagramViewer(container.id);
    });

    figure.append(viewerLink);
  }
}

window.MermaidDocs = {
  extractDiagramType,
  openDiagramViewer,
  readViewerDiagramPayload,
  renderMermaidSource,
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    renderMermaid();
  });
} else {
  renderMermaid();
}

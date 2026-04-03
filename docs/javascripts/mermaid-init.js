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

    const container = document.createElement("div");
    container.className = "mermaid";
    container.textContent = source;

    preBlock.replaceWith(container);
  }
}

const mermaidTheme = {
  startOnLoad: false,
  securityLevel: "loose",
  theme: "base",
  darkMode: true,
  fontFamily: "Aptos, Segoe UI, Trebuchet MS, sans-serif",
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
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    renderMermaid();
  });
} else {
  renderMermaid();
}

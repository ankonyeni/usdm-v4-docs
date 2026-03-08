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

async function renderMermaid() {
  if (typeof mermaid === "undefined") {
    return;
  }

  upgradeMermaidBlocks();
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: "default",
  });
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

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "usdm_v4.linkml.yaml"
DOCS_PATH = REPO_ROOT / "docs"
EXAMPLES_PATH = REPO_ROOT / "examples"
SITE_PATH = REPO_ROOT / "site"
TYPE_DOCS_PATH = DOCS_PATH / "types"
TEMPLATE_PATH = REPO_ROOT / "templates" / "docgen"
TYPE_HEADER_PATTERN = re.compile(r"^# Type:\s+(\S+)\s*$")
GENERATED_DOC_PATHS = (
    "index.md",
    "classes",
    "slots",
    "types",
    "schemas",
    "enums",
    "subsets",
    "reference",
)


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=REPO_ROOT)


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def clean_generated_docs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for relative_path in GENERATED_DOC_PATHS:
        target = path / relative_path
        if not target.exists():
            continue
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()


def add_type_doc_aliases(path: Path) -> None:
    if not path.exists():
        return

    for type_doc in sorted(path.glob("*.md")):
        with type_doc.open(encoding="utf-8") as handle:
            header_line = handle.readline().strip()

        match = TYPE_HEADER_PATTERN.match(header_line)
        if not match:
            continue

        alias_name = f"{match.group(1)}.md"
        if alias_name == type_doc.name:
            continue

        alias_path = path / alias_name
        if not alias_path.exists():
            shutil.copyfile(type_doc, alias_path)


def build_docs(
    schema_path: Path = SCHEMA_PATH,
    docs_path: Path = DOCS_PATH,
    examples_path: Path = EXAMPLES_PATH,
    site_path: Path = SITE_PATH,
) -> None:
    schema_path = resolve_path(schema_path)
    docs_path = resolve_path(docs_path)
    examples_path = resolve_path(examples_path)
    site_path = resolve_path(site_path)
    type_docs_path = docs_path / "types"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    clean_generated_docs(docs_path)

    gen_doc_args = [
        "gen-doc",
        str(schema_path),
        "-d",
        str(docs_path),
        "--preserve-names",
        "--diagram-type",
        "mermaid_class_diagram",
        "--subfolder-type-separation",
        "--truncate-descriptions",
        "false",
    ]

    if TEMPLATE_PATH.exists():
        gen_doc_args.extend(["--template-directory", str(TEMPLATE_PATH)])

    if examples_path.exists() and any(examples_path.glob("*.yaml")):
        gen_doc_args.extend(["--example-directory", str(examples_path)])

    print("Running gen-doc...")
    run(gen_doc_args)

    add_type_doc_aliases(type_docs_path)

    print("Running mkdocs build...")
    run(["mkdocs", "build", "--clean", "--strict", "--site-dir", str(site_path)])


def main() -> int:
    build_docs()

    print("Documentation generation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

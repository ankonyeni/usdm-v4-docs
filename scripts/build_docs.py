from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from sdtm_mappings import inject_class_page_sdtm_sections, write_sdtm_mapping_docs


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "usdm_v4.linkml.yaml"
DOCS_PATH = REPO_ROOT / "docs"
EXAMPLES_PATH = REPO_ROOT / "examples"
SITE_PATH = REPO_ROOT / "site"
SDTM_MAPPING_WORKBOOK = REPO_ROOT / "mappings" / "sdtm_mapping.xlsx"
TYPE_DOCS_PATH = DOCS_PATH / "types"
TEMPLATE_PATH = REPO_ROOT / "templates" / "docgen"
TYPE_HEADER_PATTERN = re.compile(r"^# Type:\s+(\S+)\s*$")
EXAMPLE_HEADING_PATTERN = re.compile(r"^### Example:\s+(.+?)\s*$")
GENERATED_TODO_COMMENT_PATTERN = re.compile(
    r"<!-- TODO: investigate https://stackoverflow\.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->\n?",
    re.MULTILINE,
)
GENERATED_DOC_PATHS = (
    "index.md",
    "classes",
    "slots",
    "types",
    "schemas",
    "enums",
    "subsets",
    "reference",
    "sdtm-mappings.md",
    "sdtm-mappings",
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


def natural_sort_key(value: str) -> list[int | str]:
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def reorder_example_sections_in_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        output.append(line)
        index += 1

        if line.strip() != "## Examples":
            continue

        leading_lines: list[str] = []
        while index < len(lines):
            next_line = lines[index]
            if next_line.startswith("## "):
                break
            if EXAMPLE_HEADING_PATTERN.match(next_line):
                break
            leading_lines.append(next_line)
            index += 1

        example_sections: list[tuple[str, list[str]]] = []
        while index < len(lines):
            heading_line = lines[index]
            match = EXAMPLE_HEADING_PATTERN.match(heading_line)
            if not match:
                break

            section_lines = [heading_line]
            index += 1
            while index < len(lines):
                next_line = lines[index]
                if next_line.startswith("## ") or EXAMPLE_HEADING_PATTERN.match(next_line):
                    break
                section_lines.append(next_line)
                index += 1

            example_sections.append((match.group(1), section_lines))

        output.extend(leading_lines)
        for _, section_lines in sorted(example_sections, key=lambda item: natural_sort_key(item[0])):
            output.extend(section_lines)

    return "".join(output)


def reorder_generated_examples(path: Path) -> None:
    classes_path = path / "classes"
    if not classes_path.exists():
        return

    for class_doc in sorted(classes_path.glob("*.md")):
        original_text = class_doc.read_text(encoding="utf-8")
        updated_text = reorder_example_sections_in_text(original_text)
        if updated_text != original_text:
            class_doc.write_text(updated_text, encoding="utf-8")


def strip_generated_todo_comments(path: Path) -> None:
    classes_path = path / "classes"
    if not classes_path.exists():
        return

    for class_doc in sorted(classes_path.glob("*.md")):
        original_text = class_doc.read_text(encoding="utf-8")
        updated_text = GENERATED_TODO_COMMENT_PATTERN.sub("", original_text)
        if updated_text != original_text:
            class_doc.write_text(updated_text, encoding="utf-8")


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
        "er_diagram",
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
    reorder_generated_examples(docs_path)
    strip_generated_todo_comments(docs_path)
    sdtm_records = write_sdtm_mapping_docs(SDTM_MAPPING_WORKBOOK, docs_path)
    inject_class_page_sdtm_sections(schema_path, docs_path, sdtm_records)

    print("Running mkdocs build...")
    run(["mkdocs", "build", "--clean", "--strict", "--site-dir", str(site_path)])


def main() -> int:
    build_docs()

    print("Documentation generation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_docs import build_docs as generate_docs
from transform import DEFAULT_MAPPING, convert_ddf_ra_to_linkml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO_ROOT / "schemas" / "usdm_v4.linkml.yaml"
DEFAULT_EXAMPLES = REPO_ROOT / "examples"
DEFAULT_REFERENCE_DOCS = REPO_ROOT / "docs"
DEFAULT_SITE = REPO_ROOT / "site"
DEFAULT_SOURCE_MODEL = REPO_ROOT / "upstream" / "cdisc-ddf-ra" / "v4.0.0" / "Deliverables" / "UML" / "dataStructure.yml"
UPSTREAM_LOCK = REPO_ROOT / "upstream" / "cdisc-ddf-ra" / "v4.0.0" / "source-lock.json"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _resolve_cli_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def check_upstream() -> int:
    if not UPSTREAM_LOCK.exists():
        print(f"Missing upstream lock file: {_display_path(UPSTREAM_LOCK)}")
        return 1

    lock = json.loads(UPSTREAM_LOCK.read_text(encoding="utf-8"))
    missing: list[str] = []
    mismatched: list[tuple[str, str, str]] = []

    for file_entry in lock["files"]:
        relative_path = file_entry["path"]
        path = REPO_ROOT / relative_path
        if not path.exists():
            missing.append(relative_path)
            continue

        actual_hash = _sha256(path)
        expected_hash = file_entry["sha256"]
        if actual_hash != expected_hash:
            mismatched.append((relative_path, expected_hash, actual_hash))

    if missing:
        print("Missing pinned upstream inputs:")
        for path in missing:
            print(f"  - {path}")

    if mismatched:
        print("Pinned upstream inputs with hash mismatches:")
        for path, expected_hash, actual_hash in mismatched:
            print(f"  - {path}")
            print(f"    expected: {expected_hash}")
            print(f"    actual:   {actual_hash}")

    if missing or mismatched:
        print("Restore the vendored files to the locked versions before conversion.")
        return 1

    print("Pinned upstream files are present and match source-lock.json.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="cli.py")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_docs_parser = subparsers.add_parser(
        "build-docs",
        help="Generate LinkML reference pages and build the MkDocs site.",
    )
    build_docs_parser.add_argument(
        "--schema",
        default=_display_path(DEFAULT_SCHEMA),
        help="Path to the LinkML schema file.",
    )
    build_docs_parser.add_argument(
        "--examples",
        default=_display_path(DEFAULT_EXAMPLES),
        help="Path to the examples directory.",
    )
    build_docs_parser.add_argument(
        "--docs-dir",
        default=_display_path(DEFAULT_REFERENCE_DOCS),
        help="Directory where generated reference pages are written.",
    )
    build_docs_parser.add_argument(
        "--site-dir",
        default=_display_path(DEFAULT_SITE),
        help="Directory where the static site is built.",
    )

    subparsers.add_parser(
        "check-upstream",
        help="Verify that the pinned upstream DDF-RA inputs are present.",
    )

    import_parser = subparsers.add_parser(
        "import-schema",
        help="Convert the vendored DDF-RA model into a first-pass LinkML schema.",
    )
    import_parser.add_argument(
        "--source",
        default=_display_path(DEFAULT_SOURCE_MODEL),
        help="Path to the vendored DDF-RA source model.",
    )
    import_parser.add_argument(
        "--mapping",
        default=str(DEFAULT_MAPPING),
        help="Path to the importer mapping YAML file.",
    )
    import_parser.add_argument(
        "--output",
        default=_display_path(DEFAULT_SCHEMA),
        help="Path to the LinkML schema file to generate.",
    )

    args = parser.parse_args()

    if args.command == "build-docs":
        generate_docs(
            schema_path=_resolve_cli_path(args.schema),
            docs_path=_resolve_cli_path(args.docs_dir),
            examples_path=_resolve_cli_path(args.examples),
            site_path=_resolve_cli_path(args.site_dir),
        )
        return 0

    if args.command == "check-upstream":
        return check_upstream()

    if args.command == "import-schema":
        convert_ddf_ra_to_linkml(
            source=_resolve_cli_path(args.source),
            output=_resolve_cli_path(args.output),
            mapping_path=_resolve_cli_path(args.mapping),
        )
        print(f"Generated LinkML schema at {args.output}")
        return 0

    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

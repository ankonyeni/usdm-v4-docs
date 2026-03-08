# USDM v4 LinkML Docs

This repository contains a derivative LinkML representation of the CDISC USDM v4 model and the tooling used to generate browsable documentation for it.

The project workflow is:

- vendor a pinned upstream copy of the USDM v4 source model from `cdisc-org/DDF-RA`
- convert `Deliverables/UML/dataStructure.yml` into LinkML
- generate reference documentation with `gen-doc`
- build a static documentation site with MkDocs
- include hand-authored per-class examples inline in the generated class pages

This is an independent derivative documentation project. It is not an official CDISC repository.

## Repository Structure

```text
.github/                  GitHub Actions workflows
docs/                     MkDocs source assets and generated reference markdown
examples/                 Inline YAML examples matched by class name
mappings/                 Importer mapping rules
requirements.txt          Runtime dependencies for local and CI use
requirements-dev.txt      Optional development dependencies
schemas/                  Generated LinkML schema files
scripts/                  Importer, build, and helper scripts
templates/docgen/         Custom LinkML docgen templates
upstream/                 Pinned vendored upstream DDF-RA source files
mkdocs.yml                MkDocs configuration
```

## Source Model

The importer reads this pinned upstream file:

```text
upstream/cdisc-ddf-ra/v4.0.0/Deliverables/UML/dataStructure.yml
```

The upstream copy is treated as source input. Do not edit it in place. Any conversion logic belongs in:

- `mappings/usdm_v4.mapping.yaml`
- `scripts/transform.py`

## Main Outputs

- `schemas/usdm_v4.linkml.yaml`: generated LinkML schema
- `docs/`: generated markdown reference pages and MkDocs assets
- `site/`: built MkDocs site output

## Local Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Common Commands

Verify the vendored upstream source:

```powershell
python .\scripts\cli.py check-upstream
```

Generate the LinkML schema:

```powershell
python .\scripts\cli.py import-schema
```

Build the reference docs and MkDocs site:

```powershell
python .\scripts\build_docs.py
```

## Example Files

Inline examples live in `examples/` and are pulled into the generated class documentation through `gen-doc --example-directory`.

Use this naming convention:

```text
ClassName-001.yaml
ClassName-002.yaml
```

Examples:

- `examples/Abbreviation-001.yaml`
- `examples/Study-001.yaml`

The filename prefix before the first `-` must exactly match the LinkML class name.

## Documentation Build Notes

The docs build uses:

- `gen-doc --preserve-names`
- `--subfolder-type-separation`
- `--truncate-descriptions false`
- Mermaid class diagrams
- custom templates from `templates/docgen/`

The generated reference docs are written to `docs/`, and the site is built into `site/`.

## Project Intent

USDM v4 is large and difficult to navigate from the upstream UML assets alone. This repository exists to make the model easier to learn by providing:

- a LinkML form of the model
- generated per-class documentation
- inline examples for concrete classes
- a publishable static documentation site

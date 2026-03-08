# USDM v4 LinkML Docs

This repository contains a derivative LinkML representation of the CDISC USDM v4 model and the source materials used to publish the documentation site.

Documentation site:

- https://ankonyeni.github.io/usdm-v4-docs/

This repository is primarily a publication source repository. It is intended to preserve:

- the pinned upstream USDM v4 source model used as input
- the derived LinkML schema
- the mapping and scripts used to regenerate the published documentation
- the GitHub Actions workflow that publishes the site to GitHub Pages

It is not an official CDISC repository.

## License

Unless otherwise noted, the original work in this repository is made available under the MIT License. Vendored and derived third-party material, including the DDF-RA source content under `upstream/`, remains subject to its original licensing and attribution requirements.

## Attribution

This repository is based in part on content from `cdisc-org/DDF-RA`.

Attribution statement:

- Content based on DDF-RA (GitHub) used under the CC-BY-4.0 license.

See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for third-party licensing and attribution details.

## Repository Purpose

USDM v4 is a large and structurally complex model, and the upstream materials can be difficult to navigate on their own. The model is distributed across the source `dataStructure.yml`, large UML artifacts, and supporting documentation, which makes it harder to follow class relationships, understand the overall structure, and find concrete examples quickly.

This repository exists to make the model easier to explore by bringing together:

- the pinned upstream `dataStructure.yml` source model
- a derived LinkML representation of the model
- generated class-level documentation for the model
- inline examples for concrete classes

## Main Contents

- `upstream/`: pinned upstream USDM v4 source inputs
- `schemas/usdm_v4.linkml.yaml`: derived LinkML schema
- `mappings/usdm_v4.mapping.yaml`: mapping rules used by the importer
- `examples/`: example YAML instances used in the published documentation
- `scripts/`: scripts used to regenerate the schema and documentation
- `.github/workflows/docs.yml`: GitHub Pages publishing workflow

## Maintenance

This repository is not meant to be under constant active development. It should change only when one of the following changes:

- the LinkML conversion logic or mapping
- the published examples
- the GitHub Pages build or publishing workflow

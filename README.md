# USDM v4

This repository publishes a browsable documentation site for a derivative LinkML representation of CDISC USDM v4.

It includes:

- generated class, slot, type, and schema docs
- example YAML instances
- SDTM trial domain mapping pages
- the source files and scripts used to rebuild the site

Documentation site:

- https://ankonyeni.github.io/usdm-v4-docs/

This is not an official CDISC repository.

## Key Paths

- `upstream/`: pinned upstream source inputs
- `schemas/usdm_v4.linkml.yaml`: derived LinkML schema
- `mappings/usdm_v4.mapping.yaml`: importer mapping rules
- `mappings/sdtm_mapping.xlsx`: SDTM trial domain mapping workbook
- `examples/`: example instances used in the docs
- `scripts/`: schema and docs build scripts
- `docs/`: generated documentation source for MkDocs

## Rebuild Docs

Run:

```bash
python scripts/build_docs.py
```

## License and Attribution

Unless noted otherwise, original repository content is available under the MIT License.

This repository includes material derived from `cdisc-org/DDF-RA`. Third-party content remains subject to its original license and attribution requirements. See [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

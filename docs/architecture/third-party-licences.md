---
type: Reference
title: Third-party licences
description: "Licences of the Python dependencies and Docker image packages kb-tools uses, and why they are compatible with kb-tools' MIT licence."
tags: [licence, dependencies, docker, public-release]
status: draft
generated:
  by: paperclip/kb-tools-developer
  at: 2026-11-13T06:03:34Z
---

# Third-party licences

kb-tools itself is MIT-licensed ([LICENSE](../../LICENSE),
[ADR 0006](decisions/0006-mit-license-template-ships-none.md)). It does not copy third-party
code into the repository: Python dependencies are installed by pip, and system packages are
installed into the Docker image from Debian. Each keeps its own licence.

Licences below are as declared by each package's metadata. A new dependency or image package
adds a row here in the same pull request ([Security](../process/security.md)).

## Python dependencies

| Package | Used by | Licence |
| --- | --- | --- |
| PyYAML | every install | MIT |
| markitdown (with its pdf, docx, pptx, xlsx and xls extras) | `[extract]` | MIT |
| python-pptx | `[extract]` | MIT |
| openpyxl | `[extract]` | MIT |
| pypdfium2 (bundles PDFium) | `[extract]` | Apache-2.0 or BSD-3-Clause; PDFium BSD-3-Clause and its dependencies' licences |
| Pillow | `[extract]` | MIT-CMU (HPND) |
| mcp | `[server]` | MIT |
| langextract | `[facts]` (optional) | Apache-2.0 |
| pytest, python-docx | `[dev]` (tests only) | MIT |
| hatchling | build only | MIT |

markitdown's extras pull in further packages (for example pdfminer.six, mammoth, pandas,
xlrd); these are under permissive licences (MIT, BSD, Apache-2.0). Run
`pip-licenses` in a full install for the complete list.

## Docker image

The image is based on `python:3.12-slim-bookworm` (Debian 12 and CPython, PSF licence) and
adds these Debian packages:

| Package | Licence |
| --- | --- |
| LibreOffice (impress, writer, calc, draw) | MPL-2.0 |
| fonts-dejavu | Bitstream Vera / DejaVu licence (free) |
| fonts-liberation, fonts-liberation2 | SIL OFL 1.1 |
| fonts-crosextra-carlito | SIL OFL 1.1 |
| fonts-crosextra-caladea | Apache-2.0 |
| fonts-noto-core, fonts-noto-cjk | SIL OFL 1.1 |
| fontconfig | MIT-style (HPND) |
| ca-certificates | MPL-2.0 (certificate data), GPL-2.0+ (scripts) |
| tini | MIT |
| git, make (`dev` stage only) | GPL-2.0, GPL-3.0 |

Each package's full copyright file is in the image under `/usr/share/doc/<package>/copyright`.

## Compatibility

- All Python dependencies are permissive, so kb-tools can be MIT-licensed and installed with
  them.
- kb-tools runs LibreOffice as a separate program (`soffice` in headless mode) and does not
  link to or modify it. MPL-2.0 is file-level copyleft: it applies only to changes to
  LibreOffice's own files, so it places no conditions on kb-tools' code.
- The GPL tools in the `dev` stage are only run as programs, never linked.
- Whoever redistributes the Docker image redistributes these packages and must keep their
  licence notices, which the image already contains under `/usr/share/doc`.

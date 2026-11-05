"""Build an extraction package for a source file.

extracted/<slug>/
  manifest.json      provenance: source hash, tool versions, options, counts, warnings
  text.md            MarkItDown conversion of the whole file (navigation and search)
  pages.md           one section per page or slide: text from the rendered PDF + render link
  slides.md/.json    PowerPoint only: per-slide text, tables, pictures (with positions), charts, notes
  workbook.json      Excel only: every non-empty cell with formula, cached value, number format
  sheets/*.csv       Excel only: cached values per sheet
  renders/page-NNN.png  every page or slide, for visual review
  media/             embedded images (candidate key graphics)
  rendered.pdf       Office files only: the LibreOffice PDF used for renders
  review.md          reconciliation checklist to fill in during visual review
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import tempfile
import zipfile
from importlib import metadata
from pathlib import Path

from . import __version__, ingest_log
from .common import Repo, atomic_write, now_iso, sha256, source_slug

OFFICE = {".pptx", ".ppt", ".pps", ".ppsx", ".odp", ".key", ".docx", ".doc", ".odt", ".rtf", ".xlsx", ".xlsm", ".xls", ".ods"}
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff", ".bmp"}
EMU_PER_INCH = 914400


# ---------------------------------------------------------------- helpers

def _versions() -> dict[str, str]:
    versions = {"kb-tools": __version__, "python": platform.python_version()}
    for package in ("markitdown", "python-pptx", "openpyxl", "pypdfium2", "Pillow"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = "missing"
    versions["libreoffice"] = _libreoffice_version() or "missing"
    return versions


def _soffice() -> str | None:
    return shutil.which("soffice") or shutil.which("libreoffice")


def _libreoffice_version() -> str | None:
    binary = _soffice()
    if not binary:
        return None
    try:
        out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=60)
        return out.stdout.strip() or None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _md_cell(value) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", "<br>")


def _md_table(rows: list[list]) -> str:
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [list(r) + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(_md_cell(c) for c in rows[0]) + " |", "|" + " --- |" * width]
    lines += ["| " + " | ".join(_md_cell(c) for c in r) + " |" for r in rows[1:]]
    return "\n".join(lines)


# ---------------------------------------------------------------- steps

def markitdown_text(source: Path) -> str:
    from markitdown import MarkItDown

    converter = MarkItDown(enable_plugins=False)
    convert = getattr(converter, "convert_local", None) or converter.convert
    result = convert(str(source))
    text = getattr(result, "text_content", None) or getattr(result, "markdown", None)
    if text is None:
        raise RuntimeError("MarkItDown returned no content")
    return str(text)


def office_to_pdf(source: Path, out_dir: Path, timeout: int = 600) -> Path:
    binary = _soffice()
    if not binary:
        raise RuntimeError("LibreOffice (soffice) is not installed; cannot render Office files")
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="kb-lo-") as profile, tempfile.TemporaryDirectory(prefix="kb-conv-") as tmp:
        command = [
            binary, "--headless", "--norestore", "--nolockcheck", "--nodefault",
            f"-env:UserInstallation=file://{profile}",
            "--convert-to", "pdf", "--outdir", tmp, str(source),
        ]
        run = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        produced = list(Path(tmp).glob("*.pdf"))
        if run.returncode != 0 or not produced:
            raise RuntimeError(f"LibreOffice conversion failed: {run.stderr.strip() or run.stdout.strip()}")
        target = out_dir / "rendered.pdf"
        shutil.move(str(produced[0]), target)
    return target


def render_pdf(pdf: Path, renders: Path, dpi: int) -> tuple[int, list[str]]:
    """Render every page to PNG and return (page count, per-page text)."""
    import pypdfium2 as pdfium

    renders.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf))
    texts = []
    try:
        for index in range(len(document)):
            page = document[index]
            image = page.render(scale=dpi / 72).to_pil()
            image.save(renders / f"page-{index + 1:03d}.png", optimize=True)
            textpage = page.get_textpage()
            texts.append(textpage.get_text_range().replace("\r\n", "\n").replace("\r", "\n").strip())
            textpage.close()
            page.close()
    finally:
        document.close()
    return len(texts), texts


def render_image(source: Path, renders: Path) -> int:
    from PIL import Image

    renders.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.convert("RGB").save(renders / "page-001.png", optimize=True)
    return 1


def zip_media(source: Path, media: Path) -> list[str]:
    """Copy embedded media out of OOXML containers (docx/xlsx/pptx)."""
    saved = []
    try:
        with zipfile.ZipFile(source) as archive:
            for name in archive.namelist():
                if "/media/" in name and not name.endswith("/"):
                    target = media / Path(name).name
                    media.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(name))
                    saved.append(target.name)
    except zipfile.BadZipFile:
        pass
    return saved


def docx_warnings(source: Path) -> list[str]:
    warnings = []
    try:
        with zipfile.ZipFile(source) as archive:
            names = set(archive.namelist())
            body = archive.read("word/document.xml").decode("utf-8", "ignore") if "word/document.xml" in names else ""
    except (zipfile.BadZipFile, KeyError):
        return warnings
    if "<w:ins " in body or "<w:del " in body:
        warnings.append("Tracked changes present: decide between markup and accepted views; text.md may mix them.")
    if "word/comments.xml" in names:
        warnings.append("Comments present: review them separately; they are not document assertions.")
    if any(n.startswith("word/header") or n.startswith("word/footer") for n in names):
        warnings.append("Headers/footers present: check renders; text extraction may omit or interleave them.")
    return warnings


def pptx_slides(source: Path, media: Path) -> tuple[list[dict], list[str]]:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    from pptx.shapes.connector import Connector

    DRAWINGML = "http://schemas.openxmlformats.org/drawingml/2006/main"
    names_by_id: dict[str, str] = {}
    prs = Presentation(str(source))
    width, height = prs.slide_width or 1, prs.slide_height or 1
    warnings: list[str] = []
    slides = []

    def bbox(shape) -> list[float] | None:
        if shape.left is None or shape.width is None:
            return None
        return [round(shape.left / width, 4), round(shape.top / height, 4),
                round((shape.left + shape.width) / width, 4), round((shape.top + shape.height) / height, 4)]

    def walk(shapes, slide_no, record, prefix=""):
        for shape in shapes:
            name = f"{prefix}{shape.name}"
            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                record["groups"].append({"name": name, "bbox": bbox(shape)})
                walk(shape.shapes, slide_no, record, prefix=f"{name}/")
                continue
            if getattr(shape, "has_table", False) and shape.has_table:
                rows = [[cell.text for cell in row.cells] for row in shape.table.rows]
                record["tables"].append({"name": name, "bbox": bbox(shape), "rows": rows})
                continue
            if getattr(shape, "has_chart", False) and shape.has_chart:
                chart = shape.chart
                series = []
                try:
                    categories = [str(c) for c in chart.plots[0].categories] if chart.plots else []
                    for plot in chart.plots:
                        for s in plot.series:
                            series.append({"name": s.name, "values": list(s.values)})
                except Exception as error:  # charts vary widely; never fail the slide
                    categories = []
                    warnings.append(f"slide {slide_no}: chart {name!r} data not readable ({error})")
                record["charts"].append({"name": name, "bbox": bbox(shape), "type": str(chart.chart_type),
                                         "categories": categories, "series": series})
                continue
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE or hasattr(shape, "image"):
                try:
                    image = shape.image
                    filename = f"slide-{slide_no:03d}-{len(record['pictures']) + 1:02d}.{image.ext}"
                    media.mkdir(parents=True, exist_ok=True)
                    (media / filename).write_bytes(image.blob)
                    size = image.size
                except Exception:
                    filename, size = None, None
                record["pictures"].append({"name": name, "bbox": bbox(shape), "media": filename,
                                           "pixels": list(size) if size else None})
                continue
            if isinstance(shape, Connector):
                ends = {}
                for tag in ("stCxn", "endCxn"):
                    found = shape._element.find(f".//{{{DRAWINGML}}}{tag}")
                    ends[tag] = names_by_id.get(found.get("id")) if found is not None else None
                record["connectors"].append({"name": name, "bbox": bbox(shape),
                                             "from": ends["stCxn"], "to": ends["endCxn"]})
                continue
            lines = []
            if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = "".join(run.text for run in paragraph.runs).strip()
                    if text:
                        lines.append(("  " * (paragraph.level or 0)) + text)
            if shape.shape_type in (MSO_SHAPE_TYPE.AUTO_SHAPE, MSO_SHAPE_TYPE.FREEFORM) and not shape.is_placeholder:
                record["drawings"].append({"name": name, "bbox": bbox(shape), "text": " / ".join(l.strip() for l in lines)})
            elif lines:
                record["text"].append({"name": name, "bbox": bbox(shape), "lines": lines})

    for number, slide in enumerate(prs.slides, start=1):
        record = {"slide": number, "hidden": slide._element.get("show") == "0",
                  "title": "", "layout": slide.slide_layout.name, "text": [], "tables": [], "pictures": [],
                  "charts": [], "groups": [], "drawings": [], "connectors": [], "notes": ""}
        if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
            record["title"] = slide.shapes.title.text_frame.text.strip()

        def index_names(shapes, prefix=""):
            for shape in shapes:
                names_by_id[str(shape.shape_id)] = f"{prefix}{shape.name}"
                if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                    index_names(shape.shapes, f"{prefix}{shape.name}/")

        names_by_id.clear()
        index_names(slide.shapes)
        walk(slide.shapes, number, record)
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame is not None:
            record["notes"] = slide.notes_slide.notes_text_frame.text.strip()
        if record["drawings"] or record["connectors"] or record["groups"]:
            record["diagram_hint"] = True
        slides.append(record)
    return slides, warnings


def slides_markdown(source_name: str, slides: list[dict], rendered_pages: int) -> str:
    out = [f"# Slides: {source_name}", "",
           f"{len(slides)} slides in the deck; {rendered_pages} rendered pages. "
           "Positions are [left, top, right, bottom] as fractions of the slide; pass them to "
           "`kb figure --crop` to cut a graphic out of the slide render.", ""]
    for s in slides:
        title = s["title"] or "(untitled)"
        out += [f"## Slide {s['slide']}: {title}", ""]
        meta = [f"layout: {s['layout']}"]
        if s["hidden"]:
            meta.append("**hidden slide**")
        if s.get("diagram_hint"):
            meta.append("contains shapes/groups/connectors: likely a diagram, review the render")
        out += ["- " + "; ".join(meta), f"- Render: ![Slide {s['slide']}](renders/page-{s['slide']:03d}.png)", ""]
        for block in s["text"]:
            out += [f"**{block['name']}** `{block['bbox']}`", ""] + [f"    {line}" if line.startswith("  ") else line for line in block["lines"]] + [""]
        for table in s["tables"]:
            out += [f"**Table {table['name']}** `{table['bbox']}`", "", _md_table(table["rows"]), ""]
        for chart in s["charts"]:
            out += [f"**Chart {chart['name']}** ({chart['type']}) `{chart['bbox']}`", ""]
            if chart["series"]:
                header = ["series"] + chart["categories"]
                out += [_md_table([header] + [[x["name"]] + x["values"] for x in chart["series"]]), ""]
        for picture in s["pictures"]:
            media = f"media/{picture['media']}" if picture["media"] else "(not extractable)"
            out.append(f"- Picture **{picture['name']}** `{picture['bbox']}` → `{media}` {picture['pixels'] or ''}")
        if s["pictures"]:
            out.append("")
        if s["drawings"]:
            out += ["**Drawn shapes** (candidate diagram nodes; confirm against the render)", "",
                    _md_table([["shape", "text", "position"]] + [[d["name"], d["text"], d["bbox"]] for d in s["drawings"]]), ""]
        if s["connectors"]:
            out += ["**Connectors** (from/to are only known when the connector is glued to a shape)", "",
                    _md_table([["connector", "from", "to", "position"]] +
                              [[c["name"], c["from"] or "?", c["to"] or "?", c["bbox"]] for c in s["connectors"]]), ""]
        if s["notes"]:
            out += ["**Speaker notes**", "", s["notes"], ""]
    return "\n".join(out).rstrip() + "\n"


def xlsx_workbook(source: Path, sheets_dir: Path, max_cells: int = 200_000) -> tuple[dict, list[str]]:
    import csv

    from openpyxl import load_workbook

    warnings = []
    formulas = load_workbook(source, data_only=False)
    values = load_workbook(source, data_only=True)
    book = {"sheets": [], "defined_names": []}
    try:
        for name, defined in formulas.defined_names.items():
            book["defined_names"].append({"name": name, "refers_to": defined.attr_text})
    except Exception:
        pass
    total = 0
    sheets_dir.mkdir(parents=True, exist_ok=True)
    for ws in formulas.worksheets:
        wv = values[ws.title]
        sheet = {"name": ws.title, "state": ws.sheet_state, "dimensions": ws.dimensions,
                 "merged": [str(r) for r in ws.merged_cells.ranges], "charts": len(getattr(ws, "_charts", [])),
                 "images": len(getattr(ws, "_images", [])), "cells": []}
        if ws.sheet_state != "visible":
            warnings.append(f"sheet {ws.title!r} is {ws.sheet_state}")
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None:
                    continue
                total += 1
                if total > max_cells:
                    continue
                entry = {"ref": cell.coordinate, "number_format": cell.number_format}
                cached = wv[cell.coordinate].value
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    entry["formula"] = cell.value
                    entry["cached"] = cached if not hasattr(cached, "isoformat") else cached.isoformat()
                    if cached is None:
                        entry["cached_missing"] = True
                else:
                    entry["value"] = cell.value if not hasattr(cell.value, "isoformat") else cell.value.isoformat()
                sheet["cells"].append(entry)
        with (sheets_dir / f"{source_slug(ws.title)}.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            for row in wv.iter_rows(values_only=True):
                writer.writerow(["" if v is None else v for v in row])
        book["sheets"].append(sheet)
    if total > max_cells:
        warnings.append(f"{total} non-empty cells; workbook.json truncated at {max_cells}")
    missing = sum(1 for s in book["sheets"] for c in s["cells"] if c.get("cached_missing"))
    if missing:
        warnings.append(f"{missing} formulas have no cached value (workbook saved without calculation); do not read them as blank")
    return book, warnings


def review_template(source_rel: str, pages: int, kind: str) -> str:
    unit = "Slide" if kind == "presentation" else "Page"
    rows = "\n".join(f"| {n} | [ ] | | |" for n in range(1, pages + 1))
    return f"""# Review: {source_rel}

Fill this in during visual reconciliation (see the project's ingestion process).
Look at every render; compare with pages.md{', slides.md' if kind == 'presentation' else ''} and text.md.

## Per {unit.lower()}

| {unit} | Reviewed | Key graphics → figure path | Discrepancies / notes |
| --- | --- | --- | --- |
{rows}

## Reconciliation

- Counts (pages/slides/sheets/tables) agree across formats:
- Reading order problems:
- Raster-only text found:
- Diagrams found (reconstruct with element tables; mark inferred links):
- Not reviewed (and why):
"""


# ---------------------------------------------------------------- orchestration

def extract_source(repo: Repo, relative: str, *, dpi: int = 120, force: bool = False, update_log: bool = True) -> dict:
    source = repo.sources / relative
    if not source.is_file():
        raise SystemExit(f"kb: {source} not found")
    package = repo.extracted / source_slug(relative)
    if package.exists():
        if not force:
            raise SystemExit(f"kb: {repo.rel(package)} exists; pass --force to rebuild it")
        shutil.rmtree(package)
    package.mkdir(parents=True)
    suffix = source.suffix.lower()
    kind = ("presentation" if suffix in {".pptx", ".ppt", ".pps", ".ppsx", ".odp", ".key"} else
            "workbook" if suffix in {".xlsx", ".xlsm", ".xls", ".ods"} else
            "document" if suffix in OFFICE else "pdf" if suffix == ".pdf" else
            "image" if suffix in IMAGES else "other")
    manifest = {"source": f"docs/sources/{relative}", "sha256": sha256(source), "bytes": source.stat().st_size,
                "kind": kind, "extracted_at": now_iso(), "options": {"dpi": dpi}, "versions": _versions(),
                "outputs": [], "counts": {}, "warnings": [], "errors": []}

    def step(name, func):
        try:
            return func()
        except Exception as error:  # record and continue: partial extraction beats none
            manifest["errors"].append(f"{name}: {error}")
            return None

    text = step("markitdown", lambda: markitdown_text(source))
    if text is not None:
        atomic_write(package / "text.md", text)
        manifest["outputs"].append("text.md")

    pdf = source if suffix == ".pdf" else None
    if suffix in OFFICE:
        pdf = step("libreoffice", lambda: office_to_pdf(source, package))
        if pdf:
            manifest["outputs"].append("rendered.pdf")
    page_texts: list[str] = []
    if pdf:
        rendered = step("render", lambda: render_pdf(pdf, package / "renders", dpi))
        if rendered:
            manifest["counts"]["pages"], page_texts = rendered
            manifest["outputs"].append("renders/")
    elif kind == "image":
        if step("render", lambda: render_image(source, package / "renders")):
            manifest["counts"]["pages"] = 1
            manifest["outputs"].append("renders/")
    else:
        manifest["warnings"].append("no rendering for this format: visual review is limited to the original")

    if page_texts:
        unit = "Slide" if kind == "presentation" else "Page"
        sections = [f"# Pages: {relative}", "",
                    f"Text from the rendered PDF, one section per {unit.lower()}, with the render to review.", ""]
        for number, body in enumerate(page_texts, start=1):
            sections += [f"## {unit} {number}", "", f"![{unit} {number}](renders/page-{number:03d}.png)", "",
                         body or "_(no text layer: image-only page, review the render)_", ""]
        atomic_write(package / "pages.md", "\n".join(sections))
        manifest["outputs"].append("pages.md")
        empty = [str(i) for i, t in enumerate(page_texts, start=1) if not t]
        if empty:
            manifest["warnings"].append(f"pages without a text layer (raster-only): {', '.join(empty)}")

    if suffix == ".pptx":
        result = step("pptx", lambda: pptx_slides(source, package / "media"))
        if result:
            slides, warnings = result
            manifest["warnings"] += warnings
            manifest["counts"]["slides"] = len(slides)
            atomic_write(package / "slides.json", json.dumps(slides, indent=2, default=str))
            atomic_write(package / "slides.md", slides_markdown(relative, slides, manifest["counts"].get("pages", 0)))
            manifest["outputs"] += ["slides.md", "slides.json"]
            hidden = [str(s["slide"]) for s in slides if s["hidden"]]
            if hidden:
                manifest["warnings"].append(f"hidden slides: {', '.join(hidden)}")
            pages = manifest["counts"].get("pages")
            if pages is not None and pages != len(slides):
                manifest["warnings"].append(f"slide count {len(slides)} differs from rendered pages {pages} (hidden slides are often not exported)")
            diagrams = [str(s["slide"]) for s in slides if s.get("diagram_hint")]
            if diagrams:
                manifest["warnings"].append(f"slides with drawn shapes/connectors (possible diagrams): {', '.join(diagrams)}")
    elif suffix in {".docx", ".xlsx", ".xlsm"}:
        media = step("media", lambda: zip_media(source, package / "media"))
        if media:
            manifest["counts"]["media"] = len(media)
            manifest["outputs"].append("media/")
    if suffix == ".docx":
        manifest["warnings"] += docx_warnings(source)
    if suffix in {".xlsx", ".xlsm"}:
        result = step("xlsx", lambda: xlsx_workbook(source, package / "sheets"))
        if result:
            book, warnings = result
            manifest["warnings"] += warnings
            manifest["counts"]["sheets"] = len(book["sheets"])
            atomic_write(package / "workbook.json", json.dumps(book, indent=1, default=str))
            manifest["outputs"] += ["workbook.json", "sheets/"]
    if suffix in {".xls", ".ods"}:
        manifest["warnings"].append("formula extraction supports .xlsx/.xlsm only; convert to .xlsx for workbook.json")

    pages = manifest["counts"].get("slides") or manifest["counts"].get("pages") or 0
    atomic_write(package / "review.md", review_template(f"docs/sources/{relative}", pages, kind))
    manifest["outputs"].append("review.md")
    manifest["status"] = "failed" if not manifest["outputs"][:-1] else ("partial" if manifest["errors"] else "ok")
    atomic_write(package / "manifest.json", json.dumps(manifest, indent=2))

    if update_log:
        rows = ingest_log.load(repo.log_path)
        index = ingest_log.by_source(rows)
        row = index.get(relative)
        if row is not None:
            row["extraction"] = repo.rel(package)
            if row["status"] == "pending" and manifest["status"] != "failed":
                row["status"] = "extracted"
            ingest_log.save(repo.log_path, rows)
        else:
            manifest["warnings"].append("source is not in the ingest log; run `kb inventory`")
    return {"package": repo.rel(package), **{k: manifest[k] for k in ("status", "counts", "warnings", "errors")}}


def pending_sources(repo: Repo) -> list[str]:
    return [row["source"] for row in ingest_log.load(repo.log_path)
            if row["status"] == "pending" and (repo.sources / row["source"]).is_file()]


os.environ.setdefault("SAL_USE_VCLPLUGIN", "svp")  # headless LibreOffice without a display

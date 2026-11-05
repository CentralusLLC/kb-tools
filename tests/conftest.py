from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from kbtools.common import Repo
from kbtools.intake import init

HAS_SOFFICE = bool(shutil.which("soffice") or shutil.which("libreoffice"))
needs_soffice = pytest.mark.skipif(not HAS_SOFFICE, reason="LibreOffice not installed")


@pytest.fixture
def repo(tmp_path: Path) -> Repo:
    (tmp_path / ".git").mkdir()
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Test bundle\n')
    r = Repo(tmp_path)
    init(r)
    return r


def make_png(path: Path, size=(400, 300), color=(200, 30, 30)) -> Path:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", size, "white")
    ImageDraw.Draw(image).rectangle([size[0] // 4, size[1] // 4, size[0] * 3 // 4, size[1] * 3 // 4], fill=color)
    image.save(path)
    return path


def make_pptx(path: Path, picture: Path) -> Path:
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
    from pptx.util import Inches

    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "World layers"
    body = slide.placeholders[1].text_frame
    body.text = "Boards contain spaces"
    body.add_paragraph().text = "Spaces hold tiles"
    body.paragraphs[1].level = 1
    slide.notes_slide.notes_text_frame.text = "Speaker note about layers"

    slide2 = prs.slides.add_slide(prs.slide_layouts[5])
    slide2.shapes.title.text = "Diagram and data"
    a = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(2), Inches(2), Inches(1))
    a.text = "WorldBoard"
    b = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(5), Inches(2), Inches(2), Inches(1))
    b.text = "TerrainBoard"
    line = slide2.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(3), Inches(2.5), Inches(5), Inches(2.5))
    line.begin_connect(a, 3)
    line.end_connect(b, 1)
    slide2.shapes.add_picture(str(picture), Inches(1), Inches(4), Inches(2), Inches(1.5))
    rows = slide2.shapes.add_table(2, 2, Inches(5), Inches(4), Inches(3), Inches(1)).table
    rows.cell(0, 0).text, rows.cell(0, 1).text = "Terrain", "Cost"
    rows.cell(1, 0).text, rows.cell(1, 1).text = "Forest", "1.5"
    data = CategoryChartData()
    data.categories = ["Grass", "Sand"]
    data.add_series("Cost", (1.0, 1.2))
    slide2.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(8), Inches(4), Inches(1.8), Inches(1.5), data)
    prs.save(path)
    return path


def make_xlsx(path: Path) -> Path:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Costs"
    ws.append(["terrain", "cost"])
    ws.append(["grass", 1])
    ws.append(["forest", 1.5])
    ws["B4"] = "=SUM(B2:B3)"
    hidden = wb.create_sheet("Hidden")
    hidden["A1"] = "secret"
    hidden.sheet_state = "hidden"
    wb.save(path)
    return path


def make_docx(path: Path, picture: Path) -> Path:
    from docx import Document  # python-docx comes with markitdown[docx]

    document = Document()
    document.add_heading("Creature notes", 1)
    document.add_paragraph("Wolves hunt in packs.")
    document.add_picture(str(picture))
    document.save(path)
    return path


def make_pdf(path: Path, picture: Path) -> Path:
    from PIL import Image

    with Image.open(picture) as image:
        image.convert("RGB").save(path, "PDF")
    return path

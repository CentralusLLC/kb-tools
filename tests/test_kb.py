from __future__ import annotations

import json
from datetime import datetime, timezone

from conftest import make_docx, make_pdf, make_png, make_pptx, make_xlsx, needs_soffice

from kbtools import ingest_log
from kbtools.check import run_checks
from kbtools.cli import main
from kbtools.extract import extract_source
from kbtools.figure import make_figure
from kbtools.intake import inventory, update_row
from kbtools.report import page_trust, render


def test_init_creates_gitignored_intake(repo):
    ignore = (repo.sources / ".gitignore").read_text()
    assert "*\n" in ignore and "!ingest-log.csv" in ignore
    assert (repo.extracted / ".gitignore").exists()
    assert ingest_log.header_problems(repo.log_path) == []


def test_inventory_logs_new_and_detects_changes(repo):
    make_png(repo.sources / "map.png")
    result = inventory(repo, added_by="human:test", origin="paperclip:CEN-1")
    assert result["added"] == ["map.png"]
    row = ingest_log.by_source(ingest_log.load(repo.log_path))["map.png"]
    assert row["status"] == "pending" and row["origin"] == "paperclip:CEN-1" and len(row["sha256"]) == 64
    make_png(repo.sources / "map.png", color=(0, 0, 255))
    assert inventory(repo, added_by="human:test")["changed"] == ["map.png"]
    (repo.sources / "map.png").unlink()
    assert inventory(repo, added_by="human:test")["missing_locally"] == ["map.png"]


def test_log_update_sets_dates_and_outputs(repo):
    make_png(repo.sources / "a.png")
    inventory(repo, added_by="human:test")
    row = update_row(repo, "a.png", status="ingested", by="claude-code/test", add_outputs=["docs/index.md"])
    assert row["ingested_at"] and row["ingested_by"] == "claude-code/test" and row["outputs"] == "docs/index.md"


@needs_soffice
def test_extract_pptx_package(repo, tmp_path):
    picture = make_png(tmp_path / "pic.png")
    make_pptx(repo.sources / "deck.pptx", picture)
    inventory(repo, added_by="human:test")
    result = extract_source(repo, "deck.pptx")
    package = repo.root / result["package"]
    assert result["status"] == "ok", result
    assert result["counts"]["slides"] == 2 and result["counts"]["pages"] == 2
    slides = json.loads((package / "slides.json").read_text())
    assert slides[0]["notes"] == "Speaker note about layers"
    assert slides[1]["tables"][0]["rows"][1] == ["Forest", "1.5"]
    assert slides[1]["pictures"][0]["media"] and (package / "media" / slides[1]["pictures"][0]["media"]).exists()
    assert slides[1]["charts"][0]["series"][0]["values"] == [1.0, 1.2]
    assert slides[1].get("diagram_hint")
    assert slides[1]["connectors"][0]["from"] and slides[1]["connectors"][0]["to"]
    assert {d["text"] for d in slides[1]["drawings"]} == {"WorldBoard", "TerrainBoard"}
    assert (package / "renders" / "page-002.png").exists()
    md = (package / "slides.md").read_text()
    assert "## Slide 2: Diagram and data" in md and "renders/page-002.png" in md
    assert "WorldBoard" in (package / "pages.md").read_text()
    assert ingest_log.by_source(ingest_log.load(repo.log_path))["deck.pptx"]["status"] == "extracted"


@needs_soffice
def test_extract_xlsx_formulas_and_hidden_sheets(repo):
    make_xlsx(repo.sources / "costs.xlsx")
    inventory(repo, added_by="human:test")
    result = extract_source(repo, "costs.xlsx")
    package = repo.root / result["package"]
    book = json.loads((package / "workbook.json").read_text())
    formula = next(c for c in book["sheets"][0]["cells"] if c["ref"] == "B4")
    assert formula["formula"] == "=SUM(B2:B3)" and formula.get("cached_missing")
    assert any("hidden" in w for w in result["warnings"])
    assert any("no cached value" in w for w in result["warnings"])
    assert (package / "sheets" / "costs.csv").exists()


@needs_soffice
def test_extract_docx_and_pdf(repo, tmp_path):
    picture = make_png(tmp_path / "pic.png")
    make_docx(repo.sources / "notes.docx", picture)
    make_pdf(repo.sources / "scan.pdf", picture)
    inventory(repo, added_by="human:test")
    docx = extract_source(repo, "notes.docx")
    assert docx["status"] == "ok" and docx["counts"]["media"] == 1
    assert "Wolves" in (repo.root / docx["package"] / "text.md").read_text()
    pdf = extract_source(repo, "scan.pdf")
    assert pdf["counts"]["pages"] == 1
    assert any("without a text layer" in w for w in pdf["warnings"])


def test_extract_image_without_soffice(repo):
    make_png(repo.sources / "sketch.png")
    inventory(repo, added_by="human:test")
    result = extract_source(repo, "sketch.png")
    assert (repo.root / result["package"] / "renders" / "page-001.png").exists()
    assert (repo.root / result["package"] / "review.md").exists()


def test_figure_rejects_images_outside_repo(repo, tmp_path_factory):
    import pytest

    outside = make_png(tmp_path_factory.mktemp("elsewhere") / "x.png")
    with pytest.raises(SystemExit):
        make_figure(repo, outside, repo.docs / "assets" / "x.png")


def test_figure_crops_into_docs_with_snippet(repo):
    (repo.extracted / "pkg" / "renders").mkdir(parents=True)
    render_png = make_png(repo.extracted / "pkg" / "renders" / "page-001.png", size=(1000, 500))
    snippet = make_figure(repo, render_png, repo.docs / "world" / "assets" / "layers.png",
                          crop="0.25,0.25,0.75,0.75", page=repo.docs / "world" / "model.md",
                          alt="Board layers", caption="How boards nest", source_ref="docs/sources/deck.pptx, slide 2")
    from PIL import Image

    with Image.open(repo.docs / "world" / "assets" / "layers.png") as image:
        assert 500 <= image.size[0] <= 520
    assert "![Board layers](assets/layers.png)" in snippet and "| Element |" in snippet


def _write_page(repo, name, front, body="Text.\n"):
    path = repo.docs / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front}\n---\n\n{body}")
    return path


def test_check_flags_problems(repo):
    _write_page(repo, "good.md", "type: Guide\nstatus: stable")
    (repo.docs / "bad.md").write_text("no front matter\n")
    _write_page(repo, "links.md", "type: Guide", "![](missing.png)\n[gone](nowhere.md)\n")
    _write_page(repo, "diagram.md", "type: Guide", "```mermaid\nflowchart LR\nA-->B\n```\n\nJust prose.\n")
    _write_page(repo, "diagram-ok.md", "type: Guide", "```mermaid\nflowchart LR\nA-->B\n```\n\n| Element | Meaning |\n| --- | --- |\n| A | start |\n")
    errors, warnings = run_checks(repo)
    joined = "\n".join(errors + warnings)
    assert "bad.md: missing front matter" in joined
    assert "broken image missing.png" in joined and "broken link nowhere.md" in joined
    assert "diagram.md: Mermaid diagram" in joined and "diagram-ok.md: Mermaid" not in joined
    assert "good.md" not in joined


def test_report_tiers_and_flags(repo):
    _write_page(repo, "human.md", "type: Guide\ngenerated: {by: x, at: 2026-01-01T00:00:00Z}\n"
                "verified:\n  - {by: 'human:reviewer', at: 2026-02-01T00:00:00Z}")
    _write_page(repo, "machine.md", "type: Guide\ngenerated: {by: x, at: 2026-03-01T00:00:00Z}\n"
                "verified:\n  - {by: 'process:kb-check', at: 2026-02-01T00:00:00Z}\nstale_after: 2026-04-01T00:00:00Z")
    _write_page(repo, "none.md", "type: Guide")
    rows = {r["page"]: r for r in page_trust(repo, 365, now=datetime(2026, 11, 1, tzinfo=timezone.utc))}
    assert rows["docs/human.md"]["tier"] == "human" and rows["docs/human.md"]["flags"] == ""
    assert rows["docs/machine.md"]["tier"] == "machine"
    assert "changed-since-verified" in rows["docs/machine.md"]["flags"] and "stale" in rows["docs/machine.md"]["flags"]
    assert rows["docs/none.md"]["tier"] == "unverified"
    assert "1 human-verified" in render(list(rows.values()), "md")


def test_cli_end_to_end(repo, capsys):
    make_png(repo.sources / "x.png")
    assert main(["--repo", str(repo.root), "inventory", "--by", "human:test"]) == 0
    assert main(["--repo", str(repo.root), "extract", "--pending"]) == 0
    assert main(["--repo", str(repo.root), "log", "x.png", "--status", "skipped", "--notes", "test"]) == 0
    assert main(["--repo", str(repo.root), "check"]) == 0
    assert "skipped" in capsys.readouterr().out


def test_scaffold_installs_clean_generic_bundle(tmp_path):
    from pathlib import Path

    from kbtools.common import Repo
    from kbtools.scaffold import scaffold, template_files

    (tmp_path / ".git").mkdir()
    result = scaffold(tmp_path, project="Acme: Portal", actor="kb-tools/test")
    assert "docs/index.md" in result["created"] and "docs/sources/.gitignore" in result["created"]
    assert ".github/copilot-instructions.md" in result["created"] and "extracted/.gitignore" in result["created"]
    for path in result["created"]:
        text = (tmp_path / path).read_text(errors="ignore")
        assert "{{" not in text, path
    assert "Acme: Portal" in (tmp_path / "docs" / "index.md").read_text()
    assert (tmp_path / "tools" / "kb").stat().st_mode & 0o111
    bin_kb = Path(__file__).resolve().parents[1] / "bin" / "kb"
    if bin_kb.exists():
        assert (tmp_path / "tools" / "kb").read_bytes() == bin_kb.read_bytes(), "template tools/kb drifted from bin/kb"
    header = (tmp_path / "docs" / "sources" / "ingest-log.csv").read_text().splitlines()[0]
    assert header.split(",") == ingest_log.COLUMNS
    errors, warnings = run_checks(Repo(tmp_path))
    assert errors == [] and warnings == [], errors + warnings
    words = ("gameworld", "centralus", "phaser", "creature")
    for name, node in template_files():
        text = node.read_bytes().decode("utf-8", "ignore").lower()
        assert not any(w in text for w in words), name


def test_scaffold_never_overwrites(tmp_path):
    from kbtools.scaffold import scaffold

    (tmp_path / "AGENTS.md").write_text("mine\n")
    first = scaffold(tmp_path, project="X", actor="t")
    assert "AGENTS.md" in first["skipped"]
    assert (tmp_path / "AGENTS.md").read_text() == "mine\n"
    second = scaffold(tmp_path, project="X", actor="t")
    assert second["created"] == []

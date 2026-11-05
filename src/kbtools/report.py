"""Trust report: verification level and recency for every knowledge page.

Tiers follow OKF: unverified (no `verified`), machine (verified only by non-human
actors), human (at least one `human:` entry). Recency and whether the page changed
after its last verification decide how far an agent should rely on it.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from . import okf
from .common import Repo, to_datetime


def page_trust(repo: Repo, max_age_days: int, now: datetime | None = None) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    rows = []
    for path in okf.bundle_pages(repo.docs):
        if not okf.is_concept(path):
            continue
        data, _, error = okf.parse_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        if error or data is None or okf.is_template(data) or str(data.get("type", "")).strip() == "Catalog":
            continue
        entries = okf.verified_entries(data)
        stamps = [(str(e.get("by", "")), to_datetime(e.get("at"))) for e in entries]
        stamps = [(by, at) for by, at in stamps if at]
        human = [at for by, at in stamps if by.startswith("human:")]
        last = max((at for _, at in stamps), default=None)
        last_human = max(human, default=None)
        tier = "human" if human else ("machine" if stamps else "unverified")
        generated = data.get("generated") if isinstance(data.get("generated"), dict) else {}
        generated_at = to_datetime(generated.get("at"))
        stale_after = to_datetime(data.get("stale_after"))
        flags = []
        if last and generated_at and generated_at > last:
            flags.append("changed-since-verified")
        if stale_after and stale_after < now:
            flags.append("stale")
        if last and (now - last).days > max_age_days:
            flags.append("verification-old")
        if str(data.get("status", "stable")).strip() == "deprecated":
            flags.append("deprecated")
        rows.append({
            "page": repo.rel(path),
            "type": str(data.get("type", "")),
            "status": str(data.get("status", "stable")),
            "tier": tier,
            "last_verified": last.date().isoformat() if last else "",
            "last_human": last_human.date().isoformat() if last_human else "",
            "age_days": (now - last).days if last else "",
            "generated_at": generated_at.date().isoformat() if generated_at else "",
            "flags": ",".join(flags),
        })
    return rows


def render(rows: list[dict], fmt: str) -> str:
    if fmt == "json":
        return json.dumps(rows, indent=2)
    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]) if rows else ["page"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()
    total = len(rows)
    counts = {tier: sum(1 for r in rows if r["tier"] == tier) for tier in ("human", "machine", "unverified")}
    flagged = {flag: sum(1 for r in rows if flag in r["flags"].split(","))
               for flag in ("changed-since-verified", "stale", "verification-old", "deprecated")}
    lines = [
        "# Knowledge trust report", "",
        f"{total} pages: {counts['human']} human-verified, {counts['machine']} machine-verified, "
        f"{counts['unverified']} unverified.",
        "Flags: " + ", ".join(f"{k} {v}" for k, v in flagged.items()) + ".", "",
        "| Page | Status | Tier | Last verified | Last human | Age (days) | Flags |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    order = {"human": 0, "machine": 1, "unverified": 2}
    for r in sorted(rows, key=lambda r: (order[r["tier"]], r["page"])):
        lines.append(f"| {r['page']} | {r['status']} | {r['tier']} | {r['last_verified']} | "
                     f"{r['last_human']} | {r['age_days']} | {r['flags']} |")
    return "\n".join(lines) + "\n"

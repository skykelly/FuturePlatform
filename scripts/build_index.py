#!/usr/bin/env python3
"""Build data/signals.json and dashboard/dist.html from markdown notes.

No third-party dependencies. Frontmatter supports `key: value` and
inline lists `key: [a, b]`.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)
VALID_DIR = {"+", "-", "new"}


def parse_value(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    v = v.strip('"').strip("'")
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if re.fullmatch(r"-?\d+(\.\d+)?", v):
        return float(v) if "." in v else int(v)
    return v


def read_note(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        return None, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = parse_value(v)
    return meta, m.group(2)


def section(body: str, title: str) -> str:
    m = re.search(rf"## {re.escape(title)}\n(.*?)(?=\n## |\Z)", body, re.S)
    return m.group(1).strip() if m else ""


def main():
    errors = []
    thesis = {}
    for p in sorted((ROOT / "thesis").glob("PF-*.md")):
        meta, _ = read_note(p)
        thesis[meta["id"]] = {k: meta.get(k) for k in
                              ("id", "name", "control_point", "stack", "quadrant", "score", "weight")}
    indices = []
    for p in sorted((ROOT / "indices").glob("*.md")):
        meta, _ = read_note(p)
        indices.append(meta["name"])

    signals = []
    seen_urls = {}
    for p in sorted((ROOT / "signals").rglob("*.md")):
        meta, body = read_note(p)
        if not meta:
            errors.append(f"{p}: frontmatter 없음")
            continue
        sid = meta.get("id", p.stem)
        pf = meta.get("pf") or []
        idx = meta.get("index") or []
        if isinstance(pf, str):
            pf = [pf]
        if isinstance(idx, str):
            idx = [idx]
        for x in pf:
            if x not in thesis:
                errors.append(f"{sid}: 알 수 없는 PF {x}")
        for x in idx:
            if x not in indices:
                errors.append(f"{sid}: 알 수 없는 지수 {x}")
        if str(meta.get("direction")) not in VALID_DIR:
            errors.append(f"{sid}: direction 값 오류 {meta.get('direction')}")
        if meta.get("strength") not in (1, 2, 3):
            errors.append(f"{sid}: strength 값 오류 {meta.get('strength')}")
        url = meta.get("url", "")
        if url in seen_urls:
            errors.append(f"{sid}: URL 중복 ({seen_urls[url]})")
        seen_urls[url] = sid
        signals.append({
            "id": sid,
            "title": meta.get("title", ""),
            "collected": str(meta.get("collected", "")),
            "published": str(meta.get("published", "")),
            "source": meta.get("source", ""),
            "url": url,
            "type": meta.get("type", ""),
            "direction": str(meta.get("direction")),
            "strength": meta.get("strength"),
            "pf": pf,
            "index": idx,
            "japan": bool(meta.get("japan", False)),
            "status": meta.get("status", "accepted"),
            "summary": section(body, "요지"),
            "path": str(p.relative_to(ROOT)),
        })

    signals.sort(key=lambda s: (s["collected"], s["id"]), reverse=True)
    data = {
        "generated": date.today().isoformat(),
        "thesis": thesis,
        "indices": indices,
        "signals": signals,
    }
    out = ROOT / "data" / "signals.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    tpl = ROOT / "dashboard" / "template.html"
    if tpl.exists():
        html = tpl.read_text(encoding="utf-8")
        payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        html = html.replace("/*__DATA__*/null", payload)
        (ROOT / "dashboard" / "dist.html").write_text(html, encoding="utf-8")

    print(f"signals: {len(signals)}, thesis: {len(thesis)}, indices: {len(indices)}")
    if errors:
        print("검증 오류:")
        for e in errors:
            print(" -", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

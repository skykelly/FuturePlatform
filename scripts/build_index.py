#!/usr/bin/env python3
"""FuturePlatform 빌드.

1) signals/ 노트와 data/scores.json을 검증한다.
2) wiki/PF-*.md 의 AUTO 블록(스코어·이력·출처)과 wiki/Portfolio.md 의 포트폴리오 표를 다시 쓴다.
3) data/signals.json 과 포털(dashboard/dist.html)을 만든다.

외부 의존성 없음. 오류가 있으면 종료 코드 1.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FM = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.S)
VALID_DIR = {"+", "-", "new"}
TIERS = ["컨설팅", "투자은행", "산업리서치", "정부·공공", "글로벌기업", "언론"]
DIR_LABEL = {"+": "강화", "-": "약화", "new": "신규"}
REQUIRED_WIKI = ["id", "name", "name_ko", "one_liner", "stack", "control_point", "mechanism", "conviction", "updated"]


# ---------- parsing ----------
def parse_value(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if re.fullmatch(r"-?\d+(\.\d+)?", v):
        return float(v) if "." in v else int(v)
    return v


def read_note(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FM.match(text)
    if not m:
        return None, text, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = parse_value(v)
    return meta, m.group(2), text


def section(body: str, title: str) -> str:
    m = re.search(rf"## {re.escape(title)}\n(.*?)(?=\n## |\Z)", body, re.S)
    return m.group(1).strip() if m else ""


def as_list(v):
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


def fmt(x):
    return f"{x:.1f}"


def delta_str(d):
    if abs(d) < 1e-9:
        return "–"
    return ("+" if d > 0 else "−") + f"{abs(d):.1f}"


def replace_block(text, name, content):
    pat = re.compile(rf"(<!-- AUTO:{name} -->)(.*?)(<!-- /AUTO:{name} -->)", re.S)
    if not pat.search(text):
        return None
    return pat.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


# ---------- scoring ----------
def compute(scores):
    crit = [c["key"] for c in scores["criteria"]]
    q = scores["quadrant_rule"]
    out = {}
    for pf, s in scores["pf"].items():
        res = {}
        for kind in ("baseline", "current"):
            v = s[kind]
            total = sum(v[k] for k in crit)
            x = sum(v[k] for k in q["x"])
            y = sum(v[k] for k in q["y"])
            key = ("H" if x >= q["x_threshold"] else "L") + ("H" if y >= q["y_threshold"] else "L")
            res[kind] = {"scores": v, "total": total, "x": x, "y": y, "quadrant": q["names"][key]}
        out[pf] = res
    return out


# ---------- main ----------
def main():
    errors = []
    scores = json.loads((ROOT / "data" / "scores.json").read_text(encoding="utf-8"))
    crit_keys = [c["key"] for c in scores["criteria"]]
    crit_label = {c["key"]: c["label"] for c in scores["criteria"]}
    for pf, s in scores["pf"].items():
        for kind in ("baseline", "current"):
            for k in crit_keys:
                v = s[kind].get(k)
                if v is None or not (1 <= v <= 5) or (v * 2) % 1:
                    errors.append(f"scores {pf}.{kind}.{k}: 1~5 사이 0.5 단위가 아님 ({v})")
    calc = compute(scores)

    # indices
    indices = []
    for p in sorted((ROOT / "indices").glob("*.md")):
        meta, _, _ = read_note(p)
        indices.append(meta["name"])

    # wiki meta
    wiki_paths = sorted((ROOT / "wiki").glob("PF-*.md"))
    thesis = {}
    for p in wiki_paths:
        meta, body, _ = read_note(p)
        for k in REQUIRED_WIKI:
            if k not in meta:
                errors.append(f"{p.name}: frontmatter {k} 없음")
        thesis[meta["id"]] = {k: meta.get(k) for k in REQUIRED_WIKI + ["name_ko", "essence"]}
        if meta["id"] not in scores["pf"]:
            errors.append(f"{meta['id']}: scores.json 항목 없음")

    # signals
    signals = []
    seen_urls = {}
    for p in sorted((ROOT / "signals").rglob("*.md")):
        meta, body, _ = read_note(p)
        if not meta:
            errors.append(f"{p}: frontmatter 없음")
            continue
        sid = meta.get("id", p.stem)
        if sid != p.stem:
            errors.append(f"{p}: id와 파일명 불일치")
        pf = as_list(meta.get("pf"))
        idx = as_list(meta.get("index"))
        crit = as_list(meta.get("criteria"))
        for x in pf:
            if x not in thesis:
                errors.append(f"{sid}: 알 수 없는 PF {x}")
        for x in idx:
            if x not in indices:
                errors.append(f"{sid}: 알 수 없는 지수 {x}")
        for x in crit:
            if x not in crit_keys:
                errors.append(f"{sid}: 알 수 없는 기준 {x}")
        if meta.get("tier") not in TIERS:
            errors.append(f"{sid}: tier 값 오류 {meta.get('tier')}")
        if str(meta.get("direction")) not in VALID_DIR:
            errors.append(f"{sid}: direction 값 오류 {meta.get('direction')}")
        if meta.get("strength") not in (1, 2, 3):
            errors.append(f"{sid}: strength 값 오류 {meta.get('strength')}")
        url = meta.get("url", "")
        if url in seen_urls:
            errors.append(f"{sid}: URL 중복 ({seen_urls[url]})")
        seen_urls[url] = sid
        signals.append({
            "id": sid, "title": meta.get("title", ""),
            "collected": str(meta.get("collected", "")), "published": str(meta.get("published", "")),
            "source": meta.get("source", ""), "url": url, "type": meta.get("type", ""),
            "tier": meta.get("tier", ""), "direction": str(meta.get("direction")),
            "strength": meta.get("strength"), "pf": pf, "index": idx, "criteria": crit,
            "japan": bool(meta.get("japan", False)), "status": meta.get("status", "accepted"),
            "summary": section(body, "요지"), "path": str(p.relative_to(ROOT)),
        })
    sig_by_id = {s["id"]: s for s in signals}

    for h in scores["history"]:
        for sid in h["signals"]:
            if sid not in sig_by_id:
                errors.append(f"history {h['pf']}.{h['criterion']}: 없는 신호 {sid}")
        cur = scores["pf"][h["pf"]]["current"][h["criterion"]]
    for w in scores["watch"]:
        for sid in w["signals"] + w.get("counter", []):
            if sid not in sig_by_id:
                errors.append(f"watch {w['pf']}: 없는 신호 {sid}")

    # ---------- wiki AUTO blocks ----------
    wiki_md = {}
    for p in wiki_paths:
        meta, body, text = read_note(p)
        pf = meta["id"]
        c = calc[pf]
        base, cur = c["baseline"], c["current"]
        last_change = {}
        for h in scores["history"]:
            if h["pf"] == pf:
                last_change[h["criterion"]] = h

        rows = ["| 기준 | 기준선 (" + scores["baseline_meta"]["date"] + ") | 현재 | 변화 | 최근 변경 근거 |",
                "|---|:-:|:-:|:-:|---|"]
        for k in crit_keys:
            b, v = base["scores"][k], cur["scores"][k]
            h = last_change.get(k)
            why = ""
            if h:
                why = h["date"] + " · " + ", ".join(f"[[{s}]]" for s in h["signals"])
            rows.append(f"| {crit_label[k]} | {fmt(b)} | **{fmt(v)}** | {delta_str(v - b)} | {why} |")
        dt = cur["total"] - base["total"]
        summary = (f"**총점 {fmt(cur['total'])} / 40** (기준선 {fmt(base['total'])}, {delta_str(dt)}) · "
                   f"**사분면 {cur['quadrant']}** — X(독점우위+실행) {fmt(cur['x'])} · Y(네트워크+TAM) {fmt(cur['y'])}")
        if cur["quadrant"] != base["quadrant"]:
            summary += f"\n\n> ⚠ 사분면 이동: {base['quadrant']} → {cur['quadrant']}"
        score_block = summary + "\n\n" + "\n".join(rows)

        log_lines = []
        hist = [h for h in scores["history"] if h["pf"] == pf]
        if hist:
            log_lines.append("**점수 변경**\n")
            for h in sorted(hist, key=lambda h: h["date"], reverse=True):
                refs = ", ".join(f"[[{s}]]" for s in h["signals"])
                log_lines.append(f"- {h['date']} · {crit_label[h['criterion']]} {fmt(h['from'])} → {fmt(h['to'])} — {h['rationale']} ({refs})")
        else:
            log_lines.append("점수 변경 없음 (기준선 유지).")
        wl = [w for w in scores["watch"] if w["pf"] == pf]
        if wl:
            log_lines.append("\n**관찰 중 (변경 보류)**\n")
            for w in wl:
                refs = ", ".join(f"[[{s}]]" for s in w["signals"])
                cnt = ", ".join(f"[[{s}]]" for s in w.get("counter", []))
                log_lines.append(f"- {w['since']}~ · {crit_label[w['criterion']]} {DIR_LABEL[w['direction']]} 방향 — {w['note']} (근거 {refs}; 반대 근거 {cnt or '없음'})")
        log_block = "\n".join(log_lines)

        mine = [s for s in signals if pf in s["pf"]]
        tier_rank = {t: i for i, t in enumerate(TIERS)}
        mine.sort(key=lambda s: (tier_rank.get(s["tier"], 99), s["published"]), reverse=False)
        mine.sort(key=lambda s: tier_rank.get(s["tier"], 99))
        counts = {}
        for s in mine:
            counts[s["tier"]] = counts.get(s["tier"], 0) + 1
        head = f"출처 {len(mine)}건 — " + " · ".join(f"{t} {counts[t]}" for t in TIERS if t in counts)
        src_lines = [head, ""]
        for i, s in enumerate(mine, 1):
            st = "●" * s["strength"] + "○" * (3 - s["strength"])
            flag = " · 검토 대기" if s["status"] == "review" else ""
            src_lines.append(
                f"{i}. **[{s['tier']}]** {s['source']}, {s['published']} — [{s['title']}]({s['url']}) · "
                f"[[{s['id']}]] · {DIR_LABEL[s['direction']]} {st}{flag}")
        src_block = "\n".join(src_lines)

        new = text
        for name, content in (("SCORE", score_block), ("LOG", log_block), ("SOURCES", src_block)):
            r = replace_block(new, name, content)
            if r is None:
                errors.append(f"{p.name}: AUTO:{name} 블록 없음")
            else:
                new = r
        if new != text:
            p.write_text(new, encoding="utf-8")
        wiki_md[pf] = new

    # decisions
    dpath = ROOT / "data" / "decisions.json"
    decisions = json.loads(dpath.read_text(encoding="utf-8")) if dpath.exists() else []
    for d in decisions:
        for sid in d.get("evidence", []):
            if sid not in sig_by_id:
                errors.append(f"decision {d['id']}: 없는 신호 {sid}")
        for x in d.get("pf", []):
            if x not in thesis:
                errors.append(f"decision {d['id']}: 알 수 없는 PF {x}")

    # digests (needed for LATEST)
    digests = []
    for p in sorted((ROOT / "digests").glob("*.md"), reverse=True):
        meta, body, text = read_note(p)
        digests.append({"date": str((meta or {}).get("date", p.stem)), "kind": (meta or {}).get("kind", "regular"),
                        "title": (meta or {}).get("title", ""),
                        "path": str(p.relative_to(ROOT)), "markdown": body if meta else text})

    # Portfolio
    port = ROOT / "wiki" / "Portfolio.md"
    if port.exists():
        text = port.read_text(encoding="utf-8")
        open_d = [d for d in decisions if d.get("status") == "open"]
        n_ib = sum(1 for s in signals if s["tier"] in ("컨설팅", "투자은행"))
        snap = (f"> **현재 상태** · {date.today().isoformat()} 갱신 · 신호 {len(signals)}건 (컨설팅·투자은행 {n_ib}건) · "
                f"9월 평가 이후 점수 변경 {len(scores['history'])}건 · 관찰 중 {len(scores['watch'])}건 · "
                f"결정이 필요한 질문 {len(open_d)}건")
        text = replace_block(text, "SNAPSHOT", snap) or text

        # CHANGES
        moved = sorted(calc, key=lambda k: -(calc[k]["current"]["total"] - calc[k]["baseline"]["total"]))
        ups = [f"{pf} ({delta_str(calc[pf]['current']['total'] - calc[pf]['baseline']['total'])})" for pf in moved
               if calc[pf]["current"]["total"] > calc[pf]["baseline"]["total"]]
        downs = [f"{pf} ({delta_str(calc[pf]['current']['total'] - calc[pf]['baseline']['total'])})" for pf in moved
                 if calc[pf]["current"]["total"] < calc[pf]["baseline"]["total"]]
        qmoves = [f"{pf} {calc[pf]['baseline']['quadrant']} → {calc[pf]['current']['quadrant']}" for pf in sorted(calc)
                  if calc[pf]["baseline"]["quadrant"] != calc[pf]["current"]["quadrant"]]
        ch = [f"- **점수가 오른 Thesis**: {', '.join(ups) or '없음'}",
              f"- **점수가 내려간 Thesis**: {', '.join(downs) or '없음'}",
              f"- **사분면 이동**: {', '.join(qmoves) or '없음 — 9개 모두 9월 위치 유지'}",
              "", "**점수 변경 내역**", "",
              "| Thesis | 기준 | 9월 → 현재 | 왜 바뀌었나 | 근거 |", "|---|---|:-:|---|---|"]
        for h in sorted(scores["history"], key=lambda h: (h["date"], h["pf"]), reverse=True):
            refs = " ".join(f"[[{s}]]" for s in h["signals"])
            ch.append(f"| [[{h['pf']}]] {thesis[h['pf']]['name']} | {crit_label[h['criterion']]} | "
                      f"{fmt(h['from'])}→**{fmt(h['to'])}** | {h['rationale']} | {refs} |")
        if scores["watch"]:
            ch += ["", "**관찰 중 — 근거가 엇갈려 아직 점수를 바꾸지 않은 항목**", "",
                   "| Thesis | 기준 | 방향 | 무엇을 보고 있나 |", "|---|---|:-:|---|"]
            for w in scores["watch"]:
                ch.append(f"| [[{w['pf']}]] {thesis[w['pf']]['name']} | {crit_label[w['criterion']]} | "
                          f"{DIR_LABEL[w['direction']]} | {w['note']} |")
        text = replace_block(text, "CHANGES", "\n".join(ch)) or text

        # DECISIONS
        dl = ["| # | 질문 | 관련 Thesis | 결정 시점 |", "|---|---|---|---|"]
        for d in open_d:
            dl.append(f"| {d['id']} | {d['question']} | {' '.join('[['+p+']]' for p in d['pf'])} | {d['due']} |")
        for d in open_d:
            dl += ["", f"### {d['id']} · {d['question']}", "",
                   f"**왜 중요한가.** {d['why']}", "", "**선택지**", ""]
            dl += [f"- {o}" for o in d.get("options", [])]
            dl += ["", "**답을 바꿀 신호**", ""]
            dl += [f"- {o}" for o in d.get("watch_signals", [])]
            dl += ["", f"**지금까지의 근거** {' '.join('[['+s+']]' for s in d.get('evidence', []))}  ",
                   f"**결정 주체** {d['owner']} · **시점** {d['due']}"]
        text = replace_block(text, "DECISIONS", "\n".join(dl)) or text

        # LATEST
        if digests:
            dg = digests[0]
            m = re.search(r"## 이번 회차 핵심 3가지\n(.*?)(?=\n## |\Z)", dg["markdown"], re.S)
            tm = re.search(r"^# (.+)$", dg["markdown"], re.M)
            lt = [f"**{tm.group(1) if tm else dg['date']}**", "", (m.group(1).strip() if m else ""), "",
                  f"전문은 다이제스트 탭(`{dg['path']}`)에서 볼 수 있다."]
            text = replace_block(text, "LATEST", "\n".join(lt)) or text
        port.write_text(text, encoding="utf-8")
        rows = ["| PF | Thesis | 총점 | 변화 | 사분면 | X | Y | 신호 (강화/약화) | 확신도 |",
                "|---|---|:-:|:-:|---|:-:|:-:|:-:|:-:|"]
        order = sorted(calc, key=lambda k: -calc[k]["current"]["total"])
        for pf in order:
            c = calc[pf]
            t = thesis[pf]
            mine = [s for s in signals if pf in s["pf"]]
            pos = sum(1 for s in mine if s["direction"] == "+")
            neg = sum(1 for s in mine if s["direction"] == "-")
            q = c["current"]["quadrant"] + (" ⚠" if c["current"]["quadrant"] != c["baseline"]["quadrant"] else "")
            rows.append(f"| [[{pf}]] | {t['name']} ({t['name_ko']}) | **{fmt(c['current']['total'])}** | "
                        f"{delta_str(c['current']['total'] - c['baseline']['total'])} | {q} | "
                        f"{fmt(c['current']['x'])} | {fmt(c['current']['y'])} | {pos} / {neg} | {t['conviction']} |")
        r = replace_block(text, "PORTFOLIO", "\n".join(rows))
        if r is None:
            errors.append("Portfolio.md: AUTO:PORTFOLIO 블록 없음")
        else:
            if r != text:
                port.write_text(r, encoding="utf-8")
            wiki_md["Portfolio"] = r

    # index notes (for portal reader)
    for p in sorted((ROOT / "indices").glob("*.md")):
        meta, _, text = read_note(p)
        wiki_md[meta["name"]] = text

    # wiki change logs → update feed
    feed = []
    for pf, md in wiki_md.items():
        if not pf.startswith("PF-") and pf != "Portfolio":
            continue
        _, body, _ = read_note(ROOT / "wiki" / f"{pf}.md")
        for line in section(body, "변경 이력").splitlines():
            m = re.match(r"-\s*(\d{4}-\d{2}-\d{2}):\s*(.*)", line.strip())
            if m:
                feed.append({"date": m.group(1), "pf": pf, "text": m.group(2)})
    feed.sort(key=lambda f: f["date"], reverse=True)

    signals.sort(key=lambda s: (s["collected"], s["published"], s["id"]), reverse=True)
    for pf in thesis:
        thesis[pf]["calc"] = calc[pf]
        thesis[pf]["signal_count"] = sum(1 for s in signals if pf in s["pf"])

    data = {
        "generated": date.today().isoformat(),
        "criteria": scores["criteria"],
        "quadrant_rule": scores["quadrant_rule"],
        "baseline_meta": scores["baseline_meta"],
        "thesis": thesis,
        "history": scores["history"],
        "watch": scores["watch"],
        "indices": indices,
        "signals": signals,
        "wiki": wiki_md,
        "digests": digests,
        "decisions": decisions,
        "feed": feed,
    }
    (ROOT / "data" / "signals.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    tpl = ROOT / "dashboard" / "template.html"
    if tpl.exists():
        html = tpl.read_text(encoding="utf-8")
        payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        html = html.replace("/*__DATA__*/null", payload)
        (ROOT / "dashboard" / "dist.html").write_text(html, encoding="utf-8")

    print(f"signals {len(signals)} · thesis {len(thesis)} · history {len(scores['history'])} · watch {len(scores['watch'])}")
    for pf in sorted(calc):
        c = calc[pf]
        print(f"  {pf} {fmt(c['baseline']['total'])} → {fmt(c['current']['total'])}  {c['current']['quadrant']}")
    if errors:
        print("검증 오류:")
        for e in errors:
            print(" -", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

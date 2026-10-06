# FuturePlatform

LG Future Platform Thesis 9개(PF-01~09)를 **살아있는 가설**로 운영하는 LLM-wiki.
국내외 뉴스 레이더가 격주로 신호를 모으면, 위키 문서·스코어·포털이 한 번에 갱신된다.

```
 레이더 수집 ─▶ signals/  (출처 1건 = 노트 1개, tier·criteria·방향·강도)
                   │
                   ▼
            wiki/PF-*.md  (정의·맥락·Evidence·경쟁·반증 조건 — 단일 진실원)
                   │
                   ▼
           data/scores.json  (기준선·현재·변경 이력·관찰 목록)
                   │
                   ▼
     scripts/build_index.py  ─▶ 위키 AUTO 블록 · data/signals.json · dashboard/dist.html(포털)
```

## 폴더

| 경로 | 내용 |
|---|---|
| `wiki/Portfolio.md` | 9개 Thesis 개요, 사분면 표, 공통 패턴, 핵심 논점 |
| `wiki/PF-01.md` ~ `PF-09.md` | Thesis별 LLM-wiki — 정의, 왜 지금인가, LG 비대칭 자산, 스코어, Evidence, 경쟁 지형, 반증 조건, 관찰 지표, Wedge→2030, Sources |
| `indices/` | Korea Futures Lab 수요층 지수 4개 |
| `signals/` | 신호 노트 |
| `digests/` | 회차별 다이제스트 |
| `data/scores.json` | 8대 기준 점수 원장 (기준선 2026-09-13) |
| `dashboard/template.html` | 포털 템플릿 — 빌드가 `dist.html`로 데이터를 주입 |
| `CLAUDE.md` | 정기 실행 지침 (수집·위키 갱신·점수 규칙·빌드·게시) |
| `sources.md` | 소스 목록과 레이더 운영 규칙 |

## 포털

빌드 결과 `dashboard/dist.html`이 Claude 아티팩트로 게시된다. 홈(이번 회차, 포트폴리오 지도, Thesis 카드, 점수 변경·관찰, 최근 신호), 9개 플랫폼 기회 영역 리더, 신호 레이더, 다이제스트로 구성된다.

## Obsidian

저장소를 Vault로 열면 `[[PF-xx]]`, `[[SIG-...]]`, `[[지수명]]` 링크로 신호–Thesis–지수 그래프가 보인다. Obsidian Git 자동 pull을 켜두면 정기 수집 결과가 그대로 들어온다. 위키의 `<!-- AUTO:... -->` 블록은 빌드가 다시 쓰므로 그 안은 편집하지 않는다.

## 로컬 빌드

```bash
python3 scripts/build_index.py
```

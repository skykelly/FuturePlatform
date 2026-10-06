# FuturePlatform 운영 지침

이 저장소는 LG Future Platform Thesis 9개(PF-01~09)를 **살아있는 가설**로 운영하는 LLM-wiki다. 정기 작업이 실행되면 아래 순서를 그대로 따른다. 모든 문서는 한국어로 쓴다.

## 0. 구조와 원칙

| 계층 | 위치 | 역할 | 누가 쓰나 |
|---|---|---|---|
| 신호 | `signals/YYYY-MM/SIG-*.md` | 근거의 최소 단위 (출처 1건 = 노트 1개) | Claude |
| 위키 | `wiki/PF-*.md`, `wiki/Portfolio.md` | Thesis 정의·맥락·근거·경쟁·반증 조건 — **단일 진실원** | Claude (AUTO 블록 제외) |
| 부속 문서 | `wiki/Appendix-A~C.md`, `wiki/study/PF-*-study.md` | 개요 부록(검토 방법·용어·의사결정 사항), Thesis 심층 분석(Template v2 18항목) | Claude (AUTO 블록 제외) |
| 점수 원장 | `data/scores.json` | 기준선·현재 점수, 변경 이력, 관찰 목록 | Claude |
| 결정 질문 | `data/decisions.json` | 답에 따라 Thesis 위치·추진 방식이 바뀌는 질문 | Claude (결정은 사용자) |
| 지수 | `indices/*.md` | Korea Futures Lab 수요층 지수 4개 (정의·해석) | Claude (AUTO 블록 제외) |
| 지표 원장 | `data/indicators.json` | 지수별 관측 변수의 최신값·이전값·출처 | Claude |
| 다이제스트 | `digests/YYYY-MM-DD.md` | 회차별 요약 | Claude |
| 산출물 | `data/signals.json`, `dashboard/dist.html` | 빌드 결과 (직접 수정 금지) | `scripts/build_index.py` |

- 위키의 `<!-- AUTO:... -->` 블록(SCORE·LOG·SOURCES·PORTFOLIO·SNAPSHOT·CHANGES·DECISIONS·LATEST)은 빌드가 다시 쓴다. **손으로 고치지 않는다.** `<!-- VIZ:... -->` 표시는 포털이 그림으로 바꾸는 자리이므로 지우지 않는다.
- 신호 → 위키 → 점수 → 다이제스트 → 빌드 순서가 한 회차의 한 묶음이다. 신호만 쌓고 위키를 안 고치면 회차가 끝난 것이 아니다.

## 1. 맥락 읽기

- `wiki/Portfolio.md`와 `wiki/PF-*.md` 전체 (특히 frontmatter `radar_ko`·`radar_en`, 섹션 7 반증 조건, 섹션 8 관찰 지표)
- `data/scores.json`의 `watch` 목록
- 최근 다이제스트 2개의 "다음 회차 관찰 포인트"
- `data/signals.json`의 기존 URL (중복 방지)
- `sources.md`의 소스 목록

## 2. 국내외 뉴스 레이더 (웹 검색 25~35회)

기간은 직전 실행 이후(기본 최근 14일). 쿼리에 연·월을 넣는다.

1. **Thesis 레이더** — PF별로 `radar_ko`에서 1회, `radar_en`에서 1회 (총 18회 내외). 확신도 "상승·하락" Thesis와 Strategic Core는 1회 더.
2. **글로벌 리서치 스윕** — 컨설팅(McKinsey·BCG·Bain·Deloitte·Accenture)과 투자은행(Goldman Sachs·Morgan Stanley·J.P. Morgan·UBS)의 최근 2주 발간물을 주제(agentic commerce, physical AI·robotics, smart home, energy flexibility, aging, circular economy)로 2~4회.
3. **관찰 목록** — `watch` 항목마다 1회. 반대 근거도 함께 찾는다.
4. **반증 조건** — 각 위키 섹션 7의 반증 조건이 실제로 일어났는지 확인하는 쿼리 2~3회.
5. **수요층 지수** — 4개 지수 각 1회 (통계청·정부 발표 우선).
6. **일본 선행 사례** — 일본어 쿼리 2회.
7. 직전 다이제스트의 관찰 포인트는 모두 검색.

검색 결과는 WebFetch로 원문을 확인한다. 접근이 막히면 우회하지 말고 `status: review`로 기록한다.

## 3. 품질 게이트

- **탈락**: 구체적 주장(수치·결정·출시·제도·계약)이 없는 기사, 의견 칼럼만 있는 기사, 기존 URL 중복, 같은 사건의 중복 보도(1차에 가장 가까운 것 하나만), 직전 실행 이전에 이미 다룬 사건
- **review**: 2차 출처만 있음, 원문 확인 불가, PF 연결이 약함
- **accepted**: 나머지
- 회차당 목표 8~15건. 억지로 채우지 않는다. 컨설팅·투자은행 출처가 0건이면 다이제스트에 그 사실을 적는다.

## 4. 신호 노트 작성

- 템플릿 `templates/signal.md`. 파일명 `signals/YYYY-MM/SIG-YYYYMMDD-NN.md` (수집일, NN은 그날 일련번호)
- `tier`: 컨설팅 | 투자은행 | 산업리서치 | 정부·공공 | 글로벌기업 | 언론 — 리포트를 보도한 기사는 원 발행 주체가 아니라 실제 확인한 출처 기준으로 매기고, 원 발행 주체는 `source`에 괄호로 적는다
- `criteria`: 영향을 주는 8대 기준 키 — tam, value, rtw, network, moat, monetize, execution, differentiation
- `direction`: Thesis를 강화 "+", 약화 "-", 9개에 없는 새 기회 "new"
- `strength`: 1 참고 · 2 근거 · 3 판단을 바꿀 만한 근거
- 요지는 **반드시 자기 말로 요약**. 원문 문장을 옮기지 않는다. 인용은 꼭 필요할 때 15단어 미만 1회.
- Thesis 연결에는 경쟁 주체가 Control Point를 먼저 가져가는 **약화 측면**도 적는다.

## 5. 위키 갱신 (LLM-wiki 유지)

이번 회차 신호가 연결된 PF마다:

1. **섹션 5 Evidence** — 강화/약화 목록 맨 위에 새 근거를 한 줄씩 추가 (`설명 — [[SIG-...]]`). 같은 내용의 기존 줄이 있으면 신호 링크만 덧붙인다.
2. **섹션 2 왜 지금인가** — 구조적으로 새로운 사실일 때만 문단을 고친다. 단순 추가 사례는 Evidence에만 둔다.
3. **섹션 6 경쟁 지형** — 새 경쟁 주체나 자리 이동이 있으면 표를 고친다.
4. **섹션 7 반증 조건** — 반증 조건이 충족되거나 가까워지면 그 줄에 `(2026-MM-DD 근접: [[SIG-...]])`를 붙이고 다이제스트 맨 위에 올린다.
5. **섹션 4 해석** — 점수가 바뀌었거나 관찰이 추가·해제되면 해석 문단을 다시 쓴다.
6. **frontmatter** — `updated`를 오늘로, `conviction`을 최근 2회차 순방향(강화 strength 합 − 약화 strength 합)으로: +3 이상 "상승", −3 이하 "하락", 그 사이 "유지".
7. **변경 이력** — 맨 아래에 `- YYYY-MM-DD: 신호 N건(강화 a·약화 b). 점수 변경 … / 관찰 …` 한 줄. 포털의 업데이트 피드가 이 줄을 읽는다.
8. **심층 분석 문서** — `wiki/study/PF-*-study.md`가 있는 Thesis는 점수·사분면이 바뀌었을 때만 관련 항목을 고친다.

### 개요 페이지(`wiki/Portfolio.md`) — 공유용 랜딩 페이지

포털의 첫 화면이며 처음 보는 사람이 읽는 문서다. 장마다 갱신 권한이 다르다.

| 장 | 내용 | 정기 실행에서 |
|---|---|---|
| 요약, 1장, 2장, 부록 A·B | 요약, 검토 배경, 9개 기회, 검토 방법(`wiki/Appendix-A.md`), 용어(`wiki/Appendix-B.md`) | **고치지 않는다.** 사용자가 대화에서 승인한 경우에만 수정 |
| 3장 | 평가 기준과 점수 | 서술은 고치지 않는다. 표·지도는 빌드가 자동 갱신 |
| 4장 | 9월 평가 이후 변화 | 표는 자동. "주요 시사점"은 여러 기회에 걸친 새 패턴이 확인될 때 고치거나 추가 |
| 5장 | 수요 환경 | 지수 추세가 바뀌면 표의 "현재 추세" 칸을 갱신 |
| 6장 | 최근 점검 결과 | 자동 (최신 다이제스트의 핵심 3가지) |
| 부록 C | 의사결정 사항 (`wiki/Appendix-C.md`, 대기·완료) | `data/decisions.json`을 고치면 빌드가 자동 반영. 새 결정 질문은 여기서 관리 |

이 페이지는 경영진 보고 자료다. 문장은 짧은 보고체("~습니다", 개조식은 명사형)로 쓰고, 줄표(—)로 문장을 잇지 않으며, 비유·수사·과장 표현을 쓰지 않는다. 약어와 내부 용어는 처음 나올 때 풀어 쓴다. 다이제스트의 "이번 회차 핵심 3가지"도 이 페이지에 그대로 실리므로 같은 문체로 쓴다.


### 결정이 필요한 질문 (`data/decisions.json` → 부록 C)

"답에 따라 Thesis의 위치나 추진 방식이 바뀌는 질문"을 관리한다. 항목: `id, pf, question, why, options, watch_signals, evidence, owner, due, status(open|closed)`.
- 매 회차, 새 신호가 `watch_signals`에 해당하면 그 신호 ID를 `evidence`에 추가하고, 필요하면 `why`를 현재 상황에 맞게 고친다.
- 관찰 목록이나 반증 조건에서 "한 가지 판단이 사분면·추진 방식을 바꾸는" 상황이 새로 생기면 질문을 추가한다. 질문은 예/아니오 또는 A/B로 답할 수 있는 형태로 쓴다.
- 사용자가 결정을 알려주면 `status`를 `closed`로 바꾸고 `decision` 필드에 결정 내용과 날짜를 적는다. 닫힌 질문은 개요에 표시되지 않는다.

### 수요층 지수와 지표 원장 (`data/indicators.json`)

지수 노트의 관측 데이터 표는 `data/indicators.json`에서 자동 생성된다(`<!-- AUTO:INDICATORS -->`).
- 새 공식 통계가 나오면 해당 항목의 `value`·`as_of`를 갱신하고, 기존 값을 `prev_value`·`prev_as_of`로 옮긴다. 새 변수는 항목을 추가한다 (`index, label, value, unit, as_of, prev_value, prev_as_of, raises_index_when(up|down), source, url, cadence, note`).
- 이전값은 원문에 나온 값이나 원문의 증감으로 계산한 값만 쓴다. 기억이나 추정으로 채우지 않는다. 없으면 `null`.
- 값이 바뀐 지수는 노트의 "지금 읽히는 방향"을 다시 쓰고, 변경 이력에 한 줄 남긴다. "아직 비어 있는 변수"를 채웠으면 그 줄을 지운다.
- 주요 발표 시기: 고령자 통계(9~10월), 인구주택총조사(7월), 맞벌이 가구 통계(6월), 주거실태조사(연말), 생활시간조사(5년 주기, 다음 2029년). 해당 월의 회차에는 이 발표를 우선 검색한다.
- 지수 통계가 특정 Thesis의 TAM·고객가치 판단을 바꿀 만하면 신호 노트로도 기록한다.

## 6. 점수 갱신 규칙 (`data/scores.json`)

- **기준선(baseline)은 절대 바꾸지 않는다.** 바꾸는 것은 `current`, `history`, `watch`뿐이다.
- 변경 단위 0.5, 회차당 기준별 최대 ±0.5. 범위 1.0~5.0.
- 변경 조건: 같은 방향의 strength 2 이상 신호가 **서로 다른 출처에서 2건 이상**, 또는 strength 3 신호 1건.
- 같은 기준에 반대 방향 근거(strength 2 이상)가 있으면 바꾸지 않고 `watch`에 올린다 (`signals`, `counter`, `note`).
- `watch` 항목은 매 회차 재검토한다: 같은 방향 근거가 추가로 쌓여 변경 조건을 넘으면 점수를 바꾸고 `watch`에서 지운다. 반대 근거가 우세해지면 지우고 위키 변경 이력에 "관찰 해제"로 남긴다.
- 모든 변경은 `history`에 `date, pf, criterion, from, to, signals, rationale`로 남긴다. rationale은 왜 그 기준이 움직였는지 한두 문장.
- 사분면은 빌드가 자동 계산한다 (X = 독점우위 + 실행 용이성, Y = 네트워크 + TAM, 각 8.0 이상이 High). 사분면이 바뀌면 다이제스트 맨 위에 쓴다.

## 7. 다이제스트

`digests/YYYY-MM-DD.md` — frontmatter `date`, `kind`(regular | monthly | quarterly), `title`. 본문은 2026-10-06 형식을 따른다:
제목(`# 다이제스트 날짜 · 한 줄 요약`) → 개요 문단 → `## 이번 회차 핵심 3가지`(번호 목록, 각 항목은 `**굵은 제목.** 설명`) → `## 점수 변경` 표 → `## 관찰 등록·해제` → `## 검토 대기` → `## 다음 회차 관찰 포인트`.
- **월 첫 실행**: `## 월간 롤업` — 지난달 PF별 신호 수·방향 합계, 확신도 변화
- **분기 첫 실행(1·4·7·10월)**: `## 2x2 재배치 검토` — 사분면 경계(8.0)에 가까운 Thesis와 이동 조건

## 8. 빌드·검증·커밋

```bash
python3 scripts/build_index.py   # 오류가 나면 노트·위키·점수를 고치고 다시 실행
git add -A && git commit -m "radar: YYYY-MM-DD 신호 N건, 점수 변경 M건" && git push origin main
```

## 9. 포털 갱신

`dashboard/dist.html`을 Artifact 도구로 아래 URL에 다시 게시한다 (같은 URL 유지, icon 생략). 다른 세션에서는 먼저 `action: "read"`로 읽은 뒤 게시한다.
- Portal URL: https://claude.ai/artifact/Ms1tRpckbYjRzBc1kLAPNW

## 10. 보고

사용자에게 한국어 한 문단: 신호 수(채택/검토, 컨설팅·IB 건수), 점수 변경·사분면 이동, 관찰 등록·해제, 이번 회차 핵심 3가지 제목, 다이제스트 경로.

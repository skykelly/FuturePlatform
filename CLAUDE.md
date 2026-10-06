# 정기 수집 실행 지침

이 저장소는 Platform Thesis(PF-01~09)와 Korea Futures Lab 수요 지수 4개를 추적하는 신호 저장소다. 정기 작업이 실행되면 아래 순서를 그대로 따른다. 모든 노트는 한국어로 쓴다.

## 1. 맥락 읽기
- `thesis/*.md`, `indices/*.md`, `sources.md`
- 최근 다이제스트 2개(`digests/`)의 "다음 회차 관찰 포인트"
- `data/signals.json`의 기존 URL 목록 (중복 방지)

## 2. 수집 (웹 검색 15~25회)
- 기간: 직전 실행 이후(기본 최근 14일). 날짜를 쿼리에 넣는다.
- 가중치: `weight: high` PF(04·05·06·07)는 각 2회 이상, medium은 1회 이상, low는 키워드 1회.
- 지수 4개는 각 1회 이상, 통계청·정부 발표 우선.
- 일본 선행 사례 검색 2회 이상(일본어 쿼리 허용).
- 직전 다이제스트의 관찰 포인트는 반드시 검색.
- 검색 결과 상세는 WebFetch로 확인. 접근이 막히면 우회하지 말고 `status: review`로 기록.

## 3. 품질 게이트
- **탈락**: 구체적 주장(수치·결정·출시·제도·계약)이 하나도 없는 기사, 의견·전망 칼럼만 있는 기사, 기존 URL 중복, 같은 사건의 중복 보도(가장 1차에 가까운 것 하나만)
- **review**: 2차 출처만 있음, 원문 확인 불가, PF 연결이 약함
- **accepted**: 나머지
- 회차당 목표 6~12건. 억지로 채우지 않는다.

## 4. 노트 작성
- 템플릿: `templates/signal.md`. 파일: `signals/YYYY-MM/SIG-YYYYMMDD-NN.md` (YYYYMMDD = 수집일)
- `pf`, `index`는 thesis/indices에 있는 ID·이름만 사용
- direction: Thesis를 강화하면 "+", 약화하면 "-", 기존 9개에 없는 새 기회면 "new"
- strength: 1=참고, 2=근거, 3=판단을 바꿀 만한 근거
- 요지는 **반드시 자기 말로 요약**. 원문 문장을 옮기지 않는다. 인용이 꼭 필요하면 15단어 미만 1회.
- Thesis 연결에는 경쟁 주체가 Control Point를 먼저 가져가는 "약화 측면"도 적는다.

## 5. 다이제스트
`digests/YYYY-MM-DD.md` — 핵심 3가지, PF별 표, 8대 기준 영향, 검토 대기, 다음 관찰 포인트. 2026-10-06 다이제스트 형식을 따른다.
- **월 첫 실행**: "월간 롤업" 섹션 추가 — 지난달 PF별 신호 수·방향 합계, 8대 기준 점수를 움직일 근거 정리
- **분기 첫 실행(1·4·7·10월)**: "2x2 재배치 검토" 섹션 추가 — 사분면 이동 후보와 근거

## 6. 빌드·검증·커밋
```bash
python3 scripts/build_index.py   # 오류가 나면 노트를 고치고 다시 실행
git add -A && git commit -m "signals: YYYY-MM-DD 수집 N건" && git push origin main
```

## 7. 대시보드 갱신
`dashboard/dist.html`을 Artifact 도구로 아래 URL에 다시 게시한다(같은 URL 유지).
- Dashboard URL: https://claude.ai/artifact/Ms1tRpckbYjRzBc1kLAPNW
- Artifact 호출: `file_path=dashboard/dist.html`, `url=<위 URL>` (icon은 생략). 다른 세션에서는 먼저 `action: "read"`로 읽은 뒤 게시한다.

## 8. 알림
실행 결과를 사용자에게 한 문단으로 보낸다: 수집 건수, 이번 회차 핵심 3가지 제목, 다이제스트 경로.

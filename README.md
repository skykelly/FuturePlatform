# FuturePlatform Signal Tracker

미래 소비자 변화(Korea Futures Lab)와 LG Future Platform Thesis(PF-01~09)를 **살아있는 가설**로 관리하기 위한 신호 저장소입니다.

- 신호 하나 = 마크다운 노트 하나 (`signals/YYYY-MM/`)
- 노트는 `[[PF-xx]]`, `[[지수명]]` 링크로 Thesis·지수 노트와 연결 → Obsidian 그래프 뷰가 곧 **신호–지수–Thesis 온톨로지**
- `scripts/build_index.py`가 노트를 읽어 `data/signals.json`과 대시보드(`dashboard/dist.html`)를 생성
- 격주 화요일 정기 작업이 수집 → 노트 작성 → 다이제스트 → 인덱스 빌드 → 커밋 → 대시보드 갱신

## 폴더 구조

```
thesis/      PF-01~09 Thesis 노트 (Control Point, 관찰 키워드, 강화·약화 신호 기준)
indices/     Korea Futures Lab 잠재 지수 4개 (시간빈곤·공간제약·가사외주화·돌봄부담)
signals/     신호 노트 (월별 폴더)
digests/     격주 다이제스트, 월간 롤업, 분기 2x2 검토
templates/   신호 노트 템플릿
data/        signals.json (빌드 산출물)
dashboard/   대시보드 템플릿과 빌드 결과
scripts/     인덱스·대시보드 빌드 스크립트
sources.md   수집 소스 목록
CLAUDE.md    정기 수집 실행 지침
```

## Obsidian에서 쓰기

1. 이 저장소를 로컬에 clone한 뒤 Obsidian에서 폴더를 Vault로 엽니다.
2. Obsidian Git 플러그인으로 주기적 pull을 설정하면 새 신호가 자동으로 들어옵니다.
3. 그래프 뷰에서 `path:thesis OR path:indices`를 그룹 색으로 지정하면 허브 구조가 잘 보입니다.

## 로컬 빌드

```bash
python3 scripts/build_index.py
```

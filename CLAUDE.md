# 고객 뉴스 프로젝트

## 월간 뉴스 요약 요청 처리 방법

사용자가 특정 인물의 "한달치 뉴스", "월간 요약", "지난달 뉴스" 등을 요청하면:

1. **뉴스 수집** — 해당 인물의 이름(과 특징)을 확인하고 아래 명령 실행:
   ```bash
   cd "C:\Users\michelle\projects\고객 뉴스"
   python monthly_news.py "이름" "특징(선택)"
   ```

2. **monthly_raw.json 읽기** — 수집된 기사 목록 확인

3. **요약 작성** — 다음 형식으로 한국어 요약 제공:
   - 기간: 최근 30일
   - 주요 이슈/사건 흐름 (시간순)
   - 반복 등장하는 키워드/테마
   - 긍정적 뉴스 / 부정적 뉴스 구분
   - 전체 총평 1~2문장

## 인물 목록 (통합 문서1.xlsx)
- 이하늬 — 배우
- 이혜영 — 인플루언서
- 권오경 — 한양대교수 SDI사외이사
- 김병주 — MBK파트너스
- 서정진 — 셀트리온
- 정정이 — 현대해상
- 송창현 — 42dot

## 일간 자동 뉴스
- 매일 아침 9시 KST 자동 실행
- 결과: https://michelleyoo94-crypto.github.io/peopledetail/
- 루틴: https://claude.ai/code/routines/trig_01JjU5h5jg7L7eb8FqJTtscL

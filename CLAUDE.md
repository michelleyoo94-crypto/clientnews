# 고객 뉴스 프로젝트

## 월간 뉴스 요약 요청 처리 방법

사용자가 "한달치 뉴스", "월간 요약", "지난달 뉴스" 등을 요청하면 **엑셀의 모든 인물**을 대상으로 처리:

1. **전체 뉴스 수집**:
   ```bash
   cd "C:\Users\michelle\projects\고객 뉴스"
   python monthly_all.py
   ```

2. **monthly_raw_all.json 읽기** — 각 인물별 수집된 기사 목록 확인

3. **인물별 요약 작성** (한국어):
   - 기간: 최근 30일
   - 주요 이슈/사건 흐름 (시간순 bullet points)
   - 반복 키워드/테마
   - 긍정/부정 구분
   - 전체 총평 1~2문장
   - 기사 없으면 "이번 달 특이사항 없음"

4. **monthly.html 생성** — monthly_all.py의 build_monthly_html() 호출:
   ```python
   # monthly_raw_all.json의 각 person에 summary 채운 뒤:
   from monthly_all import build_monthly_html
   import json
   from pathlib import Path
   data = json.load(open("monthly_raw_all.json", encoding="utf-8"))
   # data["people"] 각 항목에 summary 필드 채우기
   html = build_monthly_html(data["date_range"], data["people"])
   Path("docs/monthly.html").write_text(html, encoding="utf-8")
   ```

5. **GitHub 푸시**:
   ```bash
   git add docs/monthly.html monthly_raw_all.json
   git commit -m "월간 뉴스 요약 업데이트"
   git push
   ```

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

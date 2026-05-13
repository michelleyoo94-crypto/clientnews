import json
from pathlib import Path
from datetime import datetime

with open("raw_news.json", encoding="utf-8") as f:
    data = json.load(f)

# Claude가 기사를 직접 읽고 작성한 요약
summaries = {
    "이하늬": (
        "• [주의] 미등록 기획사 운영 혐의로 이하늬 및 남편이 경찰에 의해 검찰 송치\n"
        "• 드라마 '애마' 공동 출연 신인 방효린이 제62회 백상예술대상 여자 신인 연기상 수상, "
        "수상 소감에서 이하늬를 롤모델로 언급하며 긍정 이미지도 공존\n"
        "• 법적 이슈와 긍정 이미지가 동시에 부각되는 상황 — 검찰 수사 결과 주시 필요"
    ),
    "이혜영": (
        "• 결혼 14주년 기념 SNS 게시물 업로드, 남편 얼굴 공개 및 일상 공유로 긍정 반응\n"
        "• '이 바닥에 얼씬도 하지 마' 제목 기사에서 이혜영·탁재훈 관련 내용 언급 (구체적 내용 확인 필요)\n"
        "• 양정원 씨 관련 인플루언서 사기·향응 의혹 기사는 동명이인으로 본인과 무관"
    ),
    "권오경": (
        "• 삼성SDI 사외이사진 전원 교체 단행 — 권오경 포함 기존 사외이사 교체, 이미경 신규 선임\n"
        "• 삼성SDI·삼성SDS, '선임 사외이사제' 전격 도입 (이사회 독립성 강화 조치)\n"
        "• SDI 사외이사직 종료로 보임 — 향후 행보 주시 필요"
    ),
    "김병주": (
        "• 홈플러스 사태 구속영장 기각 — 법원이 영장 청구 기각\n"
        "• 검찰, 수사 재시동 — 신영증권 관계자 조사 진행 중 (단독)\n"
        "• 미국에서 300억원대 초고가 별장 실소유 의혹 제기\n"
        "• 자택 담보로 홈플러스에 1,000억 단독 수혈한 사실 단독 보도 (긍정/부정 해석 엇갈림)\n"
        "• 총평: 구속 위기는 넘겼으나 수사 지속 + 재산 의혹 등 리스크 상존"
    ),
    "서정진": (
        "• 짐펜트라(크론병 치료제) 미국 시장 성장 궤도 진입 — 서정진의 뚝심 통했다는 평가\n"
        "• 프랑스 헬스케어 기업 인수 완료 — 현지 약국·병원 영업망 확보로 유럽 거점 마련\n"
        "• 다우존스 지속가능경영(DJSI) 월드 지수 2년 연속 편입 (ESG 우수 기업 인정)\n"
        "• 창업 공신 세대 교체 단행, 형제경영 체제 강화 움직임\n"
        "• 총평: 사업 성과와 글로벌 확장 긍정적, 오너 일가 지배구조 변화 주시"
    ),
    "정정이": (
        "• 현대하임자산운용 대표직 연임 확정 (단독 보도) — 자산운용 부문 경영 입지 공고화\n"
        "• 현대하임, 예술인센터 인수 추진 중으로 사업 다각화 행보\n"
        "• 부친 정몽윤 회장 지분 추가 매입으로 현대해상 지분율 23.97%로 상승\n"
        "• 남매 정경선 부사장은 실적 반토막 논란으로 별도 이슈 존재 (정정이 본인과 무관)"
    ),
    "송창현": (
        "• 현대차 자율주행 사령탑·42dot 사장 전격 사임\n"
        "• 수천억원 규모 보상 수령 후 퇴진, 후임자 물색 난항 예상\n"
        "• '성과 없고 불만만' — 42dot이 현대차 자율주행 발목 잡았다는 비판적 평가 다수\n"
        "• 총평: 현대차 SDV 독자 노선 사실상 폐기 수순, 자율주행 전략 전면 재검토 예상"
    ),
}

today = datetime.now().strftime("%Y년 %m월 %d일")

cards_html = ""
for person in data["people"]:
    name = person["name"]
    desc = person["description"]
    articles = []
    for src, arts in person["sources"].items():
        for a in arts:
            articles.append({"title": a["title"], "link": a["link"], "source": src})

    summary = summaries.get(name, "• 오늘 특이사항 없음")
    count = len(articles)

    articles_html = ""
    for a in articles[:8]:
        src_label = {"google_news": "구글", "naver_news": "네이버", "dcinside": "DC"}.get(a["source"], a["source"])
        articles_html += f'<li><a href="{a["link"]}" target="_blank">{a["title"]}</a><span class="src-tag">{src_label}</span></li>'

    count_badge = f'<span class="count-badge">{count}건</span>' if count > 0 else '<span class="count-badge zero">0건</span>'
    article_section = f'<details><summary>원문 기사 보기 ({count}건)</summary><ul class="article-list">{articles_html}</ul></details>' if articles else ""

    cards_html += f"""
    <div class="card">
        <div class="name-row">
            <h2>{name}</h2>
            <span class="role">{desc}</span>
            {count_badge}
        </div>
        <div class="summary">{summary}</div>
        {article_section}
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>고객 일간 뉴스 — {today}</title>
<style>
  :root {{ --primary: #1a1a2e; --accent: #4f8ef7; --bg: #f0f2f8; --text: #1a1a2e; --muted: #888; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text); }}
  header {{ background: var(--primary); color: #fff; padding: 28px 36px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }}
  .header-left h1 {{ font-size: 1.6rem; font-weight: 800; }}
  .header-left p {{ font-size: 0.85rem; opacity: 0.55; margin-top: 4px; }}
  .nav {{ display: flex; gap: 8px; }}
  .nav a {{ background: rgba(255,255,255,0.12); color: #fff; border: none; padding: 8px 18px; border-radius: 20px; font-size: 0.83rem; text-decoration: none; }}
  .nav a.active, .nav a:hover {{ background: var(--accent); }}
  .container {{ max-width: 960px; margin: 32px auto; padding: 0 20px; display: flex; flex-direction: column; gap: 14px; }}
  .card {{ background: #fff; border-radius: 14px; padding: 22px 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); border-left: 4px solid var(--accent); }}
  .name-row {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }}
  .name-row h2 {{ font-size: 1.1rem; font-weight: 700; }}
  .role {{ background: #eef2ff; color: #4f6ef7; font-size: 0.76rem; padding: 3px 11px; border-radius: 20px; }}
  .count-badge {{ background: #fff0f0; color: #e53935; font-size: 0.76rem; padding: 3px 10px; border-radius: 20px; margin-left: auto; }}
  .count-badge.zero {{ background: #f5f5f5; color: #bbb; }}
  .summary {{ font-size: 0.92rem; line-height: 1.95; color: #2c2c2c; white-space: pre-wrap; }}
  details {{ margin-top: 14px; border-top: 1px solid #eee; padding-top: 10px; }}
  details summary {{ cursor: pointer; font-size: 0.82rem; color: var(--muted); list-style: none; }}
  details summary::-webkit-details-marker {{ display: none; }}
  details summary::before {{ content: "▶  "; font-size: 0.68rem; }}
  details[open] summary::before {{ content: "▼  "; }}
  .article-list {{ margin-top: 10px; list-style: none; display: flex; flex-direction: column; gap: 7px; }}
  .article-list li {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; font-size: 0.83rem; }}
  .article-list a {{ color: var(--accent); text-decoration: none; flex: 1; line-height: 1.5; }}
  .article-list a:hover {{ text-decoration: underline; }}
  .src-tag {{ background: #f0f4ff; color: #7c9ef7; font-size: 0.7rem; padding: 2px 7px; border-radius: 10px; white-space: nowrap; }}
  footer {{ text-align: center; padding: 36px; color: var(--muted); font-size: 0.78rem; }}
</style>
</head>
<body>
<header>
  <div class="header-left">
    <h1>고객 일간 뉴스</h1>
    <p>{today} · Claude Code 요약</p>
  </div>
  <nav class="nav">
    <a class="active" href="index.html">일간</a>
    <a href="monthly.html">월간 요약</a>
  </nav>
</header>
<div class="container">
{cards_html}
</div>
<footer>매일 아침 9시 자동 업데이트 · Claude Code</footer>
</body>
</html>"""

Path("docs/index.html").write_text(html, encoding="utf-8")
print("docs/index.html 생성 완료")

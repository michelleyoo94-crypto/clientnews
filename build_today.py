import json
from pathlib import Path
from datetime import datetime

with open("raw_news.json", encoding="utf-8") as f:
    data = json.load(f)

summaries = {
    "이하늬": "• 드라마 '애마' 공동 출연 신인 배우 방효린이 제62회 백상예술대상 여자 신인 연기상 수상, 수상 소감에서 \"이하늬를 통해 훌륭한 배우가 무엇인지 배웠다\"고 공개 언급\n• 직접적인 단독 뉴스는 없으나 후배 배우들 사이에서 롤모델로 꾸준히 회자되는 긍정적 이미지 확인",
    "이혜영": "• 인플루언서 관련 검색 결과 동명이인(양정원 씨 관련 사기·향응 의혹 사건) 기사 혼선 가능성\n• 검찰이 해당 사건에서 현직 경찰관에 구속영장 청구, 사건 은폐 여부 수사 중\n• 본인 직접 연루 기사인지 추가 확인 권장",
    "권오경": "• 오늘 특이사항 없음",
    "김병주": "• 홈플러스 사태 관련 검찰 수사 재시동 — 신영증권 관계자 조사 진행 중 (단독 보도)\n• 김병주 회장, \"당국이 위법 행위 없다고 확인했다\"고 공개 발언 → 여론 역풍 지속\n• MBK파트너스, 일본 알루미늄 캔 업계 3위 기업 인수 추진 (해외 딜 확장 행보)",
    "서정진": "• 짐펜트라(크론병 치료제) 미국 처방 1분기 185% 급증, 분기 기준 최대 기록 달성\n• 프랑스 114년 역사 약국 체인 지프레(9,000개 약국) 인수 완료 — 유럽 유통망 대폭 강화\n• 다우존스 지속가능경영(ESG) 월드 지수 2년 연속 편입\n• 2세 경영 한계로 서정진 회장 직접 재등판, 형제경영 체제 강화 중\n• 혼외자 분쟁 및 친인척 계열사 편입 논란 지속 / 한국 부자 3위, 총자산 12조원",
    "정정이": "• 정몽윤 현대해상 회장의 장녀로, 현대하임자산운용 대표직 연임 확정 (단독 보도)\n• 그룹 내 경영 승계 구도에서 자산운용 부문 입지를 안정적으로 유지",
    "송창현": "• 오늘 특이사항 없음",
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

    articles_html = ""
    for a in articles[:8]:
        src_label = {"google_news": "구글", "naver_news": "네이버", "dcinside": "DC"}.get(a["source"], a["source"])
        articles_html += f'<li><a href="{a["link"]}" target="_blank">{a["title"]}</a><span class="src-tag">{src_label}</span></li>'

    count = len(articles)
    count_badge = f'<span class="count-badge">{count}건</span>' if count > 0 else '<span class="count-badge zero">0건</span>'

    cards_html += f"""
    <div class="card">
        <div class="card-top">
            <div class="name-row">
                <h2>{name}</h2>
                <span class="role">{desc}</span>
                {count_badge}
            </div>
        </div>
        <div class="summary">{summary}</div>
        {"" if not articles else f'''<details><summary>원문 기사 보기 ({count}건)</summary><ul class="article-list">{articles_html}</ul></details>'''}
    </div>"""

html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>고객 일간 뉴스 — {today}</title>
<style>
  :root {{ --primary: #1a1a2e; --accent: #4f8ef7; --bg: #f0f2f8; --card: #fff; --text: #1a1a2e; --muted: #888; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }}
  header {{ background: var(--primary); color: #fff; padding: 32px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }}
  .header-left h1 {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }}
  .header-left p {{ font-size: 0.88rem; opacity: 0.6; margin-top: 4px; }}
  .header-right {{ display: flex; gap: 10px; }}
  .nav-btn {{ background: rgba(255,255,255,0.12); color: #fff; border: none; padding: 8px 18px; border-radius: 20px; font-size: 0.85rem; cursor: pointer; text-decoration: none; transition: background 0.2s; }}
  .nav-btn:hover, .nav-btn.active {{ background: var(--accent); }}
  .container {{ max-width: 960px; margin: 36px auto; padding: 0 20px; display: flex; flex-direction: column; gap: 16px; }}
  .card {{ background: var(--card); border-radius: 16px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-left: 4px solid var(--accent); transition: box-shadow 0.2s; }}
  .card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
  .card-top {{ margin-bottom: 14px; }}
  .name-row {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
  .name-row h2 {{ font-size: 1.15rem; font-weight: 700; }}
  .role {{ background: #eef2ff; color: #4f6ef7; font-size: 0.78rem; padding: 3px 12px; border-radius: 20px; }}
  .count-badge {{ background: #fff0f0; color: #e53935; font-size: 0.78rem; padding: 3px 10px; border-radius: 20px; margin-left: auto; }}
  .count-badge.zero {{ background: #f5f5f5; color: #aaa; }}
  .summary {{ font-size: 0.93rem; line-height: 1.9; color: #333; white-space: pre-wrap; }}
  details {{ margin-top: 16px; border-top: 1px solid #eee; padding-top: 12px; }}
  details summary {{ cursor: pointer; font-size: 0.83rem; color: var(--muted); list-style: none; }}
  details summary::before {{ content: "▶ "; font-size: 0.7rem; }}
  details[open] summary::before {{ content: "▼ "; }}
  .article-list {{ margin-top: 10px; list-style: none; display: flex; flex-direction: column; gap: 8px; }}
  .article-list li {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; font-size: 0.85rem; }}
  .article-list a {{ color: var(--accent); text-decoration: none; flex: 1; line-height: 1.5; }}
  .article-list a:hover {{ text-decoration: underline; }}
  .src-tag {{ background: #f0f4ff; color: #7c9ef7; font-size: 0.72rem; padding: 2px 8px; border-radius: 10px; white-space: nowrap; }}
  footer {{ text-align: center; padding: 40px; color: var(--muted); font-size: 0.8rem; }}
</style>
</head>
<body>
<header>
  <div class="header-left">
    <h1>고객 일간 뉴스</h1>
    <p>{today} 기준 수집</p>
  </div>
  <div class="header-right">
    <a class="nav-btn active" href="index.html">일간</a>
    <a class="nav-btn" href="monthly.html">월간 요약</a>
  </div>
</header>
<div class="container">
{cards_html}
</div>
<footer>매일 아침 9시 자동 업데이트 · Claude Code</footer>
</body>
</html>"""

Path("docs/index.html").write_text(html, encoding="utf-8")
print("docs/index.html 생성 완료")

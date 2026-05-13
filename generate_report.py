"""
이 스크립트는 Claude 에이전트가 매일 실행합니다.
raw_news.json을 읽고 요약 후 index.html을 생성합니다.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

def load_raw_news():
    with open("raw_news.json", encoding="utf-8") as f:
        return json.load(f)

def build_html(date_str, summaries):
    cards = ""
    for item in summaries:
        sources_html = ""
        for article in item.get("articles", []):
            sources_html += f"""
            <li>
                <a href="{article['link']}" target="_blank">{article['title']}</a>
                <span class="source">{article.get('source','')}</span>
            </li>"""

        cards += f"""
        <div class="card">
            <div class="card-header">
                <h2>{item['name']}</h2>
                <span class="badge">{item['description']}</span>
            </div>
            <div class="summary">{item['summary']}</div>
            <details>
                <summary>원문 기사 보기 ({len(item.get('articles',[]))}건)</summary>
                <ul class="article-list">{sources_html}</ul>
            </details>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>고객 일간 뉴스 — {date_str}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif; background: #f4f6f9; color: #222; }}
        header {{ background: #1a1a2e; color: white; padding: 24px 32px; }}
        header h1 {{ font-size: 1.5rem; font-weight: 700; }}
        header p {{ font-size: 0.9rem; opacity: 0.7; margin-top: 4px; }}
        .container {{ max-width: 900px; margin: 32px auto; padding: 0 16px; display: flex; flex-direction: column; gap: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }}
        .card-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
        .card-header h2 {{ font-size: 1.2rem; }}
        .badge {{ background: #e8f0fe; color: #1a73e8; font-size: 0.78rem; padding: 3px 10px; border-radius: 20px; white-space: nowrap; }}
        .summary {{ line-height: 1.8; color: #333; white-space: pre-wrap; }}
        details {{ margin-top: 16px; }}
        details summary {{ cursor: pointer; color: #666; font-size: 0.88rem; padding: 8px 0; border-top: 1px solid #eee; }}
        .article-list {{ list-style: none; margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }}
        .article-list li {{ font-size: 0.88rem; display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
        .article-list a {{ color: #1a73e8; text-decoration: none; }}
        .article-list a:hover {{ text-decoration: underline; }}
        .source {{ color: #999; font-size: 0.8rem; white-space: nowrap; }}
        footer {{ text-align: center; color: #aaa; font-size: 0.8rem; padding: 32px; }}
    </style>
</head>
<body>
    <header>
        <h1>고객 일간 뉴스</h1>
        <p>{date_str} 기준 수집</p>
    </header>
    <div class="container">
        {cards}
    </div>
    <footer>매일 자동 생성 — Claude Code</footer>
</body>
</html>"""

def main():
    data = load_raw_news()
    # summaries.json이 있으면 Claude 에이전트가 작성한 요약 사용
    summaries_override = {}
    if Path("summaries.json").exists():
        with open("summaries.json", encoding="utf-8") as f:
            summaries_override = json.load(f)

    summaries = []
    for person in data["people"]:
        all_articles = []
        for src_name, articles in person["sources"].items():
            for a in articles:
                all_articles.append({
                    "title": a["title"],
                    "link": a["link"],
                    "source": src_name,
                    "summary": a.get("summary", "")
                })

        name = person["name"]
        if name in summaries_override:
            summary_text = summaries_override[name]
        else:
            summary_text = "\n".join([f"• {a['title']}" for a in all_articles[:10]]) if all_articles else "수집된 기사 없음"

        summaries.append({
            "name": name,
            "description": person["description"],
            "summary": summary_text,
            "articles": all_articles
        })

    date_str = data.get("generated_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    html = build_html(date_str, summaries)

    output_path = Path("docs/index.html")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"리포트 생성 완료: {output_path.resolve()}")

if __name__ == "__main__":
    main()

"""
엑셀의 모든 인물에 대해 지난 30일 뉴스를 수집하고
docs/monthly.html 을 생성합니다.
Claude Code에서 요약 요청 시 실행됩니다.
"""
import requests
import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from bs4 import BeautifulSoup
from pathlib import Path

EXCEL_PATH = "통합 문서1.xlsx"
OUTPUT_JSON = "monthly_raw_all.json"
DAYS = 30

def load_people():
    df = pd.read_excel(EXCEL_PATH)
    df.columns = ["이름", "특징"]
    df = df.dropna(subset=["이름"])
    df["이름"] = df["이름"].astype(str).str.strip()
    df["특징"] = df["특징"].fillna("").astype(str).str.strip()
    return df.to_dict("records")

def parse_rss(content, since):
    articles = []
    try:
        root = ET.fromstring(content)
        channel = root.find("channel")
        if channel is None:
            return articles
        for item in channel.findall("item")[:30]:
            title = BeautifulSoup(item.findtext("title", ""), "html.parser").get_text()
            link = item.findtext("link", "")
            pub_str = item.findtext("pubDate", "")
            summary = BeautifulSoup(item.findtext("description", ""), "html.parser").get_text()
            pub_date = None
            for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"]:
                try:
                    pub_date = datetime.strptime(pub_str, fmt)
                    if pub_date.tzinfo is None:
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                    break
                except:
                    continue
            if pub_date and pub_date < since:
                continue
            articles.append({"title": title, "link": link, "published": pub_str, "summary": summary})
    except:
        pass
    return articles

def fetch_news(name, description, since):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = quote(f"{name} {description}".strip())
    all_articles = []
    # Google News
    try:
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        resp = requests.get(url, headers=headers, timeout=15)
        all_articles += parse_rss(resp.content, since)
    except:
        pass
    # Naver News
    try:
        url = f"https://search.naver.com/rss?where=news&query={quote(name)}"
        resp = requests.get(url, headers=headers, timeout=10)
        all_articles += parse_rss(resp.content, since)
    except:
        pass
    # 중복 제거
    seen = set()
    unique = []
    for a in all_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)
    return unique

def build_monthly_html(date_range, people_data):
    cards = ""
    for person in people_data:
        articles_html = ""
        for a in person["articles"]:
            articles_html += f"""
            <li>
                <a href="{a['link']}" target="_blank">{a['title']}</a>
                <span class="date">{a.get('published','')[:16]}</span>
            </li>"""

        summary_html = person.get("summary", "요약 생성 중...")

        cards += f"""
        <div class="card">
            <div class="card-header">
                <h2>{person['name']}</h2>
                <span class="badge">{person['description']}</span>
                <span class="count">{len(person['articles'])}건</span>
            </div>
            <div class="summary">{summary_html}</div>
            <details>
                <summary>원문 기사 전체 보기</summary>
                <ul class="article-list">{articles_html}</ul>
            </details>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>고객 월간 뉴스 요약</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Apple SD Gothic Neo', sans-serif; background: #f4f6f9; color: #222; }}
        header {{ background: #0d3b66; color: white; padding: 24px 32px; }}
        header h1 {{ font-size: 1.5rem; font-weight: 700; }}
        header p {{ font-size: 0.9rem; opacity: 0.7; margin-top: 4px; }}
        .nav {{ background: #1a1a2e; padding: 12px 32px; }}
        .nav a {{ color: #aaa; text-decoration: none; font-size: 0.88rem; margin-right: 20px; }}
        .nav a:hover {{ color: white; }}
        .container {{ max-width: 900px; margin: 32px auto; padding: 0 16px; display: flex; flex-direction: column; gap: 20px; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }}
        .card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }}
        .card-header h2 {{ font-size: 1.2rem; }}
        .badge {{ background: #e8f0fe; color: #1a73e8; font-size: 0.78rem; padding: 3px 10px; border-radius: 20px; }}
        .count {{ background: #fce8e6; color: #d93025; font-size: 0.78rem; padding: 3px 10px; border-radius: 20px; margin-left: auto; }}
        .summary {{ line-height: 1.8; color: #333; white-space: pre-wrap; }}
        details {{ margin-top: 16px; }}
        details summary {{ cursor: pointer; color: #666; font-size: 0.88rem; padding: 8px 0; border-top: 1px solid #eee; }}
        .article-list {{ list-style: none; margin-top: 10px; display: flex; flex-direction: column; gap: 8px; }}
        .article-list li {{ font-size: 0.85rem; display: flex; justify-content: space-between; gap: 8px; }}
        .article-list a {{ color: #1a73e8; text-decoration: none; }}
        .article-list a:hover {{ text-decoration: underline; }}
        .date {{ color: #999; font-size: 0.78rem; white-space: nowrap; }}
        footer {{ text-align: center; color: #aaa; font-size: 0.8rem; padding: 32px; }}
    </style>
</head>
<body>
    <header>
        <h1>고객 월간 뉴스 요약</h1>
        <p>수집 기간: {date_range}</p>
    </header>
    <nav class="nav">
        <a href="index.html">일간 뉴스</a>
        <a href="monthly.html">월간 요약</a>
    </nav>
    <div class="container">{cards}</div>
    <footer>Claude Code 생성</footer>
</body>
</html>"""

def main():
    since = datetime.now(timezone.utc) - timedelta(days=DAYS)
    date_range = f"{since.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}"
    people = load_people()
    results = []
    for p in people:
        name, desc = p["이름"], p["특징"]
        print(f"수집 중: {name} ({desc})")
        articles = fetch_news(name, desc, since)
        print(f"  → {len(articles)}건")
        results.append({"name": name, "description": desc, "articles": articles, "summary": ""})

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"date_range": date_range, "people": results}, f, ensure_ascii=False, indent=2)
    print(f"\n수집 완료 → {OUTPUT_JSON}")
    print("Claude가 요약을 작성 후 monthly.html을 생성합니다.")

if __name__ == "__main__":
    main()

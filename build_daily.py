"""
매일 9시 GitHub Actions에서 실행.
Google News RSS로 지난 24시간 뉴스 수집 → docs/index.html 생성.
"""
import json, re, requests, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from pathlib import Path
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime

PEOPLE = [
    ("이하늬",  "배우",               "이하늬 배우"),
    ("이혜영",  "탤런트",             "이혜영 이상민"),
    ("권오경",  "한양대교수 SDI사외이사", "권오경 한양대교수"),
    ("김병주",  "MBK파트너스",        "김병주 MBK파트너스"),
    ("서정진",  "셀트리온",           "서정진 셀트리온"),
    ("정정이",  "현대해상",           "정정이 현대해상"),
    ("송창현",  "42dot",              "송창현 42dot"),
]

KST = timezone(timedelta(hours=9))
NOW_KST = datetime.now(KST)
CUTOFF  = NOW_KST - timedelta(hours=24)

TITLE_FILTERS = {"이하늬", "이혜영"}  # 제목에 이름 포함된 기사만


def fetch_rss(query: str) -> list[dict]:
    q = quote(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        root = ET.fromstring(r.content)
        items = []
        for item in (root.find("channel") or []):
            if item.tag != "item":
                continue
            title   = BeautifulSoup(item.findtext("title",""), "html.parser").get_text()
            link    = item.findtext("link","")
            pub_raw = item.findtext("pubDate","")
            source  = item.findtext("source","")
            try:
                pub_dt = parsedate_to_datetime(pub_raw).astimezone(KST)
            except:
                pub_dt = NOW_KST
            items.append({"title": title, "link": link, "pub_dt": pub_dt, "source": source})
        return items
    except Exception as e:
        print(f"  RSS 실패 ({query}): {e}")
        return []


def collect():
    results = []
    for name, desc, query in PEOPLE:
        print(f"수집: {name}")
        items = fetch_rss(query)
        # 24시간 필터
        recent = [i for i in items if i["pub_dt"] >= CUTOFF]
        # 이름 필터 (이하늬, 이혜영)
        if name in TITLE_FILTERS:
            recent = [i for i in recent if name in i["title"]]
        # 중복 제거 (제목 앞 30자 기준)
        seen, unique = set(), []
        for i in recent:
            k = i["title"][:30]
            if k not in seen:
                seen.add(k)
                unique.append(i)
        print(f"  → {len(unique)}건")
        results.append({"name": name, "desc": desc, "items": unique})
    return results


def build_html(results: list[dict]) -> str:
    date_str  = NOW_KST.strftime("%Y년 %m월 %d일")
    from_str  = CUTOFF.strftime("%m/%d %H:%M")
    to_str    = NOW_KST.strftime("%m/%d %H:%M")
    total     = sum(len(r["items"]) for r in results)

    cards = ""
    for r in results:
        name, desc, items = r["name"], r["desc"], r["items"]
        count = len(items)

        if items:
            rows = ""
            for i in items:
                time_str = i["pub_dt"].strftime("%H:%M")
                src      = i["source"] or ""
                title    = i["title"]
                link     = i["link"]
                rows += f"""
          <li class="article">
            <span class="art-time">{time_str}</span>
            <div class="art-body">
              <a class="art-title" href="{link}" target="_blank" rel="noopener">{title}</a>
              {f'<span class="art-src">{src}</span>' if src else ''}
            </div>
          </li>"""
            content = f'<ul class="article-list">{rows}\n        </ul>'
            badge   = f'<span class="badge">{count}건</span>'
        else:
            content = '<p class="no-news">24시간 내 새 뉴스 없음</p>'
            badge   = '<span class="badge zero">0건</span>'

        cards += f"""
    <div class="card{'empty' if not items else ''}">
      <div class="card-head">
        <div class="card-name">
          <strong>{name}</strong>
          <span class="desc">{desc}</span>
        </div>
        {badge}
      </div>
      <div class="card-body">{content}</div>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>고객 뉴스 {date_str}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', sans-serif;
    background: #F2F4F6;
    color: #191F28;
    min-height: 100vh;
  }}
  header {{
    background: #fff;
    border-bottom: 1px solid #E5E8EB;
    padding: 20px 28px;
    display: flex;
    align-items: baseline;
    gap: 14px;
    flex-wrap: wrap;
  }}
  header h1 {{ font-size: 17px; font-weight: 700; }}
  header .period {{
    font-size: 13px;
    color: #8B95A1;
  }}
  header .total {{
    margin-left: auto;
    font-size: 13px;
    color: #3182F6;
    font-weight: 600;
  }}
  .wrap {{
    max-width: 780px;
    margin: 24px auto;
    padding: 0 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}
  .card {{
    background: #fff;
    border: 1px solid #E5E8EB;
    border-radius: 14px;
    overflow: hidden;
  }}
  .card-head {{
    display: flex;
    align-items: center;
    padding: 14px 18px;
    border-bottom: 1px solid #F2F4F6;
    gap: 10px;
  }}
  .card-name {{ display: flex; align-items: center; gap: 8px; flex: 1; }}
  .card-name strong {{ font-size: 15px; font-weight: 700; }}
  .desc {{
    font-size: 11px;
    color: #8B95A1;
    background: #F2F4F6;
    padding: 2px 8px;
    border-radius: 10px;
  }}
  .badge {{
    font-size: 12px;
    font-weight: 600;
    color: #3182F6;
    background: #EBF3FF;
    padding: 3px 10px;
    border-radius: 20px;
  }}
  .badge.zero {{
    color: #B0B8C1;
    background: #F2F4F6;
  }}
  .card-body {{ padding: 12px 18px; }}
  .article-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .article {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
  }}
  .art-time {{
    font-size: 11px;
    color: #B0B8C1;
    white-space: nowrap;
    padding-top: 2px;
    min-width: 36px;
  }}
  .art-body {{ display: flex; flex-direction: column; gap: 3px; flex: 1; }}
  .art-title {{
    font-size: 14px;
    color: #191F28;
    text-decoration: none;
    line-height: 1.5;
  }}
  .art-title:hover {{ color: #3182F6; text-decoration: underline; }}
  .art-src {{
    font-size: 11px;
    color: #B0B8C1;
  }}
  .no-news {{
    font-size: 13px;
    color: #B0B8C1;
    padding: 4px 0;
  }}
  footer {{
    text-align: center;
    padding: 32px;
    font-size: 12px;
    color: #B0B8C1;
  }}
</style>
</head>
<body>
<header>
  <h1>고객 뉴스</h1>
  <span class="period">{from_str} ~ {to_str}</span>
  <span class="total">총 {total}건</span>
</header>
<div class="wrap">
{cards}
</div>
<footer>매일 9시 자동 업데이트 · Claude Code</footer>
</body>
</html>"""


if __name__ == "__main__":
    results = collect()
    html    = build_html(results)
    Path("docs/index.html").write_text(html, encoding="utf-8")
    print("docs/index.html 생성 완료")

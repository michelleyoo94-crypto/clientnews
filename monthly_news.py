"""
Usage: python monthly_news.py "이름"
지난 30일간의 뉴스를 수집해 monthly_raw.json 으로 저장합니다.
"""
import sys
import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote
from bs4 import BeautifulSoup

OUTPUT_PATH = "monthly_raw.json"
DAYS = 30

def parse_rss(content, since: datetime):
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

            articles.append({
                "title": title,
                "link": link,
                "published": pub_str,
                "summary": summary
            })
    except Exception as e:
        pass
    return articles

def fetch_google_news_monthly(name, description=""):
    since = datetime.now(timezone.utc) - timedelta(days=DAYS)
    query = quote(f"{name} {description}".strip())
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        return parse_rss(resp.content, since)
    except Exception as e:
        print(f"  [Google] 수집 실패: {e}")
        return []

def fetch_naver_news_monthly(name):
    since = datetime.now(timezone.utc) - timedelta(days=DAYS)
    query = quote(name)
    url = f"https://search.naver.com/rss?where=news&query={query}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        return parse_rss(resp.content, since)
    except Exception as e:
        print(f"  [Naver] 수집 실패: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python monthly_news.py \"이름\" [특징]")
        sys.exit(1)

    name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    since = datetime.now(timezone.utc) - timedelta(days=DAYS)

    print(f"'{name}' 최근 {DAYS}일 뉴스 수집 중...")
    google = fetch_google_news_monthly(name, description)
    naver = fetch_naver_news_monthly(name)

    all_articles = google + naver
    print(f"  Google: {len(google)}건 / Naver: {len(naver)}건 / 합계: {len(all_articles)}건")

    result = {
        "name": name,
        "description": description,
        "period": f"{since.strftime('%Y-%m-%d')} ~ {datetime.now().strftime('%Y-%m-%d')}",
        "total": len(all_articles),
        "articles": all_articles
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {OUTPUT_PATH}")
    print("이제 Claude Code에서 요약을 요청하세요.")

if __name__ == "__main__":
    main()

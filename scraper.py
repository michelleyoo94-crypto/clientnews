import feedparser
import requests
import json
import pandas as pd
from datetime import datetime, timezone
from urllib.parse import quote
from bs4 import BeautifulSoup

EXCEL_PATH = "통합 문서1.xlsx"
OUTPUT_PATH = "raw_news.json"

def load_people():
    df = pd.read_excel(EXCEL_PATH)
    df.columns = ["이름", "특징"]
    df = df.dropna(subset=["이름"])
    return df.to_dict("records")

def fetch_google_news(name, description):
    query = quote(f"{name} {description}")
    url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries[:5]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()
            })
        return articles
    except Exception as e:
        print(f"[{name}] 뉴스 수집 실패: {e}")
        return []

def fetch_naver_news(name):
    # Naver News RSS (API 키 없이 사용 가능한 공개 RSS)
    query = quote(name)
    url = f"https://search.naver.com/rss?where=news&query={query}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(resp.content)
        articles = []
        for entry in feed.entries[:5]:
            articles.append({
                "title": BeautifulSoup(entry.get("title", ""), "html.parser").get_text(),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": BeautifulSoup(entry.get("description", ""), "html.parser").get_text()
            })
        return articles
    except Exception as e:
        print(f"[{name}] 네이버 뉴스 수집 실패: {e}")
        return []

def fetch_dcinside(name):
    # DC인사이드 갤러리 검색
    query = quote(name)
    url = f"https://search.dcinside.com/post/p/{query}"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        posts = []
        for item in soup.select(".search_result_list li")[:5]:
            title_tag = item.select_one(".tit a")
            if title_tag:
                posts.append({
                    "title": title_tag.get_text(strip=True),
                    "link": title_tag.get("href", ""),
                    "published": "",
                    "summary": item.select_one(".cont") and item.select_one(".cont").get_text(strip=True) or ""
                })
        return posts
    except Exception as e:
        print(f"[{name}] DC인사이드 수집 실패: {e}")
        return []

def main():
    people = load_people()
    result = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "people": []
    }

    for person in people:
        name = str(person["이름"]).strip()
        desc = str(person["특징"]).strip() if pd.notna(person["특징"]) else ""
        print(f"수집 중: {name} ({desc})")

        person_data = {
            "name": name,
            "description": desc,
            "sources": {
                "google_news": fetch_google_news(name, desc),
                "naver_news": fetch_naver_news(name),
                "dcinside": fetch_dcinside(name)
            }
        }
        result["people"].append(person_data)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n완료! {OUTPUT_PATH} 저장됨")

if __name__ == "__main__":
    main()

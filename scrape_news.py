import asyncio
import re
import html as html_module
from datetime import datetime, timedelta
from pathlib import Path
from playwright.async_api import async_playwright

# (이름, 특징, 검색쿼리)
PEOPLE = [
    ("이하늬",  "배우",               "이하늬 배우"),
    ("이혜영",  "탤런트",             "이혜영"),
    ("권오경",  "한양대교수 SDI사외이사", "권오경 한양대교수"),
    ("김병주",  "MBK파트너스",        "김병주 MBK파트너스"),
    ("서정진",  "셀트리온",           "서정진 셀트리온"),
    ("정정이",  "현대해상",           "정정이 현대해상"),
    ("송창현",  "42dot",              "송창현 42dot"),
]

TODAY = datetime(2026, 5, 14)
MAX_PAGES = 5


def date_from_url(url: str) -> str:
    """URL에서 날짜 패턴 추출 (예: /20260505, /2026/05/05)"""
    m = re.search(r'[/\-_]?(2026)(\d{2})(\d{2})[/\-_\.]', url)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).strftime("%Y.%m.%d")
        except:
            pass
    m2 = re.search(r'(2026)[/\-](0[1-9]|1[0-2])[/\-](0[1-9]|[12]\d|3[01])', url)
    if m2:
        try:
            return datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3))).strftime("%Y.%m.%d")
        except:
            pass
    return ""


def normalize_date(raw: str) -> str:
    raw = raw.strip().rstrip(".")
    # YYYY.MM.DD
    m = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', raw)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).strftime("%Y.%m.%d")
        except:
            pass
    # N분 전 / N시간 전
    if re.fullmatch(r'\d+분\s*전', raw) or re.fullmatch(r'\d+시간\s*전', raw) or raw == "방금" or raw == "오늘":
        return TODAY.strftime("%Y.%m.%d")
    # N일 전
    m2 = re.fullmatch(r'(\d+)일\s*전', raw)
    if m2:
        return (TODAY - timedelta(days=int(m2.group(1)))).strftime("%Y.%m.%d")
    # 어제
    if raw == "어제":
        return (TODAY - timedelta(days=1)).strftime("%Y.%m.%d")
    # 날짜로 판단 불가 → 빈 문자열 반환 (오표기 방지)
    return ""


EXTRACT_JS = """
() => {
    const results = [];
    const titleLinks = document.querySelectorAll('a[data-heatmap-target=".tit"]');
    titleLinks.forEach(a => {
        const title = a.innerText.replace(/\\s+/g, ' ').trim();
        const href = a.href || '';
        if (!title || title.length < 3) return;

        // 개별 기사 컨테이너: 제목링크의 3단계 부모
        const container = a.parentElement?.parentElement?.parentElement;
        if (!container) return;

        let press = '';
        let date = '';
        let summary = '';

        // 모든 span을 순회하며 날짜·언론사·요약 추출
        const allSpans = Array.from(container.querySelectorAll('span'));
        for (const sp of allSpans) {
            const t = sp.innerText.replace(/\\s+/g, ' ').trim();
            if (!t) continue;

            // 날짜
            if (!date && t.length < 25) {
                if (/^\\d+시간\\s*전$/.test(t) || /^\\d+분\\s*전$/.test(t) ||
                    /^\\d+일\\s*전$/.test(t) ||
                    /^(어제|오늘|방금)$/.test(t) ||
                    /^\\d{4}\\.\\d{1,2}\\.\\d{1,2}\\.?$/.test(t)) {
                    date = t;
                }
            }

            // 요약 (body1 클래스)
            if (!summary && sp.className.includes('body1') && t.length > 30) {
                summary = t.substring(0, 220);
            }
        }

        // 언론사: 날짜 span 바로 앞 텍스트 노드 or profile-info
        const allDivs = Array.from(container.querySelectorAll('div, span'));
        for (const el of allDivs) {
            const cls = el.className || '';
            if (cls.includes('profile-info') || cls.includes('press')) {
                const t = el.innerText.replace(/\\s+/g, ' ').trim();
                const part = t.split(/\\|/)[0].trim();
                if (part && part.length < 40 && !part.includes('Keep')) {
                    press = part;
                    break;
                }
            }
        }
        // fallback: 날짜 바로 앞 span
        if (!press) {
            for (let i = 0; i < allSpans.length - 1; i++) {
                const t = allSpans[i].innerText.trim();
                const nextT = allSpans[i+1]?.innerText.trim() || '';
                if (nextT === date && t && t.length < 35 && !t.includes('Keep')) {
                    press = t;
                    break;
                }
            }
        }

        results.push({ title, href, date, press, summary });
    });
    return results;
}
"""


async def scrape_person(page, name: str, description: str, query: str,
                        title_filter: str | None = None) -> list[dict]:
    base_url = (
        f"https://search.naver.com/search.naver?where=news&query={query}"
        f"&ds=2026.01.01&de=2026.12.31&sort=1"
    )
    print(f"\n[{name}] 검색: {query}" + (f" (제목에 '{title_filter}' 포함만)" if title_filter else ""))

    all_items = []
    try:
        for page_num in range(1, MAX_PAGES + 1):
            start = (page_num - 1) * 10 + 1
            url = f"{base_url}&start={start}"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2500)

            items = await page.evaluate(EXTRACT_JS)
            print(f"  페이지 {page_num} (start={start}): {len(items)}건")

            if not items:
                break

            for item in items:
                item["name"] = name
                item["description"] = description
                item["date"] = normalize_date(item.get("date", ""))

            # 제목 필터 적용 (이혜영 등 동명이인 방지)
            if title_filter:
                items = [i for i in items if title_filter in i["title"]]

            all_items.extend(items)

    except Exception as e:
        print(f"  오류: {e}")

    # 중복 제거
    seen = set()
    unique = []
    for item in all_items:
        key = item["title"][:40]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # 날짜 없는 기사: URL에서 추출 → 그래도 없으면 페이지 방문
    no_date = [i for i in unique if not i["date"]]
    if no_date:
        print(f"  날짜 미상 {len(no_date)}건 — URL/페이지에서 보완 시도")
        for item in no_date:
            # 1) URL 패턴
            item["date"] = date_from_url(item["href"])
            if item["date"]:
                continue
            # 2) 기사 페이지의 meta 태그 방문
            try:
                await page.goto(item["href"], wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(1000)
                date_meta = await page.evaluate("""
                () => {
                    const metas = [
                        document.querySelector('meta[property="article:published_time"]'),
                        document.querySelector('meta[name="article:published_time"]'),
                        document.querySelector('meta[name="pubdate"]'),
                        document.querySelector('meta[property="og:regDate"]'),
                        document.querySelector('time[datetime]'),
                    ];
                    for (const el of metas) {
                        if (el) return el.getAttribute('content') || el.getAttribute('datetime') || '';
                    }
                    return '';
                }
                """)
                if date_meta:
                    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_meta)
                    if m:
                        item["date"] = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
            except:
                pass

    print(f"  [{name}] 최종 {len(unique)}건")
    return unique


def sort_key(item):
    try:
        return datetime.strptime(item["date"], "%Y.%m.%d")
    except:
        return datetime(2026, 1, 1)


def e(s):
    return html_module.escape(str(s or ""))


def save_html(all_results: list[dict], out_path: str):
    import json as _json
    from pathlib import Path as _Path

    KEYS_FILE = _Path(out_path).parent / "last_run_keys.json"

    # 이전 실행 기사 키 로드
    prev_keys: set = set()
    if KEYS_FILE.exists():
        try:
            prev_keys = set(_json.loads(KEYS_FILE.read_text(encoding="utf-8")))
        except:
            pass

    # 현재 기사 키 집합
    cur_keys = {r["title"][:40] for r in all_results}

    # 신규 기사 키
    new_keys = cur_keys - prev_keys
    new_count = sum(1 for r in all_results if r["title"][:40] in new_keys)
    updated_at = TODAY.strftime("%Y.%m.%d %H:%M")

    # 사람별 정렬된 데이터 준비
    people_data = []
    for name, desc, *_ in PEOPLE:
        items = sorted(
            [r for r in all_results if r["name"] == name],
            key=sort_key, reverse=True
        )
        people_data.append((name, desc, items))

    # 날짜별 그룹핑 함수
    def group_by_date(items):
        groups = {}
        for item in items:
            d = item["date"] or "날짜 미상"
            groups.setdefault(d, []).append(item)
        return sorted(groups.items(), reverse=True)

    # 탭 버튼 생성 (신규 있으면 탭에 NEW 표시)
    tabs_html = ""
    for i, (name, desc, items) in enumerate(people_data):
        active = "active" if i == 0 else ""
        has_new = any(r["title"][:40] in new_keys for r in items)
        new_dot = ' <span class="new-dot"></span>' if has_new else ""
        tabs_html += f'<button class="tab-btn {active}" onclick="showTab({i})">{e(name)}{new_dot} <span class="count">{len(items)}</span></button>\n'

    # 각 인물 패널 생성
    panels_html = ""
    for i, (name, desc, items) in enumerate(people_data):
        display = "block" if i == 0 else "none"
        date_groups = group_by_date(items)

        dates_html = ""
        for date, date_items in date_groups:
            cards_html = ""
            for item in date_items:
                is_new = item["title"][:40] in new_keys
                new_badge = '<span class="new-badge">NEW</span>' if is_new else ""
                card_cls = "card new-card" if is_new else "card"
                summary_html = f'<p class="summary">{e(item["summary"])}</p>' if item.get("summary") else ""
                press_html = f'<span class="press">{e(item["press"])}</span>' if item.get("press") else ""
                cards_html += f"""
        <div class="{card_cls}">
          <div class="card-meta">{press_html}{new_badge}</div>
          <a class="card-title" href="{e(item['href'])}" target="_blank" rel="noopener">{e(item['title'])}</a>
          {summary_html}
        </div>"""

            dates_html += f"""
      <div class="date-group">
        <div class="date-label">{e(date)}</div>
        <div class="cards">{cards_html}
        </div>
      </div>"""

        empty = '<p class="empty">검색 결과 없음</p>' if not items else ""
        panels_html += f"""
    <div class="panel" id="panel-{i}" style="display:{display}">
      <div class="panel-header">
        <h2>{e(name)}</h2>
        <span class="desc-tag">{e(desc)}</span>
        <span class="total-count">총 {len(items)}건</span>
      </div>
      {empty}{dates_html}
    </div>"""

    # 현재 키 저장 (다음 실행 시 비교용)
    KEYS_FILE.write_text(_json.dumps(list(cur_keys), ensure_ascii=False), encoding="utf-8")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>고객 뉴스 모니터링 · 2026</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Pretendard', 'Noto Sans KR', sans-serif;
    background: #F2F4F6;
    color: #191F28;
    min-height: 100vh;
  }}
  header {{
    background: #fff;
    border-bottom: 1px solid #E5E8EB;
    padding: 20px 32px;
    position: sticky; top: 0; z-index: 100;
  }}
  header h1 {{ font-size: 18px; font-weight: 700; color: #191F28; }}
  header p {{ font-size: 13px; color: #8B95A1; margin-top: 2px; }}
  header .new-info {{ font-size: 12px; color: #00B386; font-weight: 600; margin-top: 4px; }}

  .tabs {{
    background: #fff;
    border-bottom: 1px solid #E5E8EB;
    padding: 0 32px;
    display: flex; gap: 4px; overflow-x: auto;
  }}
  .tab-btn {{
    padding: 14px 18px;
    border: none; background: none; cursor: pointer;
    font-size: 14px; font-weight: 500; color: #8B95A1;
    border-bottom: 2px solid transparent;
    white-space: nowrap; transition: all .15s;
  }}
  .tab-btn:hover {{ color: #191F28; }}
  .tab-btn.active {{ color: #3182F6; border-bottom-color: #3182F6; font-weight: 700; }}
  .tab-btn .count {{
    display: inline-block; background: #F2F4F6;
    color: #8B95A1; font-size: 11px; font-weight: 600;
    padding: 1px 6px; border-radius: 10px; margin-left: 4px;
  }}
  .tab-btn.active .count {{ background: #EBF3FF; color: #3182F6; }}
  .new-dot {{
    display: inline-block; width: 6px; height: 6px;
    background: #00B386; border-radius: 50%; margin-left: 2px; vertical-align: middle;
  }}
  .new-badge {{
    display: inline-block; background: #E6FBF4; color: #00B386;
    font-size: 10px; font-weight: 700; padding: 1px 7px;
    border-radius: 10px; margin-left: 6px; vertical-align: middle;
  }}
  .new-card {{
    background: #F5FFFB;
    border-color: #B3EDD9;
  }}

  .content {{ max-width: 860px; margin: 0 auto; padding: 32px 24px; }}

  .panel-header {{
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 24px;
  }}
  .panel-header h2 {{ font-size: 22px; font-weight: 700; }}
  .desc-tag {{
    background: #EBF3FF; color: #3182F6;
    font-size: 12px; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
  }}
  .total-count {{
    margin-left: auto; font-size: 13px; color: #8B95A1;
  }}

  .date-group {{ margin-bottom: 28px; }}
  .date-label {{
    font-size: 13px; font-weight: 700; color: #8B95A1;
    padding: 0 0 10px 0;
    border-bottom: 1px solid #E5E8EB;
    margin-bottom: 12px;
  }}

  .card {{
    background: #fff;
    border: 1px solid #E5E8EB;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: box-shadow .15s;
  }}
  .card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,.08); }}
  .card-meta {{ margin-bottom: 6px; }}
  .press {{
    font-size: 12px; color: #8B95A1; font-weight: 500;
    background: #F8F9FA; padding: 2px 8px; border-radius: 4px;
  }}
  .card-title {{
    display: block;
    font-size: 15px; font-weight: 600; color: #191F28;
    line-height: 1.5; text-decoration: none;
    margin-bottom: 6px;
  }}
  .card-title:hover {{ color: #3182F6; text-decoration: underline; }}
  .summary {{
    font-size: 13px; color: #6B7684; line-height: 1.6;
  }}
  .empty {{ color: #8B95A1; font-size: 14px; padding: 20px 0; }}
</style>
</head>
<body>
<header>
  <h1>고객 뉴스 모니터링</h1>
  <p>2026년 · 네이버 뉴스 기준 · 업데이트 {updated_at}</p>
  {f'<p class="new-info">✦ 이번 업데이트 신규 {new_count}건</p>' if new_count else ''}
</header>
<div class="tabs">
{tabs_html}</div>
<div class="content">
{panels_html}
</div>
<script>
function showTab(idx) {{
  document.querySelectorAll('.tab-btn').forEach((b,i) => b.classList.toggle('active', i===idx));
  document.querySelectorAll('.panel').forEach((p,i) => p.style.display = i===idx ? 'block' : 'none');
}}
</script>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
    print(f"\n저장 완료 → {out_path}")


async def main():
    all_results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "Chrome/124.0 Safari/537.36",
            locale="ko-KR",
        )
        page = await ctx.new_page()

        for name, desc, query in PEOPLE:
            title_filter = name if name == "이혜영" else None
            items = await scrape_person(page, name, desc, query, title_filter)
            all_results.extend(items)

        await browser.close()

    print(f"\nPlaywright 수집: {len(all_results)}건")

    # ── MCP 결과 병합 ──────────────────────────────────────────────────────
    import json as _json
    from pathlib import Path as _Path
    mcp_path = _Path("c:\\Users\\michelle\\projects\\고객 뉴스\\mcp_results.json")
    if mcp_path.exists():
        mcp_items = _json.loads(mcp_path.read_text(encoding="utf-8"))
        # 기존 제목 집합 (앞 40자 기준 중복 제거)
        existing_keys = {r["title"][:40] for r in all_results}
        added = 0
        for item in mcp_items:
            key = item["title"][:40]
            if key not in existing_keys:
                existing_keys.add(key)
                all_results.append(item)
                added += 1
        print(f"MCP 추가: {added}건 (중복 제외)")
    else:
        print("mcp_results.json 없음 — MCP 병합 스킵")

    print(f"최종 합계: {len(all_results)}건")
    out = "c:\\Users\\michelle\\projects\\고객 뉴스\\뉴스_2026.html"
    save_html(all_results, out)


if __name__ == "__main__":
    asyncio.run(main())

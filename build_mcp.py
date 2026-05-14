"""
네이버 MCP 검색 결과를 가공해 mcp_results.json 으로 저장하는 스크립트.
pubDate 2026년 기사만 포함, 이혜영은 제목에 '이혜영' 포함된 것만 포함.
"""
import json, re, html

MONTHS = {
    'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
    'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'
}

def parse_date(pub_date: str) -> str:
    """'Mon, 11 May 2026 08:33:00 +0900' → '2026.05.11'"""
    try:
        parts = pub_date.split(', ')[1].split(' ')
        day, mon, year = parts[0], parts[1], parts[2]
        return f"{year}.{MONTHS[mon]}.{day.zfill(2)}"
    except:
        return ""

def clean(s: str) -> str:
    """HTML 태그 및 엔티티 제거"""
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()

# ── 원본 MCP 데이터 (person, description, title_filter, items) ──────────────
RAW = []

# ── 이하늬 ──────────────────────────────────────────────────────────────────
RAW += [("이하늬","배우",None,x) for x in [
  {"title":"박지훈, 영화·시리즈 동시 노미…제24회 디렉터스컷 어워즈, 후보 공개","originallink":"https://sports.donga.com/ent/article/all/20260511/133895884/1","pubDate":"Mon, 11 May 2026 08:33:00 +0900","description":"DGK가 주최하는 이번 시상식은 2025년 4월 1일부터 2026년 3월 31일 사이에 공개된 영화와 이하늬(애마), 임수정(파인) 등이 이름을 올렸다."},
  {"title":"[62회 백상예술대상] 방효린, 방송부문 여자 신인 연기상…'이하늬 선배를 통해'","originallink":"https://www.nc.press/news/articleView.html?idxno=614789","pubDate":"Fri, 08 May 2026 20:27:00 +0900","description":"이하늬 선배를 통해 훌륭한 배우란 어떤 것인지 보고 배울 수 있었다."},
  {"title":"카드로 보는 시사상식 [2026년 03월 넷째 주]","originallink":"http://www.sisunnews.co.kr/news/articleView.html?idxno=235765","pubDate":"Sun, 22 Mar 2026 13:00:00 +0900","description":"최근 배우 차은우와 이하늬(60억 원대) 등 유명 연예인들이 1인 기획사를 이용해 거액의 세금을 절약했다는 의혹이 제기됐다."},
  {"title":"연예계 잇따른 탈세 의혹 속…유노윤호, 서울시 모범 납세자 표창","originallink":"https://www.mk.co.kr/article/11984940","pubDate":"Wed, 11 Mar 2026 11:33:00 +0900","description":"배우 이하늬, 차은우, 김선호 등 잇따른 연예계 탈세 의혹 속에서 유노윤호가 성실 납세를 인정받아 서울시 표창을 받았다."},
  {"title":"[잇슈 연예 브리핑] ③ 이하늬 1인 기획사 '곰탕집' 분점 논란…\"단순 임대\"","originallink":"https://www.obsnews.co.kr/news/articleView.html?idxno=1516630","pubDate":"Wed, 11 Mar 2026 09:52:00 +0900","description":"배우 이하늬가 1인 기획사 분점으로 등록된 '곰탕집' 논란에 '단순 임대'라고 해명했다."},
  {"title":"이하늬 개인 법인 '호프프로젝트' 논란… 한남동 곰탕집 주소 등록 이유는?","originallink":"https://www.ftimes.kr/news/articleView.html?idxno=36025","pubDate":"Mon, 09 Mar 2026 23:12:00 +0900","description":"배우 이하늬의 개인 법인 '호프프로젝트'가 서울 용산구 한남동의 한 곰탕집을 분점 주소지로 두고 있는 사실이 알려지면서 관심이 쏠리고 있다."},
  {"title":"장어집·곰탕집 '탈세' 의혹과 대조적… 소녀시대 유리, '유공납세자'","originallink":"https://biz.chosun.com/topics/topics_social/2026/03/10/BTPBW5DMNJAXJARLEMJYQVXYCQ/","pubDate":"Tue, 10 Mar 2026 14:06:00 +0900","description":"최근 장어집·곰탕집 등을 1인 기획사로 등록해 탈세 의혹을 받는 배우 차은우·이하늬 등과 대조적인 모습이다."},
  {"title":"스타의 1인기획사, 자립의 발판인가 탈세 통로인가","originallink":"https://koreajoongangdaily.joins.com/news/2026-02-13/englishStudy/bilingualNews/","pubDate":"Fri, 13 Feb 2026 07:00:00 +0900","description":"지난해에도 배우 이하늬와 유연석 등 여러 연예인들이 국세청으로부터 탈세 혐의로 추징금을 통보받았다."},
  {"title":"[주간핫이슈] 차은우 잡은 국세청, 지능적 탈세 정조준","originallink":"https://weekly.hankooki.com/news/articleView.html?idxno=7147450","pubDate":"Tue, 03 Feb 2026 14:00:00 +0900","description":"기존 연예인 최대 추징금 금액은 지난해 2월 배우 이하늬에게 부과된 60억원대였다."},
  {"title":"세금 절반 줄이는 '1인 기획사 매직'… 비중은 역대 최대","originallink":"https://biz.chosun.com/topics/topics_social/2026/01/31/FYQSUYTPP5CPHKVT6GWH3N7AAQ/","pubDate":"Sat, 31 Jan 2026 06:02:00 +0900","description":"2024년 배우 이하늬를 비롯해 지난해 유연석, 조진웅, 이준기 등이 수억~수십억원의 세금 추징을 당하면서 1인 기획사 논란이 커졌다."},
  {"title":"이하늬→트와이스 지효 14년만 비너스 모델 전격 교체","originallink":"https://www.newsen.com/news_view.php?uid=202601301746061210","pubDate":"Fri, 30 Jan 2026 18:12:00 +0900","description":"14년간 이어온 이전 모델은 배우 이하늬. 신영와코루 비너스는 트와이스 지효를 새로운 브랜드 모델로 발탁하고 2026 봄 캠페인을 전개한다."},
  {"title":"이하늬→트와이스 지효, 14년 만의 비너스 모델 교체","originallink":"https://sports.khan.co.kr/article/202601301127003?pt=nv","pubDate":"Fri, 30 Jan 2026 11:27:00 +0900","description":"국내 대표 언더웨어 브랜드 비너스는 트와이스 지효를 브랜드 모델로 발탁했다. 해당 브랜드는 이하늬가 무려 14년간 모델로 활동 중이었다."},
  {"title":"멀티캐스팅 끝판왕은 누구? 연상호 '군체' vs 노희경 '천천히 강렬하게'","originallink":"https://www.harpersbazaar.co.kr/article/1896432","pubDate":"Fri, 30 Jan 2026 11:54:00 +0900","description":"가수를 꿈꾸는 이하늬까지. 노희경 특유의 섬세한 대사가 이 배우들의 입을 통해 흘러나오는 순간, 2026년 하반기는 화제작이 될 것이다."},
  {"title":"라비앙, 2026년 브랜드 모델로 이하늬 선정","originallink":"https://www.m-joongang.com/news/articleView.html?idxno=402036","pubDate":"Fri, 16 Jan 2026 09:14:00 +0900","description":"프리미엄 안티에이징 스킨케어 브랜드 라비앙이 2026년 브랜드 새 모델로 배우 이하늬를 선정했다."},
  {"title":"[NC인터뷰] 이하늬, 국악→미스유니버스→배우 19년…\"韓 문화 애정, 재부팅 시간\"","originallink":"https://www.nc.press/news/articleView.html?idxno=600579","pubDate":"Wed, 03 Dec 2025 17:40:00 +0900","description":"배우로서 재부팅 하는 시간을 확보하려고 한다. 데뷔 20년을 맞는 2026년, 지난 몇 년과는 다른 행보를 보일 것을 예고했다."},
  {"title":"넷플릭스, 하반기 1000억원대 '메가 프로젝트' 쏟아낸다…K-콘텐츠 공습","originallink":"https://www.thefairnews.co.kr/news/articleView.html?idxno=73183","pubDate":"Thu, 02 Apr 2026 00:00:00 +0900","description":"출연진으로는 송혜교, 공유 외에도 차승원, 이하늬, 김설현 등이 합류해 화려한 앙상블을 완성했다."},
  {"title":"[웰컴 2026] 귀한·변곡점·시험대…어디서 터질지 모르는 '안방극장 기대작'","originallink":"https://news.tf.co.kr/read/entertain/2278006.htm","pubDate":"Thu, 01 Jan 2026 09:00:00 +0900","description":"공유, 김설현, 차승원, 이하늬 등 톱 배우들의 대거 출연은 물론, 스타 작가 노희경 각본으로 초반 화제성과 기대감이 높다."},
]]

# ── 이혜영 ──────────────────────────────────────────────────────────────────
RAW += [("이혜영","탤런트","이혜영",x) for x in [
  {"title":"신동엽, 이소라 재회 심경 밝혔다…\"내 삶의 한 페이지였다\"","originallink":"https://www.ftimes.kr/news/articleView.html?idxno=36590","pubDate":"Tue, 07 Apr 2026 17:28:00 +0900","description":"이상민과 이혜영 관련 에피소드까지 유쾌하게 풀어내며 특유의 입담도 보여줬다."},
  {"title":"동물 학대 논란에 휩싸인 이혜영, 대체 무슨 일이길래…","originallink":"https://www.huffingtonpost.kr/article/256173","pubDate":"Thu, 26 Mar 2026 18:22:00 +0900","description":"이혜영이 '동물 학대' 논란으로 도마에 올랐다. 2026년 3월 25일 화가로 활동 중인 가수 출신 방송인 이혜영이 논란에 휩쓸렸다."},
  {"title":"'재혼' 이상민, 전처 이혜영 축하받았는데…인사 피해 숨었다","originallink":"https://n.news.naver.com/mnews/article","pubDate":"Fri, 27 Jun 2025 18:19:00 +0900","description":"이상민은 2004년 가수 겸 배우 이혜영과 결혼했다가 이듬해 이혼했다. 이상민의 재혼은 약 20년 만이다."},
]]

# ── 권오경 ──────────────────────────────────────────────────────────────────
RAW += [("권오경","한양대교수 SDI사외이사",None,x) for x in [
  {"title":"한양대 교수진, 공학계 최고 권위 '한림원 대상' 포함 3관왕","originallink":"https://www.chosun.com/national/education/2026/03/18/JEY5AN5CI5GLZBXZP2TRNBMLAY/","pubDate":"Wed, 18 Mar 2026 15:52:00 +0900","description":"한양대는 지난 10일 서울 그랜드 워커힐에서 열린 '2026 한국공학한림원 시상식'에서 권오경 석좌교수가 대상을 받았다."},
  {"title":"한양대 교수진, '한국공학한림원' 대상·해동상·동진상 석권","originallink":"https://www.segye.com/newsView/20260312518846","pubDate":"Thu, 12 Mar 2026 19:00:00 +0900","description":"'2026 한국공학한림원 시상식'에서 권오경 석좌교수가 대상을, 임창환 교수가 해동상, 안진호 연구부총장이 동진상을 수상했다."},
  {"title":"공학한림원 대상에 권오경 한양대 교수","originallink":"https://www.donga.com/news/People/article/all/20260310/133496232/2","pubDate":"Tue, 10 Mar 2026 04:34:00 +0900","description":"한국공학한림원은 '2026 한국공학한림원 시상식'의 제30회 대상 수상자로 권오경 한양대 석좌교수를 선정했다."},
  {"title":"제30회 공학한림원 대상에 권오경 한양대 석좌교수","originallink":"https://www.etnews.com/20260309000139","pubDate":"Mon, 09 Mar 2026 12:01:00 +0900","description":"권오경 한양대 석좌교수가 제30회 한국공학한림원 대상의 영예를 안았다."},
  {"title":"공학한림원 '공학기술인상' 대상에 권오경 한양대 석좌교수","originallink":"http://www.edaily.co.kr/news/newspath.asp?newsid=03404646645381680","pubDate":"Mon, 09 Mar 2026 12:01:00 +0900","description":"한국공학한림원은 9일 '2026 한국공학한림원 시상식' 수상자를 발표하고 대상 수상자로 권오경 한양대학교 석좌교수를 선정했다."},
  {"title":"공학한림원 대상에 권오경 한양대 석좌교수…장진아 포스텍 교수, 젊은공학인상","originallink":"https://www.dongascience.com/news/view/76721","pubDate":"Mon, 09 Mar 2026 14:38:00 +0900","description":"제30회 한국공학한림원 대상 수상자로 권오경 한양대 융합전자공학부 석좌교수가 선정됐다."},
  {"title":"\"삼성전자 파업땐 신뢰 하락… 국가경제 전체 치명적 타격\"","originallink":"https://www.etnews.com/20260505000058","pubDate":"Tue, 05 May 2026 09:00:00 +0900","description":"권오경 한양대 융합전자공학부 석좌교수(전 한국공학한림원 회장)는 파업 강행 시 반도체 라인 재가동에 오랜 시간이 걸린다고 경고했다."},
  {"title":"[더벨][사외이사 BSM 점검]LG엔솔, CEO 경험 지닌 에너지 전문가 발굴하나","originallink":"https://www.thebell.co.kr/free/content/ArticleView.asp?key=202601050840501160106190","pubDate":"Mon, 12 Jan 2026 08:12:00 +0900","description":"이 중 권오경 한양대 공과대학 융합전자공학부 석좌교수가 삼성SDI 사외이사로 재임 중이다."},
]]

# ── 김병주 ──────────────────────────────────────────────────────────────────
RAW += [("김병주","MBK파트너스",None,x) for x in [
  {"title":"중국, 미국 제치고 억만장자 보유국 1위…어디서 돈 벌었나","originallink":"https://www.ddaily.co.kr/page/view/2026051315062519145","pubDate":"Wed, 13 May 2026 15:09:00 +0900","description":"국내 자산가 중에서는 이재용 삼성전자 회장을 비롯해 김병주 MBK파트너스 회장, 서정진 셀트리온 회장 등이 대표적인 억만장자로 꼽힌다."},
  {"title":"[단독] 검찰, 'MBK 홈플러스 사건' 수사 재시동…신영증권 관계자 조사","originallink":"https://biz.heraldcorp.com/article/10737139","pubDate":"Wed, 13 May 2026 14:38:00 +0900","description":"중앙지검은 2025년 4월 수사가 시작된 후 2026년 1월 주요 피의자 4명에 대해 구속영장을 청구했으나 기각됐다. 김병주 MBK파트너스 회장과 김광일 부회장..."},
  {"title":"[기업의 시간] 신세계, 96년 유통 제국…MBK파트너스 김병주 회장 주목","originallink":"https://www.polinews.co.kr/news/articleView.html?idxno=730944","pubDate":"Wed, 13 May 2026 07:00:00 +0900","description":"MBK파트너스 김병주 회장은 여러 차례 국회 증인 출석 요구에 불출석하다 2025년 10월 정무위 국감에 처음 출석했다."},
  {"title":"2026 대한민국 50대 부자","originallink":"https://www.forbeskorea.co.kr/news/articleView.html?idxno=401816","pubDate":"Tue, 28 Apr 2026 14:12:00 +0900","description":"지난해 2위에서 1위로 올랐고 2위인 김병주 MBK파트너스 회장과 격차를 크게 벌렸다."},
  {"title":"포브스 선정 한국 최고 부자는 '이재용'…김병주 MBK 2위","originallink":"https://www.theguru.co.kr/news/article.html?no=100629","pubDate":"Thu, 16 Apr 2026 08:30:00 +0900","description":"포브스가 발표한 '2026 한국 자산가' 1위에 이재용 회장이 올랐고, 김병주 MBK파트너스 회장은 99억 달러로 2위를 차지했다."},
  {"title":"[MBK의 명과 암] ① '유통공룡' 홈플러스 인수 10년…점포 매각·임직원 갈등","originallink":"https://www.ceoscoredaily.com/page/view/2026040615530432705","pubDate":"Fri, 10 Apr 2026 07:02:00 +0900","description":"MBK파트너스가 7조2000억원을 들여 홈플러스를 인수한 지 10년, 김병주 MBK 회장의 자택 등 개인 자산을 담보로 마련된 자금이 투입됐다."},
  {"title":"[단독] 김병주 회장의 '자택 담보'… MBK, 홈플러스에 홀로 1000억 수혈","originallink":"https://biz.chosun.com/stock/market_trend/2026/03/01/3BCFX2LC6FFOPMERQGIVH2FXKU/","pubDate":"Sun, 01 Mar 2026 08:01:00 +0900","description":"홈플러스의 기업회생 연장 여부 결정을 앞두고 최대주주인 MBK파트너스가 1000억원 규모의 긴급운영자금을 투입한다. 김병주 회장이 자택을 담보로 제공했다."},
  {"title":"법원, 김병주 MBK 회장 등 경영진 4명 구속영장 모두 기각","originallink":"https://www.investchosun.com/site/data/html_dir/2026/01/14/2026011480009.html","pubDate":"Wed, 14 Jan 2026 08:24:00 +0900","description":"법원이 '홈플러스 사태'와 관련해 사기 등의 혐의를 받는 김병주 MBK파트너스 회장에 대한 구속영장을 기각했다."},
  {"title":"[단독] 홈플러스, 차장 직급 이상 대상 희망퇴직 시행","originallink":"https://www.chosun.com/economy/market_trend/2026/01/27/KHPMYO2SE5DO5LWAIKZFMX2KSE/","pubDate":"Tue, 27 Jan 2026 16:24:00 +0900","description":"앞서 홈플러스 사태로 구속영장이 청구됐던 김병주 MBK파트너스 회장과 김광일 부회장 등의 구속 시도가 실패로 끝난 상황이다."},
  {"title":"MBK 사회적 책임위원회 책임 투자·사회적 기여 강화","originallink":"https://biz.heraldcorp.com/article/10683503","pubDate":"Fri, 27 Feb 2026 07:47:00 +0900","description":"김병주 MBK파트너스 회장이 지난해 10월 국정감사에 출석해 홈플러스 사태에 대한 입장을 밝힌 바 있다."},
  {"title":"[채명석의 산업시각] 직원 신뢰 얻은 최윤범, 그러지 못한 김병주","originallink":"http://www.thebigdata.co.kr/view.php?ud=202603181407568766570d99e4c8_23","pubDate":"Wed, 18 Mar 2026 14:16:00 +0900","description":"경영자로서 김병주 MBK 회장과 최윤범 고려아연 회장의 차이는 직원 신뢰에서 드러났다."},
  {"title":"검찰, 'MBK 홈플러스 사건' 반부패2부로 재배당","originallink":"https://www.segye.com/newsView/20260204516212","pubDate":"Wed, 04 Feb 2026 17:08:00 +0900","description":"중앙지검은 'MBK 홈플러스 사건'을 반부패3부에서 반부패2부로 재배당했다. 김병주 MBK파트너스 회장이 1월 13일 영장실질심사에 출석했다."},
  {"title":"[Invest] 검찰, '홈플러스 사태' 김병주 MBK 회장 등 4인 구속영장 청구","originallink":"https://www.investchosun.com/site/data/html_dir/2026/01/07/2026010780219.html","pubDate":"Wed, 07 Jan 2026 22:24:00 +0900","description":"검찰이 김병주 MBK파트너스 회장과 김광일 부회장에 대해 구속영장을 청구했다."},
]]

# ── 서정진 ──────────────────────────────────────────────────────────────────
RAW += [("서정진","셀트리온",None,x) for x in [
  {"title":"출시 2년차 탄력 받았나…셀트리온 짐펜트라, 美서 역대 최대 처방량","originallink":"https://www.dailian.co.kr/news/view/1641934/","pubDate":"Fri, 08 May 2026 10:06:00 +0900","description":"출시 초기에는 서정진 셀트리온그룹 회장을 비롯한 경영진이 미국 전역을 돌며 주요 의료진과 직접 만났다."},
  {"title":"셀트리온 1분기 '계단식 성장' 충족, 서정진 신제품 안착으로 실적 목표 순항","originallink":"https://www.businesspost.co.kr/BP?command=article_view&num=437158","pubDate":"Wed, 06 May 2026 15:06:00 +0900","description":"서정진 셀트리온그룹 회장이 올해 첫 분기 성적표에서 합격점을 받았다."},
  {"title":"2026 대한민국 50대 부자","originallink":"https://www.forbeskorea.co.kr/news/articleView.html?idxno=401816","pubDate":"Tue, 28 Apr 2026 14:12:00 +0900","description":"3위 서정진 81억 달러 / 셀트리온. 서정진은 바이오제약사 셀트리온 공동창업자로 올해 부자 순위에서 3위에 올랐다."},
  {"title":"서정진 셀트리온 회장, 韓 부자 3위…총자산 12조원","originallink":"https://www.theguru.co.kr/news/article.html?no=100636","pubDate":"Thu, 16 Apr 2026 09:48:00 +0900","description":"포브스가 발표한 2026년 한국 50대 자산가 순위에서 서정진 셀트리온 회장은 81억 달러로 3위를 차지했다."},
  {"title":"국민성장펀드 50조 푼다…소버린AI·새만금 등 2차 프로젝트 가동","originallink":"http://www.4th.kr/news/articleView.html?idxno=2110440","pubDate":"Tue, 14 Apr 2026 17:08:00 +0900","description":"2026년 4월 14일 예금보험공사에서 열린 국민성장펀드 2차 전략위원회에서 이억원 금융위원장, 서정진 셀트리온 회장, 박현주 미래에셋 회장 등이 참석했다."},
  {"title":"이재용 30조·서정진 13조…1분기 총수 '주식 부자' 순위 보니","originallink":"http://www.newslock.co.kr/news/articleView.html?idxno=127946","pubDate":"Thu, 02 Apr 2026 11:12:00 +0900","description":"1분기 주식재산 순위 1위 이재용(30조9414억원), 2위 서정진 셀트리온 회장(13조5347억원)이었다."},
  {"title":"[정기주총] 서정진, 11년 만 의장 복귀…셀트리온 '2조 투자·1.7조 소각'","originallink":"http://www.4th.kr/news/articleView.html?idxno=2109494","pubDate":"Tue, 24 Mar 2026 18:00:00 +0900","description":"서정진 셀트리온 회장이 11년 만에 주주총회 의장으로 복귀해 2조원 투자와 역대 최대 자사주 소각을 발표했다."},
  {"title":"[현장] 서정진 셀트리온 회장 \"사업비중 '신약:시밀러'=6:4가 목표\"","originallink":"https://www.fetv.co.kr/news/article.html?no=215603","pubDate":"Tue, 24 Mar 2026 15:48:00 +0900","description":"서정진 셀트리온 회장이 2026년 정기 주주총회에서 신약과 바이오시밀러 매출 비중을 향후 6:4로 뒤집겠다는 목표를 제시했다."},
  {"title":"168분간의 '끝장 소통'…11년 만에 의사봉 든 서정진의 정면돌파","originallink":"https://biz.heraldcorp.com/article/10701502","pubDate":"Tue, 24 Mar 2026 13:45:00 +0900","description":"서정진 셀트리온그룹 회장이 11년 만에 직접 주총에 나서며 정책 의지를 분명히 드러냈다. 168분간 주주들과 소통했다."},
  {"title":"서정진 \"4세대 비만신약, 5월 허가용 동물임상 돌입…내년 1상 진입\"","originallink":"https://www.mt.co.kr/thebio/2026/03/24/2026032411592876379","pubDate":"Tue, 24 Mar 2026 13:46:00 +0900","description":"서정진 셀트리온그룹 회장은 정기 주주총회에서 개발 중인 4세대 비만신약에 대해 5월 허가용 동물임상에 돌입한다고 밝혔다."},
  {"title":"[더벨] '고희 서정진' 다가온 은퇴시점, '서진석 체제' 전환 가시권","originallink":"https://www.thebell.co.kr/free/content/ArticleView.asp?key=202603091637131440109425","pubDate":"Wed, 11 Mar 2026 08:12:00 +0900","description":"셀트리온이 오너 2세 서진석을 중심으로 경영진 재편에 나선 가운데 창업주 서정진 회장의 은퇴 시점이 가시권에 들어왔다."},
  {"title":"[드림&CEO] 셀트리온 서정진, '역대 최대 실적' 딛고 AI 입혀 올 매출 5조 목표","originallink":"http://www.newsdream.kr/news/articleView.html?idxno=109309","pubDate":"Fri, 13 Mar 2026 07:16:00 +0900","description":"셀트리온의 2026년은 바이오시밀러의 양적 팽창과 AI 신약 개발이라는 질적 성장이 교차하는 시기다."},
  {"title":"셀트리온홀딩스, 셀트리온 투자 '영끌'… 서정진 수천억 조달 완료","originallink":"http://www.press9.kr/news/articleView.html?idxno=74613","pubDate":"Mon, 06 Apr 2026 11:10:00 +0900","description":"서정진 셀트리온그룹 회장은 2025년 4월 사재 500억원을 투입해 셀트리온 주식을 장내 매입하겠다고 밝혔다."},
  {"title":"셀트리온, 1분기 목표 영업익 3천억 넘겨…연간 실적 기대치 '쑥'","originallink":"https://news.einfomax.co.kr/news/articleView.html?idxno=4413262","pubDate":"Wed, 06 May 2026 10:10:00 +0900","description":"서정진 셀트리온그룹 회장은 정기 주주총회에서 '목표 실적을 달성하도록 최선을 다하겠다'고 말했다."},
]]

# ── 정정이 ──────────────────────────────────────────────────────────────────
RAW += [("정정이","현대해상",None,x) for x in [
  {"title":"[더벨] 현대하임 '목동 시니어', 정정이 대표 역량 시험대","originallink":"https://www.thebell.co.kr/free/content/ArticleView.asp?key=202602251527100320102461","pubDate":"Tue, 03 Mar 2026 11:02:00 +0900","description":"목동예술인회관을 인수해 개발하는 이번 프로젝트는 지난해 6월 취임한 현대가 오너 3세 정정이 대표의 역량을 시험하는 무대가 됐다."},
  {"title":"[2026 뉴리더] 금융권 리더십도 세대교체...2·3세로 권력이동","originallink":"https://www.insightkorea.co.kr/news/articleView.html?idxno=238396","pubDate":"Thu, 01 Jan 2026 07:00:00 +0900","description":"현대해상은 정몽윤 회장이 22%를 보유하고 있고, 정몽윤 회장의 장녀인 정정이 씨는 0.38%를 보유하고 있다."},
]]

# ── 송창현 ──────────────────────────────────────────────────────────────────
RAW += [("송창현","42dot",None,x) for x in [
  {"title":"[신인물탐구(21)] 현대차그룹 정의선 회장 ⑦ 리스크 관리 – 위기를 기회로","originallink":"https://www.news2day.co.kr/article/20260323500137","pubDate":"Tue, 24 Mar 2026 00:32:00 +0900","description":"이날 자율주행 전략을 총괄하던 송창현 사장(42dot 대표 겸 AVP본부장)이 조심스럽게 제안을 꺼냈다. '중국 기술을 도입하자'는 발언이 논란이 됐다."},
  {"title":"[Invest] 2007년 아이폰과 비교되는 테슬라 FSD…'갤럭시' 만들어내야","originallink":"https://www.investchosun.com/site/data/html_dir/2026/03/18/2026031880208.html","pubDate":"Thu, 19 Mar 2026 07:02:00 +0900","description":"현대차그룹에선 자율주행 기술을 이끌던 송창현 전 42dot 대표 겸 AVP본부장이 사임했다. 그룹 차원에서 독자 자율주행 전략 재검토가 이뤄지고 있다."},
  {"title":"[전기차 전환을 넘어 모빌리티 혁명으로 (8)] 현대차그룹의 자율주행 과제","originallink":"https://www.news2day.co.kr/article/20260301500027","pubDate":"Mon, 02 Mar 2026 00:32:00 +0900","description":"42dot 소프트웨어 적용을 가속하는 것이 현실적인 경로다. 송창현 전 사장이 사임 직후 '레거시 산업과 수없이 충돌했다'고 밝혔다."},
  {"title":"현대차-엔비디아, 자율주행까지 '동맹 가속화'","originallink":"http://www.seoulwire.com/news/articleView.html?idxno=706409","pubDate":"Wed, 11 Feb 2026 13:06:00 +0900","description":"현대차그룹은 최근 송창현 전 포티투닷(42dot) 사장 경질을 계기로 독자 자율주행 노선을 재검토하고 있다."},
  {"title":"\"자동차의 개념이 바뀔 원년 될까?\"…대격변이 예고된 2026년의 자율주행","originallink":"https://www.epnc.co.kr/news/articleView.html?idxno=328061","pubDate":"Tue, 03 Feb 2026 08:00:00 +0900","description":"2021년 네이버 CTO 출신 송창현 사장이 자진 사임하면서 포티투닷(42dot)의 수장이 교체되고 새로운 리더십이 출범했다."},
  {"title":"현대차그룹, 알파마요 협력 염두 '포티투닷' 역할 재정립 주목","originallink":"http://www.edaily.co.kr/news/newspath.asp?newsid=01718726645320016","pubDate":"Wed, 21 Jan 2026 06:01:00 +0900","description":"현대차그룹은 송창현 전 AVP 본부장이 사임하기 이전부터 내부에 VLA 조직을 꾸리고, 엔비디아와의 협력을 강화해왔다."},
  {"title":"[더벨][현대차 SDV 로드맵 점검]'움직이는 컴퓨터' 진화...미래차 패권 경쟁","originallink":"https://www.thebell.co.kr/free/content/ArticleView.asp?key=202601131512025560104112","pubDate":"Mon, 19 Jan 2026 08:38:00 +0900","description":"현대차는 2022년 네이버 CTO 출신 송창현 대표가 이끄는 포티투닷을 중심으로 SDV 전략을 추진해왔다."},
  {"title":"현대차, 자율주행 내재화 가속…포티투닷·모셔널 결합 주목","originallink":"https://www.pinpointnews.co.kr/news/articleView.html?idxno=417676","pubDate":"Fri, 16 Jan 2026 08:06:00 +0900","description":"지난해 12월 사임 의사를 밝힌 송창현 전 대표의 퇴진은 자율주행 성과 부진에 대한 책임론과 연관된 것으로 평가된다."},
  {"title":"\"매출 10배가 적자\"···벼랑 끝 포티투닷, '송창현 지우기' 나선 박민우","originallink":"http://www.fnnews.com/news/202603060000000000","pubDate":"Fri, 06 Mar 2026 00:00:00 +0900","description":"포티투닷의 누적 적자가 계속되는 가운데, 신임 박민우 사장이 전임 송창현 체제의 색깔을 지우고 새 방향성을 제시하고 있다."},
]]

# ── 처리 & 저장 ──────────────────────────────────────────────────────────────
import re as _re, html as _html

def strip(s):
    s = _re.sub(r'<[^>]+>', '', s)
    return _html.unescape(s).strip()

MONTHS = {
    'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',
    'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'
}

def parse_pub(pd):
    try:
        parts = pd.split(', ')[1].split(' ')
        day, mon, year = parts[0], parts[1], parts[2]
        return f"{year}.{MONTHS[mon]}.{day.zfill(2)}"
    except:
        return ""

results = []
for name, desc, title_filter, item in RAW:
    title = strip(item.get("title",""))
    date  = parse_pub(item.get("pubDate",""))
    if not date.startswith("2026") and not date.startswith("2025"):
        continue
    if title_filter and title_filter not in title:
        continue
    results.append({
        "name": name,
        "description": desc,
        "title": title,
        "href": item.get("originallink", item.get("link","")),
        "date": date,
        "press": "",
        "summary": strip(item.get("description",""))[:200],
    })

with open("c:\\Users\\michelle\\projects\\고객 뉴스\\mcp_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"MCP 결과 저장: {len(results)}건 → mcp_results.json")
for name in ["이하늬","이혜영","권오경","김병주","서정진","정정이","송창현"]:
    cnt = sum(1 for r in results if r["name"]==name)
    print(f"  {name}: {cnt}건")

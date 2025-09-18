import sqlite3
import sys
import requests
from bs4 import BeautifulSoup
import certifi
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def add_verse(reference: str, content: str):
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO bible_verses (reference, content) VALUES (?, ?)",
        (reference, content)
    )
    conn.commit()
    rowcount = c.rowcount
    conn.close()
    if rowcount:
        print(f"구절이 추가되었습니다: {reference}")
        return True
    else:
        print(f"[중복] 이미 존재하는 구절: {reference}")
        return False

def search_verses(keyword: str, book: str = None):
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    if book:
        c.execute("SELECT reference, content FROM bible_verses WHERE reference LIKE ? AND (reference LIKE ? OR content LIKE ?)", (f"{book}%", f"%{keyword}%", f"%{keyword}%"))
    else:
        c.execute("SELECT reference, content FROM bible_verses WHERE reference LIKE ? OR content LIKE ?", (f"%{keyword}%", f"%{keyword}%"))
    results = c.fetchall()
    conn.close()
    return results

def crawl_biblegateway(query: str, version: str = 'KLB'):
    # biblegateway.com에서 지정 버전으로 검색
    url = f"https://www.biblegateway.com/quicksearch/?quicksearch={query}&version={version}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for result in soup.select('.bible-item'):
            ref = result.select_one('.bible-item-title')
            content = result.select_one('.bible-item-text')
            if ref and content:
                ref_text = ref.get_text(strip=True)
                content_text = content.get_text(strip=True)
                results.append((ref_text, content_text))
        if not results:
            for result in soup.select('.result-text-style-normal'):
                ref = result.find_previous('a', class_='bible-item-title')
                ref_text = ref.get_text(strip=True) if ref else query
                content_text = result.get_text(strip=True)
                results.append((ref_text, content_text))
        return results
    except Exception as e:
        print(f"[인터넷 검색 오류] {e}")
        return []

def crawl_bibleorkr(query: str):
    # bible.or.kr에서 개역개정으로 검색
    url = f"https://www.bible.or.kr/Bible/quicksearch_result.php?version=KRV&keyword={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for row in soup.select('div.bible_list > ul > li'):
            ref = row.select_one('span.bible_list_tit')
            content = row.select_one('span.bible_list_con')
            if ref and content:
                ref_text = ref.get_text(strip=True)
                content_text = content.get_text(strip=True)
                if (ref_text, content_text) not in results:
                    results.append((ref_text, content_text))
        return results
    except Exception as e:
        print(f"[bible.or.kr 검색 오류] {e}")
        return []

def crawl_biblesearch(query: str):
    url = f"https://biblesearch.co.kr/search/?q={urllib.parse.quote(query)}&version=개역개정"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for row in soup.select('div.verse-list > div.verse-item'):
            ref = row.select_one('span.verse-ref')
            content = row.select_one('span.verse-text')
            if ref and content:
                ref_text = ref.get_text(strip=True)
                content_text = content.get_text(strip=True)
                if (ref_text, content_text) not in results:
                    results.append((ref_text, content_text))
        return results
    except Exception as e:
        print(f"[biblesearch.co.kr 검색 오류] {e}")
        return []

def crawl_biblecokr(query: str):
    # bible.co.kr에서 개역개정으로 검색
    q = urllib.parse.quote(query)
    url = f"https://www.bible.co.kr/kr/search/keyword?q={q}&version=개역개정"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.bible.co.kr/"
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for row in soup.select('div.search-result-list > ul > li'):
            ref = row.select_one('span.search-result-verse')
            content = row.select_one('span.search-result-text')
            if ref and content:
                ref_text = ref.get_text(strip=True)
                content_text = content.get_text(strip=True)
                if (ref_text, content_text) not in results:
                    results.append((ref_text, content_text))
        return results
    except Exception as e:
        print(f"[bible.co.kr 검색 오류] {e}")
        return []

def crawl_biblecokr_selenium(query: str):
    results = []
    options = Options()
    # options.add_argument('--headless')  # 창을 띄우지 않고 실행하려면 주석 해제
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        url = f"https://www.bible.co.kr/kr/search/keyword?q={query}&version=개역개정"
        driver.get(url)
        # 검색 결과가 나타날 때까지 최대 10초 대기
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.search-result-list ul li'))
            )
        except Exception:
            pass
        items = driver.find_elements(By.CSS_SELECTOR, 'div.search-result-list ul li')
        for item in items:
            try:
                ref = item.find_element(By.CSS_SELECTOR, 'span.search-result-verse').text.strip()
                content = item.find_element(By.CSS_SELECTOR, 'span.search-result-text').text.strip()
                if (ref, content) not in results:
                    results.append((ref, content))
            except Exception:
                continue
    except Exception as e:
        print(f"[bible.co.kr(셀레니움) 검색 오류] {e}")
    finally:
        driver.quit()
    return results

# 성경서별 장 수 딕셔너리 추가
BOOK_CHAPTERS = {
    '창세기': 50, '출애굽기': 40, '레위기': 27, '민수기': 36, '신명기': 34,
    '여호수아': 24, '사사기': 21, '룻기': 4, '사무엘상': 31, '사무엘하': 24,
    '열왕기상': 22, '열왕기하': 25, '역대상': 29, '역대하': 36, '에스라': 10,
    '느헤미야': 13, '에스더': 10, '욥기': 42, '시편': 150, '잠언': 31,
    '전도서': 12, '아가': 8, '이사야': 66, '예레미야': 52, '예레미야애가': 5,
    '에스겔': 48, '다니엘': 12, '호세아': 14, '요엘': 3, '아모스': 9,
    '오바댜': 1, '요나': 4, '미가': 7, '나훔': 3, '하박국': 3,
    '스바냐': 3, '학개': 2, '스가랴': 14, '말라기': 4,
    '마태복음': 28, '마가복음': 16, '누가복음': 24, '요한복음': 21,
    '사도행전': 28, '로마서': 16, '고린도전서': 16, '고린도후서': 13, '갈라디아서': 6,
    '에베소서': 6, '빌립보서': 4, '골로새서': 4, '데살로니가전서': 5, '데살로니가후서': 3,
    '디모데전서': 6, '디모데후서': 4, '디도서': 3, '빌레몬서': 1, '히브리서': 13,
    '야고보서': 5, '베드로전서': 5, '베드로후서': 3, '요한일서': 5, '요한이서': 1,
    '요한삼서': 1, '유다서': 1, '요한계시록': 22
}

def main():
    print("\n=== 성경 구절 추가 프로그램 (검색/인터넷/추가) ===")
    print("종료하려면 'q' 또는 'quit'를 입력하세요.")
    # 버전 선택
    versions = [
        ("KLB", "우리말성경"),
        ("KRV", "개역한글"),
        ("KOR", "개역개정"),
        ("NIV", "NIV"),
        ("KJV", "KJV")
    ]
    print("\n지원 버전:")
    for idx, (code, name) in enumerate(versions, 1):
        print(f"{idx}. {name} ({code})")
    while True:
        vsel = input("\n검색할 성경 버전 번호를 선택하세요 (예: 1): ").strip()
        if vsel.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            return
        if vsel.isdigit() and 1 <= int(vsel) <= len(versions):
            version = versions[int(vsel)-1][0]
            break
        print("올바른 번호를 입력하세요.")
    while True:
        keyword = input("\n검색할 단어나 구절(키워드/참조, 또는 '창세기 전체', 또는 '창세기 사랑')을 입력하세요: ").strip()
        if keyword.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        if not keyword:
            print("검색어를 입력해주세요.")
            continue
        # 성경서 전체 자동 추가 기능
        if keyword.endswith('전체'):
            book = keyword.replace('전체', '').strip()
            if book in BOOK_CHAPTERS:
                chapter_count = BOOK_CHAPTERS[book]
                print(f"\n[{book} 전체 자동 추가 시작] 총 {chapter_count}장...")
                total_added, total_dup = 0, 0
                for chapter in range(1, chapter_count + 1):
                    query = f"{book} {chapter}장"
                    results = crawl_biblegateway(query, version)
                    if not results:
                        print(f"{query}: 구절을 찾지 못함.")
                        continue
                    added, dup = 0, 0
                    for ref, cont in results:
                        if add_verse(ref, cont):
                            added += 1
                        else:
                            dup += 1
                    print(f"{query}: {added}개 추가, {dup}개 중복.")
                    total_added += added
                    total_dup += dup
                print(f"\n[{book} 전체 완료] 총 {total_added}개 추가, {total_dup}개 중복.")
                continue
            else:
                print(f"알 수 없는 성경서: {book}. 지원 목록: {', '.join(BOOK_CHAPTERS.keys())}")
                continue
        # 책 이름 + 키워드 검색 지원
        parts = keyword.split(maxsplit=1)
        if len(parts) == 2 and parts[0] in BOOK_CHAPTERS:
            book, search_kw = parts
        else:
            book, search_kw = None, keyword
        results = search_verses(search_kw, book)
        if results:
            if book:
                print(f"\n[DB 검색 결과] '{book}'에서 '{search_kw}' 관련 구절 {len(results)}개:")
            else:
                print(f"\n[DB 검색 결과] '{search_kw}' 관련 구절 {len(results)}개:")
            for ref, cont in results:
                print(f"\n{ref}\n{cont}")
        else:
            if book:
                print(f"\n[DB 검색 결과] '{book}'에서 '{search_kw}' 관련 구절이 없습니다.")
            else:
                print(f"\n[DB 검색 결과] '{search_kw}' 관련 구절이 없습니다.")
        gw_results = crawl_biblegateway(keyword, version)
        if gw_results:
            print(f"[biblegateway.com({version}) 검색 결과] {len(gw_results)}개:")
            for idx, (ref, cont) in enumerate(gw_results, 1):
                print(f"\n[G{idx}] {ref}\n{cont}")
        all_results = [("G", *r) for r in gw_results]
        if all_results:
            sel = input("\n추가할 구절 번호를 입력하세요(예: G1, 전체 추가: A 또는 ALL, 건너뛰기: 엔터): ").strip().upper()
            if sel in ['A', 'ALL']:
                added, dup = 0, 0
                for ref, cont in gw_results:
                    if add_verse(ref, cont):
                        added += 1
                    else:
                        dup += 1
                print(f"총 {len(gw_results)}개 중 {added}개 추가, {dup}개는 중복으로 건너뜀.")
                continue
            if sel and sel[0] == 'G' and sel[1:].isdigit():
                idx = int(sel[1:]) - 1
                if 0 <= idx < len(gw_results):
                    ref, cont = gw_results[idx]
                    add_verse(ref, cont)
                    continue
        else:
            print("[인터넷에서 관련 구절을 찾지 못했습니다. 직접 입력하세요.")
        add_choice = input("\n직접 새로운 구절을 추가하시겠습니까? (y/n): ").strip().lower()
        if add_choice != 'y':
            continue
        reference = input("추가할 성경 구절의 참조(reference)를 입력하세요: ").strip()
        if reference.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        if not reference:
            print("참조(reference)를 입력해주세요.")
            continue
        content = input("추가할 성경 구절의 내용을 입력하세요: ").strip()
        if content.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        if not content:
            print("내용을 입력해주세요.")
            continue
        add_verse(reference, content)

if __name__ == "__main__":
    main() 
import csv
import sys
import google.generativeai as genai
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def load_verses():
    verses = []
    try:
        with open('bible_verses.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 2:
                    verses.append({
                        'reference': row[0],
                        'content': row[1]
                    })
    except FileNotFoundError:
        print("Error: bible_verses.csv 파일을 찾을 수 없습니다.")
        sys.exit(1)
    return verses

def search_verses(verses: List[Dict], keyword: str) -> List[Dict]:
    """키워드로 성경 구절을 검색하는 함수"""
    matching_verses = []
    keyword = keyword.lower()
    
    for verse in verses:
        # 구절 내용과 참조 구절 모두에서 검색
        if (keyword in verse['content'].lower() or 
            keyword in verse['reference'].lower()):
            matching_verses.append(verse)
    
    return matching_verses

def semantic_search_verses(verses: List[Dict], query: str) -> List[Dict]:
    """Gemini를 사용하여 의미론적 검색을 수행하는 함수"""
    try:
        # 모든 구절을 하나의 문자열로 결합
        verses_text = "\n".join([f"{v['reference']}: {v['content']}" for v in verses])
        
        # Gemini 모델 설정
        model = genai.GenerativeModel('gemini-1.0-pro')
        
        # 프롬프트 구성
        prompt = f"""당신은 성경 구절을 검색하는 도우미입니다.
다음 성경 구절들 중에서 '{query}'와 가장 관련이 있는 구절들을 찾아주세요.
구절의 참조와 내용을 함께 알려주세요.

성경 구절들:
{verses_text}

관련된 구절들의 참조만 나열해주세요. 예시:
요한복음 1:1
요한복음 3:16
"""
        
        # Gemini API 호출
        response = model.generate_content(prompt)
        
        # 응답에서 구절 참조 추출
        response_text = response.text
        
        # 응답에서 구절 참조 추출
        matching_verses = []
        for verse in verses:
            if verse['reference'] in response_text:
                matching_verses.append(verse)
        
        return matching_verses
    except Exception as e:
        print(f"Gemini API 호출 중 오류가 발생했습니다: {str(e)}")
        return []

def main():
    verses = load_verses()
    
    print("\n=== 성경 구절 검색 프로그램 ===")
    print("1. 일반 검색")
    print("2. 의미론적 검색 (Gemini)")
    print("종료하려면 'q' 또는 'quit'를 입력하세요.")
    
    while True:
        print("\n검색 모드를 선택하세요 (1 또는 2): ", end='')
        mode = input().strip()
        
        if mode.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if mode not in ['1', '2']:
            print("1 또는 2를 입력해주세요.")
            continue
        
        print("\n검색할 단어나 구절을 입력하세요: ", end='')
        user_input = input().strip()
        
        if user_input.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if not user_input:
            print("검색어를 입력해주세요.")
            continue
        
        if mode == '1':
            matching_verses = search_verses(verses, user_input)
        else:
            matching_verses = semantic_search_verses(verses, user_input)
        
        if matching_verses:
            print(f"\n'{user_input}'과(와) 관련된 성경 구절:")
            for verse in matching_verses:
                print(f"\n{verse['reference']}")
                print(verse['content'])
        else:
            print(f"\n'{user_input}'과(와) 관련된 성경 구절을 찾을 수 없습니다.")

if __name__ == "__main__":
    main() 
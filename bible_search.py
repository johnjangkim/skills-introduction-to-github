import csv
import sys
import os
import google.generativeai as genai
from typing import List, Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
print(f"API Key: {api_key}")
if not api_key:
    print("Error: GOOGLE_API_KEY가 설정되지 않았습니다.")
    print("1. .env 파일을 생성하고 GOOGLE_API_KEY=your_api_key_here 형식으로 API 키를 설정해주세요.")
    print("2. Google AI Studio (https://makersuite.google.com/app/apikey)에서 API 키를 발급받을 수 있습니다.")
    sys.exit(1)

# Configure Gemini API
try:
    genai.configure(api_key=api_key)
    
    # Get the latest Gemini Pro model
    models = [m.name for m in genai.list_models()]
    print("Available models:", models)
    
    # Look for the latest Gemini Pro model
    gemini_model = None
    preferred_models = [
        'models/gemini-1.5-pro-latest',
        'models/gemini-1.5-pro',
        'models/gemini-1.5-pro-001',
        'models/gemini-1.5-pro-002'
    ]
    
    for model_name in preferred_models:
        if model_name in models:
            gemini_model = model_name
            break
            
    if not gemini_model:
        raise ValueError("No suitable Gemini Pro model found. Available models: " + ", ".join(models))
        
    print(f"Using model: {gemini_model}")
    model = genai.GenerativeModel(model_name=gemini_model)
    
except Exception as e:
    print(f"Error: Gemini API 설정 중 오류가 발생했습니다: {str(e)}")
    print(f"API Key: {api_key}")
    sys.exit(1)

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
다음 성경 구절들 중에서 '{query}'와 가장 관련이 있는 구절들을 3개 찾아주세요.
구절의 참조와 내용을 함께 알려주세요.

성경 구절들:
{verses_text}

관련된 구절들의 참조만 나열해주세요. 예시:
요한복음 1:1
요한복음 3:16
John 1:1
John 3:16
"""
        
        # Gemini API 호출
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
        )
        
        # 응답에서 구절 참조 추출
        response_text = response.text
        
        # 응답에서 구절 참조 추출
        matching_verses = []
        for verse in verses:
            if verse['reference'] in response_text:
                matching_verses.append(verse)
        
        return matching_verses
    except Exception as e:
        print(f"API Key: {api_key}")
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
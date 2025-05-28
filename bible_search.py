import csv
import sys

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

def search_verses(verses, keyword):
    """키워드로 성경 구절을 검색하는 함수"""
    matching_verses = []
    keyword = keyword.lower()
    
    for verse in verses:
        # 구절 내용과 참조 구절 모두에서 검색
        if (keyword in verse['content'].lower() or 
            keyword in verse['reference'].lower()):
            matching_verses.append(verse)
    
    return matching_verses

def main():
    verses = load_verses()
    
    print("\n=== 성경 구절 검색 프로그램 ===")
    print("종료하려면 'q' 또는 'quit'를 입력하세요.")
    
    while True:
        print("\n검색할 단어나 구절을 입력하세요: ", end='')
        user_input = input().strip()
        
        if user_input.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if not user_input:
            print("검색어를 입력해주세요.")
            continue
        
        matching_verses = search_verses(verses, user_input)
        
        if matching_verses:
            print(f"\n'{user_input}'이(가) 포함된 성경 구절:")
            for verse in matching_verses:
                print(f"\n{verse['reference']}")
                print(verse['content'])
        else:
            print(f"\n'{user_input}'이(가) 포함된 성경 구절을 찾을 수 없습니다.")

if __name__ == "__main__":
    main() 
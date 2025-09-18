import csv
import sys
import os
# NOTE: Lazy-load google.generativeai inside helper to avoid heavy import at module load
from typing import List, Dict
from dotenv import load_dotenv
import sqlite3

# Lazy Gemini initializer
_gemini_preferred_models = [
    'models/gemini-1.5-pro-latest',
    'models/gemini-1.5-pro',
    'models/gemini-1.5-pro-001',
    'models/gemini-1.5-pro-002'
]

def _get_gemini_model():
    try:
        import google.generativeai as genai
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            # Fallback: try reading from local file (for mobile packaging)
            try:
                with open('api_key.txt', 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
            except Exception:
                api_key = None
        if not api_key:
            return None
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models()]
        for name in _gemini_preferred_models:
            if name in models:
                return genai.GenerativeModel(model_name=name)
        return None
    except Exception:
        return None

def init_db():
    # DB 파일이 없으면 생성하고, 테이블이 없으면 생성
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bible_verses (
        reference TEXT PRIMARY KEY,
        content TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# CSV에서 DB로 데이터 마이그레이션 (최초 1회만 필요)
def migrate_csv_to_db():
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    with open('bible_verses.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 2:
                c.execute('INSERT OR IGNORE INTO bible_verses (reference, content) VALUES (?, ?)', (row[0], row[1]))
    conn.commit()
    conn.close()

# DB에서 구절 불러오기
def load_verses():
    verses = []
    try:
        conn = sqlite3.connect('bible_verses.db')
        c = conn.cursor()
        for row in c.execute('SELECT reference, content FROM bible_verses'):
            verses.append({'reference': row[0], 'content': row[1]})
        conn.close()
    except Exception as e:
        print(f"Error: bible_verses.db 파일을 찾을 수 없거나 읽을 수 없습니다. {e}")
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
        model = _get_gemini_model()
        if model is None:
            return []
        verses_text = "\n".join([f"{v['reference']}: {v['content']}" for v in verses])
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
        response = model.generate_content(
            prompt
        )
        response_text = getattr(response, 'text', '') or ''
        matching_verses = []
        for verse in verses:
            if verse['reference'] in response_text:
                matching_verses.append(verse)
        return matching_verses
    except Exception:
        return []

def add_verse(reference: str, content: str):
    """DB에 새로운 성경 구절을 추가하는 함수"""
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO bible_verses (reference, content) VALUES (?, ?)",
        (reference, content)
    )
    conn.commit()
    conn.close()
    print(f"구절이 추가되었습니다: {reference}")

def show_all_verses():
    """DB에 저장된 모든 성경 구절을 출력하는 함수"""
    conn = sqlite3.connect('bible_verses.db')
    c = conn.cursor()
    c.execute('SELECT reference, content FROM bible_verses ORDER BY reference')
    verses = c.fetchall()
    conn.close()
    if not verses:
        print("DB에 저장된 성경 구절이 없습니다.")
        return
    print(f"\n=== DB에 저장된 모든 성경 구절 ({len(verses)}개) ===")
    for ref, cont in verses:
        print(f"\n{ref}")
        print(cont)

def add_major_verses_korean():
    verses = [
        ("마태복음 5:3", "심령이 가난한 자는 복이 있나니 천국이 그들의 것임이요"),
        ("마태복음 5:9", "화평하게 하는 자는 복이 있나니 그들이 하나님의 아들이라 일컬음을 받을 것임이요"),
        ("마태복음 6:33", "너희는 먼저 그의 나라와 그의 의를 구하라 그리하면 이 모든 것을 너희에게 더하시리라"),
        ("마태복음 7:7", "구하라 그리하면 너희에게 주실 것이요 찾으라 그리하면 찾아낼 것이요 문을 두드리라 그리하면 너희에게 열릴 것이니"),
        ("마태복음 11:28", "수고하고 무거운 짐 진 자들아 다 내게로 오라 내가 너희를 쉬게 하리라"),
        ("마태복음 16:16", "시몬 베드로가 대답하여 이르되 주는 그리스도시요 살아 계신 하나님의 아들이시니이다"),
        ("마태복음 22:37", "예수께서 이르시되 네 마음을 다하고 목숨을 다하고 뜻을 다하여 주 너의 하나님을 사랑하라 하셨으니"),
        ("마태복음 28:19", "그러므로 너희는 가서 모든 민족을 제자로 삼아 아버지와 아들과 성령의 이름으로 세례를 베풀고"),
        ("마가복음 9:23", "예수께서 이르시되 할 수 있거든이 무슨 말이냐 믿는 자에게는 능히 하지 못할 일이 없느니라"),
        ("마가복음 10:45", "인자가 온 것은 섬김을 받으려 함이 아니라 도리어 섬기려 하고 자기 목숨을 많은 사람의 대속물로 주려 함이니라"),
        ("누가복음 6:31", "남에게 대접을 받고자 하는 대로 너희도 남을 대접하라"),
        ("누가복음 9:23", "또 무리에게 이르시되 아무든지 나를 따라오려거든 자기를 부인하고 날마다 제 십자가를 지고 나를 따를 것이니라"),
        ("누가복음 19:10", "인자가 온 것은 잃어버린 자를 찾아 구원하려 함이니라"),
        ("요한복음 1:1", "태초에 말씀이 계시니라 이 말씀이 하나님과 함께 계셨으니 이 말씀은 곧 하나님이시니라"),
        ("요한복음 1:14", "말씀이 육신이 되어 우리 가운데 거하시매 우리가 그의 영광을 보니 아버지의 독생자의 영광이요 은혜와 진리가 충만하더라"),
        ("요한복음 3:16", "하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라"),
        ("요한복음 5:24", "내 말을 듣고 또 나를 보내신 이를 믿는 자는 영생을 얻었고 심판에 이르지 아니하나니 사망에서 생명으로 옮겼느니라"),
        ("요한복음 8:12", "나는 세상의 빛이니 나를 따르는 자는 어둠에 다니지 아니하고 생명의 빛을 얻으리라"),
        ("요한복음 11:25", "나는 부활이요 생명이니 나를 믿는 자는 죽어도 살겠고"),
        ("요한복음 13:34", "새 계명을 너희에게 주노니 서로 사랑하라 내가 너희를 사랑한 것 같이 너희도 서로 사랑하라"),
        ("요한복음 14:6", "내가 곧 길이요 진리요 생명이니 나로 말미암지 않고는 아버지께로 올 자가 없느니라"),
        ("요한복음 14:27", "평안을 너희에게 끼치노니 곧 나의 평안을 너희에게 주노라"),
        ("요한복음 15:5", "나는 포도나무요 너희는 가지라 그가 내 안에 내가 그 안에 거하면 사람이 열매를 많이 맺나니 나를 떠나서는 너희가 아무것도 할 수 없음이라"),
        ("요한복음 16:33", "이것을 너희에게 이르는 것은 너희로 내 안에서 평안을 누리게 하려 함이라 세상에서는 너희가 환난을 당하나 담대하라 내가 세상을 이기었노라"),
        ("사도행전 1:8", "오직 성령이 너희에게 임하시면 너희가 권능을 받고 예루살렘과 온 유대와 사마리아와 땅 끝까지 이르러 내 증인이 되리라 하시니라"),
        ("로마서 1:16", "내가 복음을 부끄러워하지 아니하노니 이 복음은 모든 믿는 자에게 구원을 주시는 하나님의 능력이 됨이라"),
        ("로마서 3:23", "모든 사람이 죄를 범하였으매 하나님의 영광에 이르지 못하더니"),
        ("로마서 5:8", "우리가 아직 죄인 되었을 때에 그리스도께서 우리를 위하여 죽으심으로 하나님께서 우리에 대한 자기의 사랑을 확증하셨느니라"),
        ("로마서 6:23", "죄의 삯은 사망이요 하나님의 은사는 그리스도 예수 우리 주 안에 있는 영생이니라"),
        ("로마서 8:1", "그러므로 이제 그리스도 예수 안에 있는 자에게는 결코 정죄함이 없나니"),
        ("로마서 8:28", "우리가 알거니와 하나님을 사랑하는 자 곧 그의 뜻대로 부르심을 입은 자들에게는 모든 것이 합력하여 선을 이루느니라"),
        ("로마서 10:9", "네가 만일 네 입으로 예수를 주로 시인하며 또 하나님께서 그를 죽은 자 가운데서 살리신 것을 네 마음에 믿으면 구원을 받으리라"),
        ("로마서 12:2", "이 세대를 본받지 말고 오직 마음을 새롭게 함으로 변화를 받아"),
        ("고린도전서 10:13", "사람이 감당할 시험 밖에는 너희가 당한 것이 없나니"),
        ("고린도전서 13:4", "사랑은 오래 참고 사랑은 온유하며 시기하지 아니하며 사랑은 자랑하지 아니하며 교만하지 아니하며"),
        ("고린도전서 13:13", "그런즉 믿음, 소망, 사랑 이 세 가지는 항상 있을 것인데 그 중의 제일은 사랑이라"),
        ("고린도후서 5:17", "누구든지 그리스도 안에 있으면 새로운 피조물이라 이전 것은 지나갔으니 보라 새 것이 되었도다"),
        ("갈라디아서 2:20", "내가 그리스도와 함께 십자가에 못 박혔나니 그런즉 이제는 내가 사는 것이 아니요 오직 내 안에 그리스도께서 사시는 것이라"),
        ("갈라디아서 5:22", "오직 성령의 열매는 사랑과 희락과 화평과 오래 참음과 자비와 양선과 충성과"),
        ("에베소서 2:8", "너희는 그 은혜에 의하여 믿음으로 말미암아 구원을 받았으니 이것은 너희에게서 난 것이 아니요 하나님의 선물이라"),
        ("에베소서 4:32", "서로 친절하게 하며 불쌍히 여기며 서로 용서하기를 하나님이 그리스도 안에서 너희를 용서하신 것 같이 하라"),
        ("빌립보서 1:6", "너희 안에서 착한 일을 시작하신 이가 그리스도 예수의 날까지 이루실 줄을 우리는 확신하노라"),
        ("빌립보서 4:6", "아무것도 염려하지 말고 오직 모든 일에 기도와 간구로 너희 구할 것을 감사함으로 하나님께 아뢰라"),
        ("빌립보서 4:13", "내게 능력 주시는 자 안에서 내가 모든 것을 할 수 있느니라"),
        ("골로새서 3:23", "무슨 일을 하든지 마음을 다하여 주께 하듯 하고 사람에게 하듯 하지 말라"),
        ("데살로니가전서 5:16", "항상 기뻐하라"),
        ("데살로니가전서 5:17", "쉬지 말고 기도하라"),
        ("데살로니가전서 5:18", "범사에 감사하라 이것이 그리스도 예수 안에서 너희를 향하신 하나님의 뜻이니라"),
        ("디모데후서 3:16", "모든 성경은 하나님의 감동으로 된 것으로 교훈과 책망과 바르게 함과 의로 교육하기에 유익하니"),
        ("히브리서 4:12", "하나님의 말씀은 살아 있고 활력이 있어 좌우에 날선 어떤 검보다도 예리하여"),
        ("히브리서 11:1", "믿음은 바라는 것들의 실상이요 보이지 않는 것들의 증거니"),
        ("야고보서 1:5", "너희 중에 누구든지 지혜가 부족하거든 모든 사람에게 후히 주시고 꾸짖지 아니하시는 하나님께 구하라 그리하면 주시리라"),
        ("야고보서 1:22", "너희는 말씀을 행하는 자가 되고 듣기만 하여 자신을 속이는 자가 되지 말라"),
        ("베드로전서 5:7", "너희 염려를 다 주께 맡기라 이는 그가 너희를 돌보심이라"),
        ("요한일서 1:9", "만일 우리가 우리 죄를 자백하면 그는 미쁘시고 의로우사 우리 죄를 사하시며 우리를 모든 불의에서 깨끗하게 하실 것이요"),
        ("요한일서 4:7", "사랑하는 자들아 우리가 서로 사랑하자 사랑은 하나님께 속한 것이니"),
        ("요한일서 4:19", "우리가 사랑함은 그가 먼저 우리를 사랑하셨음이라"),
        # ... (이하 100개로 확장, 필요시 추가)
    ]
    for ref, cont in verses:
        add_verse(ref, cont)
    print(f"{len(verses)}개의 주요 신약성경 구절이 DB에 추가되었습니다.")

def main():
    verses = load_verses()
    
    print("\n=== 성경 구절 검색 프로그램 ===")
    print("1. 일반 검색")
    print("2. 의미론적 검색 (Gemini)")
    print("3. 성경 구절 추가")
    print("4. 모든 성경 구절 조회")
    print("종료하려면 'q' 또는 'quit'를 입력하세요.")
    
    while True:
        print("\n검색 모드를 선택하세요 (1, 2, 3 또는 4): ", end='')
        mode = input().strip()
        
        if mode.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if mode not in ['1', '2', '3', '4']:
            print("1, 2, 3 또는 4를 입력해주세요.")
            continue
        
        if mode == '3':
            print("\n추가할 성경 구절의 참조(reference)를 입력하세요: ", end='')
            reference = input().strip()
            if not reference:
                print("참조(reference)를 입력해주세요.")
                continue
            print("추가할 성경 구절의 내용을 입력하세요: ", end='')
            content = input().strip()
            if not content:
                print("내용을 입력해주세요.")
                continue
            add_verse(reference, content)
            continue
        
        if mode == '4':
            show_all_verses()
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
    init_db()
    # 아래 함수는 최초 1회만 실행하세요. (중복 입력 방지)
    add_major_verses_korean()
    # migrate_csv_to_db()  # 최초 1회만 실행 후 주석처리
    main() 
import os
import google.generativeai as genai
from dotenv import load_dotenv

def initialize_gemini():
    """Initialize the Gemini model with API key."""
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=api_key)
    
    try:
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
                print("#####")
                print(gemini_model)
                print("#####")
                break
                
        if not gemini_model:
            raise ValueError("No suitable Gemini Pro model found. Available models: " + ", ".join(models))
            
        print(f"Using model: {gemini_model}")
        return genai.GenerativeModel(model_name=gemini_model)
        
    except Exception as e:
        raise Exception(f"Error initializing Gemini: {str(e)}")

def chat_with_bible_character(model, character_name):
    """Start a chat session with the selected biblical character."""
    # Create character prompt
    character_prompts = {
        '베드로': '당신은 베드로입니다. 열정적이고 충성스러운 제자로서, 때로는 실수도 하지만 항상 회개하고 다시 일어서는 모습을 보여주는 인물입니다.',
        '바울': '당신은 바울입니다. 철저한 학자이자 열정적인 전도자로서, 그리스도 안에서의 새로운 삶을 강조하는 인물입니다.',
        '마리아': '당신은 마리아입니다. 하나님의 은혜를 깊이 묵상하고, 겸손하게 섬기는 인물입니다.',
        '예수님': '당신은 예수님입니다. 비유를 통해 깊은 진리를 전하시는 분입니다.'
    }

    if character_name not in character_prompts:
        print(f"사용 가능한 캐릭터: {', '.join(character_prompts.keys())}")
        return

    # Start chat
    chat = model.start_chat(history=[])
    character_prompt = character_prompts[character_name]
    
    print(f"\n{character_name}과의 대화를 시작합니다. (종료하려면 'quit' 또는 'exit'를 입력하세요)")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("\n나: ").strip()
        
        # Check for exit command
        if user_input.lower() in ['quit', 'exit']:
            print(f"\n{character_name}과의 대화를 종료합니다.")
            break
        
        if not user_input:
            continue

        try:
            # Prepare the prompt with character context
            full_prompt = f"{character_prompt}\n\n사용자: {user_input}\n\n위의 메시지에 캐릭터의 관점에서 답변해주세요."
            
            # Get response from Gemini
            response = chat.send_message(full_prompt)
            print(f"\n{character_name}: {response.text}")
            
        except Exception as e:
            print(f"\n오류가 발생했습니다: {str(e)}")

def main():
    """Main function to run the chatbot."""
    try:
        # Initialize Gemini
        print("Bible Mentor - 성경 인물과의 대화")
        print("초기화 중...")
        model = initialize_gemini()
        
        # Character selection
        print("\n대화할 성경 인물을 선택하세요:")
        characters = ['베드로', '바울', '마리아', '예수님']
        for i, name in enumerate(characters, 1):
            print(f"{i}. {name}")
        
        while True:
            try:
                choice = int(input("\n번호를 선택하세요 (1-4): "))
                if 1 <= choice <= 4:
                    character_name = characters[choice - 1]
                    break
                else:
                    print("1에서 4 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
        
        # Start chat with selected character
        chat_with_bible_character(model, character_name)
        
    except Exception as e:
        print(f"\n프로그램 오류: {str(e)}")
        print("프로그램을 종료합니다.")

if __name__ == "__main__":
    main()

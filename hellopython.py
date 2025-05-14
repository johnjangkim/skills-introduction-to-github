def calculator():
    print("간단한 계산기입니다.")
    print("1. 덧셈")
    print("2. 뺄셈")
    print("3. 곱셈")
    print("4. 나눗셈")
    
    while True:
        try:
            # 연산 선택
            choice = input("\n원하는 연산을 선택하세요 (1-4): ")
            
            if choice not in ['1', '2', '3', '4']:
                print("1부터 4까지의 숫자만 입력해주세요.")
                continue
                
            # 숫자 입력
            num1 = float(input("첫 번째 숫자를 입력하세요: "))
            num2 = float(input("두 번째 숫자를 입력하세요: "))
            
            # 계산 수행
            if choice == '1':
                result = num1 + num2
                print(f"\n{num1} + {num2} = {result}")
            elif choice == '2':
                result = num1 - num2
                print(f"\n{num1} - {num2} = {result}")
            elif choice == '3':
                result = num1 * num2
                print(f"\n{num1} × {num2} = {result}")
            elif choice == '4':
                if num2 == 0:
                    print("\n0으로는 나눌 수 없습니다.")
                    continue
                result = num1 / num2
                print(f"\n{num1} ÷ {num2} = {result}")
            
            # 계속할지 물어보기
            again = input("\n다시 계산하시겠습니까? (y/n): ")
            if again.lower() != 'y':
                print("\n계산기를 종료합니다.")
                break
                
        except ValueError:
            print("\n올바른 숫자를 입력해주세요.")
        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")

if __name__ == "__main__":
    calculator()

import csv
import sys

def load_recipes():
    recipes = []
    try:
        with open('recipes.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 8:  # Ensure row has enough columns
                    recipes.append({
                        'name': row[0],
                        'type': row[1],
                        'ingredients': row[2:8]
                    })
    except FileNotFoundError:
        print("Error: recipes.csv 파일을 찾을 수 없습니다.")
        sys.exit(1)
    return recipes

def find_recipes_by_ingredient(recipes, ingredient):
    """특정 재료가 포함된 요리를 찾는 함수"""
    matching_recipes = []
    seen_ingredients = set()  # Track unique ingredient combinations
    ingredient = ingredient.lower()
    
    print(f"\n[DEBUG] Searching for ingredient: {ingredient}")
    
    for recipe in recipes:
        # Convert all ingredients to lowercase and sort them
        recipe_ingredients = [ing.lower() for ing in recipe['ingredients'] if ing]
        recipe_ingredients.sort()
        ingredients_tuple = tuple(recipe_ingredients)
        
        print(f"\n[DEBUG] Processing recipe: {recipe['name']}")
        print(f"[DEBUG] Ingredients: {recipe_ingredients}")
        
        # Check if the ingredient is in any of the recipe's ingredients
        if any(ingredient in ing.lower() for ing in recipe['ingredients'] if ing):
            print(f"[DEBUG] Found matching ingredient in {recipe['name']}")
            # Only add if we haven't seen this combination of ingredients before
            if ingredients_tuple not in seen_ingredients:
                print(f"[DEBUG] Adding new unique recipe: {recipe['name']}")
                matching_recipes.append(recipe)
                seen_ingredients.add(ingredients_tuple)
            else:
                print(f"[DEBUG] Skipping duplicate recipe: {recipe['name']}")
    
    print(f"\n[DEBUG] Total unique recipes found: {len(matching_recipes)}")
    return matching_recipes

def main():
    recipes = load_recipes()
    
    print("\n=== 요리 검색 프로그램 ===")
    print("종료하려면 'q' 또는 'quit'를 입력하세요.")
    
    while True:
        print("\n검색할 재료를 입력하세요: ", end='')
        user_input = input().strip()
        
        if user_input.lower() in ['q', 'quit']:
            print("프로그램을 종료합니다.")
            break
        
        if not user_input:
            print("재료를 입력해주세요.")
            continue
        
        matching_recipes = find_recipes_by_ingredient(recipes, user_input)
        
        if matching_recipes:
            print(f"\n'{user_input}'이(가) 포함된 요리 목록:")
            for recipe in matching_recipes:
                print(f"\n요리명: {recipe['name']}")
                print(f"종류: {recipe['type']}")
                print("재료:", ", ".join(recipe['ingredients']))
        else:
            print(f"\n'{user_input}'이(가) 포함된 요리를 찾을 수 없습니다.")

if __name__ == "__main__":
    main()

import random

allowed = ["celery", "gluten", "crustacean", "eggs", "fish",
           "lupin", "dairy", "mollusc", "mustard", "peanuts",
            "sesame", "soy", "sulphur dioxide", "sulphites", "tree nuts"]

def get_allergens(text):
    food_allergens = []
    for line in text:
        allergen_array = []
        num = random.randint(0,3)
        for i in range(num):
            allergen_array.append(random.choice(allowed))
        food_allergens.append({
            "text" : line,
            "allergens" : allergen_array
        })
    return food_allergens



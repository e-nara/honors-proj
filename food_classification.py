import random

allowed = ["celery", "gluten", "crustacean", "eggs", "fish",
           "lupin", "dairy", "mollusc", "mustard", "peanuts",
            "sesame", "soy", "sulphur dioxide", "sulphites", "tree nuts"]

def get_allergens(text):
    food_allergens = []
    for line in text:
        food_allergens.append({
            "text" : line,
            "allergen" : random.choice(allowed)
        })
    return food_allergens



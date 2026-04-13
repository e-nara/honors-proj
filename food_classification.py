import random
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sklearn.pipeline import Pipeline, FeatureUnion

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[,;:()\-\/]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

allowed = ["celery", "gluten", "crustacean", "eggs", "fish",
           "lupin", "dairy", "mollusc", "mustard", "peanuts",
            "sesame", "soy", "sulphur dioxide", "sulphites", "tree nuts"]

classes = ['celery', 'crustacean', 'dairy', 'eggs', 'fish', 'gluten', 'lupin', 'mustard',
 'peanuts', 'sesame', 'soy', 'tree nuts']

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

def predict_allergens(text):

    model = pickle.load(open('model.pickle','rb')) #pretrained classifier
    combined = pickle.load(open('combined.pickle', 'rb')) #prefitted tf-idf vectoriser
    
    food_allergens = []

    for line in text:
        new_sentences = [line]
        new_sentence_tfidf = combined.transform(new_sentences)
        #probas = model.predict_proba(new_sentence_tfidf)

        predicted_sentences = model.predict(new_sentence_tfidf)
        #proba_sentence = model.predict_proba(new_sentence_tfidf)
        decoded = [classes[i] for i, val in enumerate(predicted_sentences[0]) if (val == 1).any()]
        
        food_allergens.append({
            "text" : line,
            "allergens" : decoded
        })
    
    return food_allergens



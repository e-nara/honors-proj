import random
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from sklearn.pipeline import Pipeline, FeatureUnion

import spacy
import re
nlp = spacy.load("en_core_web_sm")

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

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

custom_stop_words = ['oil', 'extract', 'essence', 'paste', 'sauce', 'powder'] #add more as necessary

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[,;:()\-\/]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def lemmatize(text):
    doc = nlp(text)
    return " ".join(token.lemma_ for token in doc if not token.is_space)

def pre_process(list):
    food = [lemmatize(item) for item in list]
    cleaned = [clean_text(item) for item in food]
    filtered = []
    for string in cleaned:
        tokens = word_tokenize(string)
        filtered_tokens = [word for word in tokens if word not in stop_words]
        custom_swr = [word for word in filtered_tokens if word not in custom_stop_words]
        filtered_str = " ".join(custom_swr)
        filtered.append(filtered_str)
    #print(filtered)
    return filtered
#food = [lemmatize(item) for item in food]

def predict_allergens(text):

    model = pickle.load(open('model.pickle','rb')) #pretrained classifier
    combined = pickle.load(open('combined.pickle', 'rb')) #prefitted tf-idf vectoriser
    ocr_text = text
    text = pre_process(text)
    
    food_allergens = []

    for i, line in enumerate(text):
        new_sentences = [line]
        new_sentence_tfidf = combined.transform(new_sentences)
        #probas = model.predict_proba(new_sentence_tfidf)

        predicted_sentences = model.predict(new_sentence_tfidf)
        #proba_sentence = model.predict_proba(new_sentence_tfidf)
        decoded = [classes[i] for i, val in enumerate(predicted_sentences[0]) if (val == 1).any()]
        
        food_allergens.append({
            "text" : ocr_text[i],
            "allergens" : decoded
        })
    
    return food_allergens



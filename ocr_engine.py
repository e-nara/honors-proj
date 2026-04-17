import easyocr
import cv2 as cv
import numpy as np
import os
import re

# code from https://stackoverflow.com/questions/76723117/divide-an-image-into-tiles-based-on-text-structure-in-python-opencv

def to_rect(box):
    xlist = [p[0] for p in box] #0 = x coordinates
    ylist = [p[1] for p in box] #1 = y coordinates
    return {
        "left": min(xlist),
        "right": max(xlist),
        "top": min(ylist),
        "bottom": max(ylist),
        "height": max(ylist) - min(ylist),
        "width": max(xlist) - min(xlist),
        "center_y": (min(ylist) + max(ylist)) / 2,
        "center_x": (min(xlist) + max(xlist)) / 2
    }


def structure_data(result):
    structured = []
    for bbox, text in result:
        structured.append({
            "rect": to_rect(bbox),
            "text": text
        })

    return structured   

def tokenize_alpha(text):
    # keep only letters and spaces
    cleaned = re.sub(r'[^A-Za-z\s]', '', text)
    # collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

LIST_OF_NON_MENU_KEYWORDS = ['.com', 'london', 'lunch', 'dinner', 'starter', 'main', 'dessert', 'cafe', 'please', 'service charge'] # expand l8r

PRICE_PATTERN = re.compile(r"""
    [£$€EeLlIi{YS]   # currency-like symbol
    \s*
    \d+               # digits
    (\.\d{1,2})?      # optional decimal
""", re.VERBOSE)

def reject_non_menu_items(text):
    if(len(text) > 2):
        if not any(w in text.lower() for w in LIST_OF_NON_MENU_KEYWORDS):
            # only return if the text contains no forbidden key substrings
            return True
    return False

def clean_menu_item(text):
    #print("items before clean", text)
    # remove allergen codes like (G/D/N)
    text = re.sub(r"\(([A-Za-z/]+)\)", "", text)
    #print("text subbed bracket patterns: ", text)

    # remove price-like codes such as E1.99, E3, + E1.99
    text = re.sub(PRICE_PATTERN, "", text)
    #print("text subbed price patterns: ", text)

    # collapse extra spaces created by removals
    text = re.sub(r"\s{2,}", " ", text).strip()
    #print("text subbed extra space: ", text)

    return text

def item_to_text(item):
    return " ".join(b["text"] for b in item)


path = "pariscafe1.jpg"
assert os.path.exists(path)

def run_ocr(path):
    #always a good idea to convert BGR to RGB when using OCR
    img = cv.imread(path)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    #read the text
    reader = easyocr.Reader(['en'])
    text_data = reader.readtext(img, paragraph=True, x_ths=0.5)     #in order ([box-coords], text, confidence)

    #print(text_data)

    rect_data = structure_data(text_data)

    #print(rect_data)

    items = []

    for para in rect_data:
        items.append(para["text"])

    #Dont bother cleaning non-menu items
    non_menu = [t for t in items if reject_non_menu_items(t)]

    clean_items = [clean_menu_item(t) for t in non_menu]
    clean_items = [t for t in clean_items if t.strip()] #remove empty strings
    print(clean_items)

    return(clean_items)
import easyocr
from rapidfuzz import fuzz
import cv2
import re
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import re
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

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

def horizontally_adjacent(a, b):
    # 1. Tight vertical alignment check
    vertical_threshold = min(a["height"], b["height"]) * 0.5
    same_row = abs(a["center_y"] - b["center_y"]) < vertical_threshold
    
    if not same_row:
        return False

    # 2. Horizontal overlap or small gap
    left_a, right_a = a["left"], a["right"]
    left_b, right_b = b["left"], b["right"]

    # Horizontal gap between boxes
    gap = max(0, max(left_b - right_a, left_a - right_b))

    # Allow small gap (e.g., space between words)
    small_gap_threshold = min(a["height"], b["height"]) * 3

    return gap < small_gap_threshold

def same_line(rect_a, rect_b):
    avg_h = (rect_a["height"] + rect_b["height"]) / 2
    return abs(rect_a["center_y"] - rect_b["center_y"]) < avg_h * 0.2

def cluster_columns(line_rects, tolerance=50):
    columns = []
    for rect in line_rects:
        placed = False
        for col in columns:
            if abs(rect["left"] - col["left"]) < tolerance:
                col["lines"].append(rect)
                placed = True
                break
        if not placed:
            columns.append({
                "left": rect["left"],
                "lines": [rect]
            })
    return columns


def structure_data(result):
    structured = []
    for bbox, text, conf in result:
        structured.append({
            "rect": to_rect(bbox),
            "text": text,
            "conf": conf
        })

    return structured    


PRICE_PATTERN = re.compile(r"""
    ^\s*
    [£$€EeLlIi{YS]?        # optional currency-like symbol
    \s*
    \d+                 # digits
    (\.\d{1,2})?        # optional decimal
    \s*$
""", re.VERBOSE)


#k-means clustering for columns: only works for known number of columns
#hierarchical clustering alternative
#alternative: rule based

def compute_line_gaps(lines):
    gaps = []
    for i in range(1, len(lines)):
        prev_bottom = lines[i-1]["bottom"]
        curr_top = lines[i]["top"]
        gaps.append(curr_top - prev_bottom)
    return gaps

def find_gap_threshold(gaps):
    positive = [g for g in gaps if g > 0]
    if not positive:
        return 9999
    median_gap = np.median(positive)
    return median_gap * 1.2

def group_lines_into_items(lines):
    gaps = compute_line_gaps(lines)
    threshold = find_gap_threshold(gaps)

    items = []
    current_item = []

    for i, line in enumerate(lines):
        if i == 0:
            current_item.append(line)
            continue

        if gaps[i-1] > threshold:
            items.append(current_item)
            current_item = [line]
        else:
            current_item.append(line)

    items.append(current_item)
    return items


def item_to_text(item):
    return " ".join(b["text"] for b in item)

def create_lines(structured):
    lines = []
    for obj in structured:
        # skip adding the text if it resembles a price
        if PRICE_PATTERN.match(obj["text"]):
            continue

        placed = False
        for line in lines:
            if horizontally_adjacent(obj["rect"], line[-1]["rect"]):
                #print(line[-1]["text"] + " | " + obj["text"] + " <- same line")
                line.append(obj)
                placed = True
                break
        if not placed:
            lines.append([obj])
    return lines

def clean_lines(lines):
    lines_text = []

    for line in lines:
        text = ""
        for part in line:
            text = text + part["text"] + " "
        lines_text.append(text)

    return lines_text

def line_to_rect(line):
    left = min(obj["rect"]["left"] for obj in line)
    right = max(obj["rect"]["right"] for obj in line)
    top = min(obj["rect"]["top"] for obj in line)
    bottom = max(obj["rect"]["bottom"] for obj in line)

    return {
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "center_x": (left + right) / 2,
        "center_y": (top + bottom) / 2,
        "height": bottom - top,
        "width": right - left,
        "text": " ".join(obj["text"] for obj in line),
        "parts": line   # keep original OCR objects
    }

def tokenize_alpha(text):
    # keep only letters and spaces
    cleaned = re.sub(r'[^A-Za-z\s]', '', text)
    # collapse multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

LIST_OF_NON_MENU_KEYWORDS = ['.com', 'london'] # expand l8r

def reject_non_menu_items(text):
    if not any(w in text.lower() for w in LIST_OF_NON_MENU_KEYWORDS):
        # only return if the text contains no forbidden key substrings
        return True
    return False

def run_ocr(filename):
    result = reader.readtext(filename)
    rect_data = structure_data(result)
    lines = create_lines(rect_data)

    # transform each line (a list of rects) into a single rect
    # for easier processing
    line_rects = [line_to_rect(line) for line in lines]

    columns = cluster_columns(line_rects)

    #sort columns by y coordinate to ensure they are in order reading top-bottom
    for col in columns:
        col["lines"].sort(key=lambda r: r["top"])
    
    lines = [] # create an array of dicts
    for col in columns:
        for l in col["lines"]:
            lines.append(l)

    items = group_lines_into_items(lines)
    text_items = [item_to_text(item) for item in items]
    non_menu = [t for t in text_items if reject_non_menu_items(t)]

    return non_menu
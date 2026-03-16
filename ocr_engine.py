import easyocr
reader = easyocr.Reader(['en']) # this needs to run only once to load the model into memory

#result = reader.readtext('samplemenu.jpg') #raw ocr read
#print(result)

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
        "center_y": (min(ylist) + max(ylist)) / 2
    }

def same_line(rect_a, rect_b):
    #if center y is different by 1 pixel, same line. 
    if abs(rect_a["center_y"] - rect_b["center_y"]) > 1:
        return False
    
    gap = max(0, min(rect_b["left"], rect_a["left"]) - max(rect_a["right"], rect_b["right"]))
    if gap > 10:
        return False
    
    return True


def structure_data(result):
    structured = []
    for bbox, text, conf in result:
        structured.append({
            "rect": to_rect(bbox),
            "text": text,
            "conf": conf
        })

    return structured    

def create_lines(structured):
    lines = []
    for obj in structured:
        placed = False
        for line in lines:
            if same_line(obj["rect"], line[-1]["rect"]):
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


def run_ocr(filename):
    result = reader.readtext(filename) #raw ocr read
    rect_data = structure_data(result)
    lines = create_lines(rect_data)
    clean = clean_lines(lines)

    return clean


from PIL import Image, ImageEnhance
import pytesseract
import pandas as pd
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Enhancing Image...")
img = Image.open("fnbTestStatement.png").convert('L')
img = img.resize((img.width * 3, img.height * 3), Image.Resampling.LANCZOS)
img = ImageEnhance.Contrast(img).enhance(2.0)

print("Reading Text...")
custom_config = r'--psm 6'
raw_text = pytesseract.image_to_string(img, config=custom_config)

def clean_fnb_amount(raw_str):
    """
    Converts messy OCR text like '§00.00¢' into float 500.00
    """
    if raw_str.startswith('S') or raw_str.startswith('s') or raw_str.startswith('§'):
        raw_str = '5' + raw_str[1:]
    
    is_credit = False
    if any(x in raw_str for x in ['Cr', 'Cr:', 'C:', '6:', '(:', '¢']):
        is_credit = True
    
    clean_nums = re.sub(r"[^0-9.]", "", raw_str)
    
    if not clean_nums or clean_nums.count('.') > 1:
        return None
    
    try:
        val = float(clean_nums)
        return val if is_credit else -val
    except ValueError:
        return None

data = []
lines = raw_text.split('\n')
valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

print("\nProcessing Lines...")

for line in lines:
    parts = line.split()
    if len(parts) < 4: continue

    # Find date
    day = parts[0]
    month = parts[1]
    
    if day.isdigit() and any(m in month for m in valid_months):
        date_str = f"{day} {month} 2023"
        
        amount_found = None
        desc_parts = []
        
        reversed_parts = parts[::-1] 
        
        for i, part in enumerate(reversed_parts):
            if i == 0: continue 
            
            val = clean_fnb_amount(part)
            if val is not None:
                amount_found = val
                split_index = len(parts) - 1 - i
                desc_parts = parts[2:split_index]
                break
        
        if amount_found is not None:
            description = " ".join(desc_parts)
            
            print(f"Found: {date_str} | R {amount_found} | {description}")
            data.append([date_str, description, amount_found])

if data:
    df = pd.DataFrame(data, columns=["Date", "Details", "Amount"])
    df.insert(0, 'Ref', [f"FNB{str(i).zfill(3)}" for i in range(1, len(df) + 1)])
    
    # Ask for opening balance instead
    try:
        op_bal = float(input("\nEnter Opening Balance (from top of page): ") or 0)
    except:
        op_bal = 0.0
        
    df['Running_Balance'] = df['Amount'].cumsum() + op_bal
    
    df.to_excel("Final_FNB_Writeup.xlsx", index=False)
    print("\nSuccess! Open 'Final_FNB_Writeup.xlsx' to see the result.")
else:
    print("No valid transactions found. The image might be too blurry.")
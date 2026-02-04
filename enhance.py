from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Loading and enhancing image...")
original_img = Image.open("fnbTestStatement.png")

# Grayscale img
img = original_img.convert('L')

#Resize to make it clearer
new_size = (original_img.width * 3, original_img.height * 3)
img = img.resize(new_size, Image.Resampling.LANCZOS)

# Increase Contrast to make text pop
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(2.0)

print("Scanning enhanced image...")
raw_text = pytesseract.image_to_string(img, config='--psm 6')

print("\n--- DIAGNOSTIC: ---")
print(raw_text[:500]) 
print("--------------------------------------------\n")

data = []
lines = raw_text.split('\n')
valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

for line in lines:
    parts = line.split()
    
    if len(parts) < 4:
        continue

    day_candidate = parts[0]
    month_candidate = parts[1]

    if day_candidate.isdigit() and any(m in month_candidate for m in valid_months):
        
        # Hardcoded year for testing
        date_str = f"{day_candidate} {month_candidate} 2023"
        
        raw_amount = parts[-2]
        
        if not ('.' in raw_amount or 'Cr' in raw_amount):
            continue

        clean_amt = raw_amount.replace(',', '')
        
        try:
            if "Cr" in clean_amt:
                final_amt = float(clean_amt.replace("Cr", ""))
            else:
                final_amt = -float(clean_amt)
            
            # Extract description
            details = " ".join(parts[2:-2])
            
            print(f"MATCH: {date_str} | {final_amt}")
            data.append([date_str, details, final_amt])
            
        except ValueError:
            continue

if len(data) > 0:
    df = pd.DataFrame(data, columns=["Date", "Details", "Amount"])
    df.insert(0, 'Ref', [f"FNB{str(i).zfill(3)}" for i in range(1, len(df) + 1)])
    df['Running_Balance'] = df['Amount'].cumsum()
    
    print("\n--- SUCCESS! ---")
    print(df)
    df.to_excel("FNB_Enhanced_Result.xlsx", index=False)
else:
    print("\nFAILED: Still couldn't find transactions. Open 'debug_enhanced_view.jpg' to check clarity.")
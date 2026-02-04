from PIL import Image
import pytesseract
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

print("Scanning image...")
raw_text = pytesseract.image_to_string(Image.open("fnbTestStatement.png"), config='--psm 6')

print("\n--- DIAGNOSTIC: WHAT THE COMPUTER SEES ---")
print(raw_text[:500]) 
print("--------------------------------------------\n")

data = []
lines = raw_text.split('\n')

valid_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

print(f"Found {len(lines)} lines of text. Checking each one...\n")

for line in lines:
    parts = line.split()
    if len(parts) < 4:
        continue

    day_candidate = parts[0]
    month_candidate = parts[1]

    if day_candidate.isdigit() and any(m in month_candidate for m in valid_months):
        
        date_str = f"{day_candidate} {month_candidate} 2023" # Hardcoding year for now
        
        raw_amount = parts[-2] 
        
        if not ('.' in raw_amount or 'Cr' in raw_amount):
            print(f"WARNING: Unsure about amount in line: {line}")
            continue

        clean_amt = raw_amount.replace(',', '')
        if "Cr" in clean_amt:
            final_amt = float(clean_amt.replace("Cr", ""))
        else:
            try:
                final_amt = -float(clean_amt)
            except ValueError:
                continue 
        details_list = parts[2:-2]
        details = " ".join(details_list)

        print(f"MATCH: {date_str} | {final_amt} | {details}")
        data.append([date_str, details, final_amt])

if len(data) > 0:
    df = pd.DataFrame(data, columns=["Date", "Details", "Amount"])
    
   
    df.insert(0, 'Ref', [f"FNB{str(i).zfill(3)}" for i in range(1, len(df) + 1)])
    df['Running_Balance'] = df['Amount'].cumsum()
    
    print("\n--- PREVIEW ---")
    print(df)
    df.to_excel("FNB_Fixed.xlsx", index=False)
else:
    print("\nFAILED: No transactions found. Check the 'DIAGNOSTIC' output above to see if the OCR is reading the text correctly.")
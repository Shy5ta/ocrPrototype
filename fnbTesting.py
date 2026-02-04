from PIL import Image
import pytesseract
import pandas as pd
import re

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set the year manually for now (since it's not in the transaction rows)
CURRENT_YEAR = "2025" 

months = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
}

# Reading bank statement
print("Scanning Statement")
img = Image.open("fnbTestStatement.png")

raw_text = pytesseract.image_to_string(img, config='--psm 6')

print("Parsing Data...")

# This pattern is specific to the fnb bank statement format sample I found
# Part A: (\d{2}\s[A-Za-z]{3})
# Part B: \s+(.+)               -> Finds the Description (everything until the numbers start)
# Part C: \s+([\d,\.]+Cr?)      -> Finds the Amount (numbers, commas, dots, optional Cr)
# Part D: \s+([\d,\.]+Cr?)      -> Finds the Balance (we capture it but won't use it)

pattern = r"(\d{2}\s[A-Za-z]{3})\s+(.+?)\s+([\d,]+\.\d{2}(?:Cr)?)"

transactions = []
lines = raw_text.split('\n')

for line in lines:
    # Filtering lines that start with a date number
    match = re.search(pattern, line)
    
    if match:
        raw_date = match.group(1)
        description = match.group(2).strip()
        raw_amount = match.group(3)

        #Convert date format from "DD + abbrev month to YYYY-MM-DD"
        day, month_txt = raw_date.split()
        month_num = months.get(month_txt, "01")
        clean_date = f"{CURRENT_YEAR}-{month_num}-{day}"

        amount_clean = raw_amount.replace(',', '')
        
        if "Cr" in amount_clean:
            # It is a Credit -> Positive
            amount_clean = amount_clean.replace("Cr", "")
            final_amount = float(amount_clean)
        else:
            # It is a Debit -> Negative
            final_amount = -float(amount_clean)

        transactions.append([clean_date, description, final_amount])

df = pd.DataFrame(transactions, columns=["Date", "Details", "Amount"])

# Reference Column (FNB001...)
df.insert(0, 'Ref', [f"FNB{str(i).zfill(3)}" for i in range(1, len(df) + 1)])

# Running Balance
start_balance = 0.0
df['Running_Balance'] = df['Amount'].cumsum() + start_balance

print("\n--- EXTRACTED DATA ---")
print(df)

#Export to Excel
df.to_excel("FNB_Converted.xlsx", index=False)
print("\nSuccess! Saved to FNB_Converted.xlsx")
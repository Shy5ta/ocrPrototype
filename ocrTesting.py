from PIL import Image
import pytesseract

path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
pytesseract.pytesseract.tesseract_cmd = path_to_tesseract

image_path = "Test.png"

try:
    print("Opening image...")
    img = Image.open(image_path)
    
    print("Reading text...")
    text = pytesseract.image_to_string(img)
    
    print("\n--- SUCCESS! ---\n")
    print(text)

except FileNotFoundError:
    print("ERROR: Cannot find 'Test.png'.")
except Exception as e:
    print(f"ERROR: {e}")
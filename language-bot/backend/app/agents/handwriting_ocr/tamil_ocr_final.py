import pytesseract
from PIL import Image
import cv2
import os
import subprocess
from tkinter import Tk, filedialog

# Direct path to Tesseract (no PATH needed)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Check if Tesseract exists
if not os.path.exists(TESSERACT_PATH):
    print("❌ Tesseract not found!")
    print(f"Looking for: {TESSERACT_PATH}")
    
    # Try alternative path
    alt_path = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
    if os.path.exists(alt_path):
        TESSERACT_PATH = alt_path
        print(f"✅ Found at: {alt_path}")
    else:
        print("\n💡 Please install Tesseract from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        exit(1)

# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

print("="*60)
print("🔍 CHECKING TESSERACT INSTALLATION")
print("="*60)

# Check version
try:
    result = subprocess.run([TESSERACT_PATH, '--version'], 
                          capture_output=True, text=True)
    print(f"\n✅ Tesseract found!")
    print(result.stdout.split('\n')[0])
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Check Tamil language
try:
    result = subprocess.run([TESSERACT_PATH, '--list-langs'], 
                          capture_output=True, text=True)
    langs = result.stdout
    print(f"\n📦 Available languages:")
    print(langs)
    
    if 'tam' not in langs:
        print("\n⚠️ WARNING: Tamil language NOT installed!")
        print("\n📥 To install Tamil:")
        print("1. Download: https://github.com/tesseract-ocr/tessdata/raw/main/tam.traineddata")
        print(f"2. Save to: C:\\Program Files\\Tesseract-OCR\\tessdata\\tam.traineddata")
        print("\n❌ Cannot proceed without Tamil language pack!")
        exit(1)
    else:
        print("\n✅ Tamil language pack found!")
except Exception as e:
    print(f"❌ Error checking languages: {e}")
    exit(1)

# ========================================
# FILE PICKER
# ========================================
def select_image_file():
    """Open file picker dialog"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Select Handwritten Tamil Image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    
    return file_path

def extract_tamil_text(image_path):
    """Extract Tamil text ONLY from image"""
    print("\n" + "="*60)
    print("🚀 தமிழ் TEXT EXTRACTION - TAMIL ONLY")
    print("="*60)
    
    # Load image
    print(f"\n📸 Loading image: {os.path.basename(image_path)}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    img = Image.open(image_path)
    print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
    
    # Preprocess
    print("🔄 Preprocessing image...")
    img_cv = cv2.imread(image_path)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(enhanced, h=10)
    
    # Save preprocessed
    temp_path = 'temp_preprocessed.jpg'
    cv2.imwrite(temp_path, denoised)
    img_preprocessed = Image.open(temp_path)
    
    print("\n" + "="*60)
    print("📝 EXTRACTING TAMIL TEXT ONLY...")
    print("="*60)
    
    results = {}
    
    # Tamil only - Preprocessed image
    print("\n1️⃣ Tamil Text (Preprocessed Image):")
    print("-"*60)
    try:
        tamil_preprocessed = pytesseract.image_to_string(img_preprocessed, lang='tam')
        results['tamil_preprocessed'] = tamil_preprocessed
        if tamil_preprocessed.strip():
            print(tamil_preprocessed)
        else:
            print("❌ No Tamil text detected")
    except Exception as e:
        print(f"❌ Error: {e}")
        results['tamil_preprocessed'] = ""
    
    # Tamil only - Original image
    print("\n2️⃣ Tamil Text (Original Image):")
    print("-"*60)
    try:
        tamil_original = pytesseract.image_to_string(img, lang='tam')
        results['tamil_original'] = tamil_original
        if tamil_original.strip():
            print(tamil_original)
        else:
            print("❌ No Tamil text detected")
    except Exception as e:
        print(f"❌ Error: {e}")
        results['tamil_original'] = ""
    
    # Choose best result (longer text usually better)
    best_result = tamil_preprocessed if len(tamil_preprocessed) > len(tamil_original) else tamil_original
    best_source = "preprocessed" if len(tamil_preprocessed) > len(tamil_original) else "original"
    
    print("\n" + "="*60)
    print(f"🏆 BEST RESULT (from {best_source} image):")
    print("="*60)
    print(best_result if best_result.strip() else "❌ No text detected")
    
    # Save results
    print("\n" + "="*60)
    print("💾 SAVING RESULTS...")
    print("="*60)
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Get image name without extension
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    output_file = os.path.join(output_dir, f'tesseract_{image_name}.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("தமிழ் TEXT EXTRACTION - TESSERACT OCR\n")
        f.write("="*60 + "\n\n")
        f.write(f"Source: {os.path.basename(image_path)}\n")
        f.write(f"Image Size: {img.size[0]}x{img.size[1]} pixels\n")
        f.write("-"*60 + "\n\n")
        
        f.write("BEST RESULT:\n")
        f.write("-"*60 + "\n")
        f.write(best_result if best_result else "(No text detected)\n")
        f.write("\n\n")
        
        f.write("PREPROCESSED IMAGE RESULT:\n")
        f.write("-"*60 + "\n")
        f.write(results['tamil_preprocessed'] if results['tamil_preprocessed'] else "(No text detected)\n")
        f.write("\n\n")
        
        f.write("ORIGINAL IMAGE RESULT:\n")
        f.write("-"*60 + "\n")
        f.write(results['tamil_original'] if results['tamil_original'] else "(No text detected)\n")
    
    print(f"✅ Results saved to: {output_file}")
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    print("\n" + "="*60)
    print("✅ EXTRACTION COMPLETE!")
    print("="*60)
    
    return best_result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("📁 SELECT IMAGE")
    print("="*60)
    print("\n🖱️  A file picker window will open...")
    print("   Select your Tamil handwritten image\n")
    
    IMAGE_PATH = select_image_file()
    
    if not IMAGE_PATH:
        print("❌ No image selected!")
        exit(1)
    
    print(f"✅ Selected: {IMAGE_PATH}\n")
    
    if os.path.exists(IMAGE_PATH):
        try:
            tamil_text = extract_tamil_text(IMAGE_PATH)
            
            if tamil_text and tamil_text.strip():
                print("\n" + "="*60)
                print("📊 SUMMARY:")
                print("="*60)
                print(f"✅ Tamil text extracted successfully!")
                print(f"📝 Text length: {len(tamil_text)} characters")
                print(f"📝 Lines: {len(tamil_text.splitlines())} lines")
            else:
                print("\n⚠️ No Tamil text could be extracted from the image")
                print("💡 Tips:")
                print("  - Make sure the image contains Tamil text")
                print("  - Try with clearer/higher resolution image")
                print("  - Check if text is handwritten (harder to recognize)")
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Image file not found: {IMAGE_PATH}")
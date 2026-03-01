import google.generativeai as genai
from PIL import Image
import os
import sys
import warnings
from tkinter import Tk, filedialog
from datetime import datetime

warnings.filterwarnings('ignore')

# ========================================
# API KEY CONFIGURATION
# ========================================
def get_api_key():
    """Get API key from user (safe - not hardcoded)"""
    print("\n🔑 GEMINI API KEY")
    print("="*60)
    print("Get your key: https://aistudio.google.com/apikey")
    print()
    
    api_key = input("Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return None
    
    return api_key

# ========================================
# FILE PICKER
# ========================================
def select_image_file():
    """Open file picker for image selection"""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    print("\n📁 FILE PICKER")
    print("="*60)
    print("🖱️  A file picker window will open...")
    print("   Select your Tamil handwritten image\n")
    
    file_path = filedialog.askopenfilename(
        title="Select Handwritten Tamil Image",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    
    return file_path

# ========================================
# MAIN EXTRACTION
# ========================================
def extract_with_gemini(image_path, api_key):
    """Extract Tamil text using Gemini"""
    
    print("\n" + "="*60)
    print("🚀 GEMINI TAMIL OCR")
    print("="*60)
    
    # Load image
    print(f"\n📸 Loading: {os.path.basename(image_path)}")
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    try:
        img = Image.open(image_path)
        print(f"   Size: {img.size[0]}x{img.size[1]} pixels")
        print("✅ Image loaded")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return None
    
    # Configure Gemini
    print("\n🔧 Initializing Gemini...")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        print("✅ Gemini initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini: {e}")
        return None
    
    # Extract text
    print("\n⏳ Processing with Gemini...")
    
    prompt = """Read this handwritten Tamil text carefully.
Extract ONLY the Tamil text you see.
Return just the text, nothing else."""
    
    try:
        response = model.generate_content([prompt, img])
        tamil_text = response.text.strip()
        
        print("✅ Extraction successful")
        
        return tamil_text
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Extraction failed: {error_msg}")
        
        # Helpful error messages
        if "403" in error_msg or "PERMISSION_DENIED" in error_msg or "SUSPENDED" in error_msg:
            print("\n🔴 API KEY ISSUE!")
            print("="*60)
            print("Your API key is suspended or invalid.")
            print("\n✅ FIX:")
            print("1. Go: https://aistudio.google.com/apikey")
            print("2. Delete current key")
            print("3. Create NEW API key")
            print("4. Run script again with new key")
        
        elif "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            print("\n🔴 QUOTA EXCEEDED!")
            print("="*60)
            print("Free tier limit reached (60 requests/minute).")
            print("\n✅ SOLUTIONS:")
            print("1. Wait 60 seconds")
            print("2. Create new API key for new quota")
            print("3. Upgrade to paid plan")
        
        elif "SAFETY" in error_msg or "blocked" in error_msg.lower():
            print("\n🔴 SAFETY FILTER BLOCKED!")
            print("="*60)
            print("Try with a clearer/higher quality image.")
        
        return None

# ========================================
# SAVE RESULTS
# ========================================
def save_results(tamil_text, image_path):
    """Save extraction results"""
    
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Use image name for output file
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'gemini_{image_name}_{timestamp}.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("GEMINI TAMIL TEXT EXTRACTION\n")
        f.write("="*60 + "\n\n")
        f.write(f"Source: {os.path.basename(image_path)}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-"*60 + "\n\n")
        f.write(tamil_text + "\n\n")
        f.write("-"*60 + "\n")
        f.write(f"Length: {len(tamil_text)} characters\n")
        f.write(f"Lines: {len(tamil_text.splitlines())}\n")
    
    print(f"\n💾 Saved to: {output_file}")
    return output_file

# ========================================
# DISPLAY RESULTS
# ========================================
def display_results(tamil_text):
    """Display extraction results"""
    
    print("\n" + "="*60)
    print("✅ EXTRACTED TAMIL TEXT:")
    print("="*60)
    print(tamil_text if tamil_text else "(No text detected)")
    print("="*60)
    
    if tamil_text:
        print(f"\n📝 Text length: {len(tamil_text)} characters")
        print(f"📝 Lines: {len(tamil_text.splitlines())}")
    
    print("\n" + "="*60)
    print("✅ EXTRACTION COMPLETE!")
    print("="*60)

# ========================================
# MAIN
# ========================================
def main():
    """Main program"""
    
    print("="*60)
    print("🚀 GEMINI TAMIL OCR - FINAL VERSION")
    print("="*60)
    
    # Get API key
    api_key = get_api_key()
    if not api_key:
        return
    
    # Select image
    image_path = select_image_file()
    if not image_path:
        print("\n❌ No image selected!")
        return
    
    print(f"\n✅ Selected: {image_path}")
    
    # Extract text
    tamil_text = extract_with_gemini(image_path, api_key)
    
    if tamil_text:
        # Display results
        display_results(tamil_text)
        
        # Save results
        save_results(tamil_text, image_path)
    else:
        print("\n❌ Failed to extract text from image")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
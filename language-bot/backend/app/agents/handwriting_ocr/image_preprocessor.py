import cv2
import numpy as np
from PIL import Image
import os

class ImagePreprocessor:
    def __init__(self, input_path, output_dir='processed_images'):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def load_image(self):
        """Load image using OpenCV"""
        img = cv2.imread(self.input_path)
        if img is None:
            raise ValueError(f"Cannot load image from {self.input_path}")
        return img
    
    def convert_to_grayscale(self, img):
        """Convert to grayscale"""
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    def increase_contrast(self, img):
        """Increase contrast using CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        return clahe.apply(img)
    
    def denoise(self, img):
        """Remove noise"""
        return cv2.fastNlMeansDenoising(img, h=10)
    
    def binarize(self, img):
        """Apply adaptive thresholding"""
        return cv2.adaptiveThreshold(
            img, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
    
    def sharpen(self, img):
        """Sharpen the image"""
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        return cv2.filter2D(img, -1, kernel)
    
    def deskew(self, img):
        """Deskew image if tilted"""
        coords = np.column_stack(np.where(img > 0))
        if len(coords) == 0:
            return img
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h), 
                                 flags=cv2.INTER_CUBIC, 
                                 borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def preprocess_basic(self):
        """Basic preprocessing pipeline"""
        print("📸 Loading image...")
        img = self.load_image()
        
        print("🔄 Converting to grayscale...")
        gray = self.convert_to_grayscale(img)
        
        print("✨ Increasing contrast...")
        contrast = self.increase_contrast(gray)
        
        print("🧹 Denoising...")
        denoised = self.denoise(contrast)
        
        # Save result
        output_path = os.path.join(self.output_dir, 'basic_preprocessed.jpg')
        cv2.imwrite(output_path, denoised)
        print(f"✅ Basic preprocessing done: {output_path}")
        
        return output_path
    
    def preprocess_advanced(self):
        """Advanced preprocessing pipeline"""
        print("📸 Loading image...")
        img = self.load_image()
        
        print("🔄 Converting to grayscale...")
        gray = self.convert_to_grayscale(img)
        
        print("✨ Increasing contrast...")
        contrast = self.increase_contrast(gray)
        
        print("🧹 Denoising...")
        denoised = self.denoise(contrast)
        
        print("📐 Deskewing...")
        deskewed = self.deskew(denoised)
        
        print("🔪 Sharpening...")
        sharpened = self.sharpen(deskewed)
        
        print("⚫ Binarizing...")
        binary = self.binarize(sharpened)
        
        # Save result
        output_path = os.path.join(self.output_dir, 'advanced_preprocessed.jpg')
        cv2.imwrite(output_path, binary)
        print(f"✅ Advanced preprocessing done: {output_path}")
        
        return output_path
    
    def preprocess_all(self):
        """Create multiple preprocessed versions"""
        results = {}
        
        # Original
        img = self.load_image()
        original_path = os.path.join(self.output_dir, 'original.jpg')
        cv2.imwrite(original_path, img)
        results['original'] = original_path
        
        # Basic
        results['basic'] = self.preprocess_basic()
        
        # Advanced
        results['advanced'] = self.preprocess_advanced()
        
        return results
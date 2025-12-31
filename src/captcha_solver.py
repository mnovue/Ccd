#!/usr/bin/env python3
"""
CAPTCHA Solver untuk text dan math CAPTCHA
"""

import re
import base64
import time
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from io import BytesIO

# Try to import optional dependencies
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CaptchaResult:
    """Hasil pemecahan CAPTCHA"""
    success: bool
    captcha_type: str
    solution: Optional[Any] = None
    confidence: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class CaptchaSolver:
    """Solver untuk text-based CAPTCHA"""
    
    def __init__(self):
        self.tesseract_configs = {
            'default': '--oem 3 --psm 6',
            'single_char': '--oem 3 --psm 10',
            'single_line': '--oem 3 --psm 7',
            'numbers_only': '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789',
            'letters_only': '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        }
    
    def load_image_from_base64(self, base64_string: str):
        """Load image dari base64 string"""
        try:
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Error loading image from base64: {e}")
            return None
    
    def preprocess_image(self, image):
        """Preprocess image untuk OCR"""
        try:
            # Convert ke grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Apply threshold
            image = image.point(lambda x: 0 if x < 128 else 255, '1')
            
            return image
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return image
    
    def solve_text_captcha(self, image_source: str) -> CaptchaResult:
        """Solve text-based CAPTCHA"""
        start_time = time.time()
        
        try:
            if not OCR_AVAILABLE:
                return CaptchaResult(
                    success=False,
                    captcha_type='text',
                    error="OCR dependencies not installed",
                    processing_time=time.time() - start_time
                )
            
            # Load image
            image = self.load_image_from_base64(image_source)
            if not image:
                return CaptchaResult(
                    success=False,
                    captcha_type='text',
                    error="Failed to load image",
                    processing_time=time.time() - start_time
                )
            
            # Preprocess
            processed = self.preprocess_image(image)
            
            # OCR
            text = pytesseract.image_to_string(
                processed,
                config=self.tesseract_configs['default']
            ).strip()
            
            if text:
                # Post-process
                text = self.post_process_text(text)
                
                return CaptchaResult(
                    success=True,
                    captcha_type='text',
                    solution=text,
                    confidence=min(len(text) / 10, 1.0),
                    processing_time=time.time() - start_time
                )
            
            return CaptchaResult(
                success=False,
                captcha_type='text',
                error="No text found",
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error solving text captcha: {e}")
            return CaptchaResult(
                success=False,
                captcha_type='text',
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def solve_math_captcha(self, image_source: str) -> CaptchaResult:
        """Solve math CAPTCHA"""
        start_time = time.time()
        
        try:
            # Solve text first
            text_result = self.solve_text_captcha(image_source)
            
            if not text_result.success:
                return CaptchaResult(
                    success=False,
                    captcha_type='math',
                    error="Failed to extract text",
                    processing_time=time.time() - start_time
                )
            
            text = text_result.solution
            
            # Try to parse math expression
            math_patterns = [
                r'(\d+)\s*[+\-*/]\s*(\d+)',
                r'(\d+)\s*\+\s*(\d+)',
                r'(\d+)\s*\-\s*(\d+)',
                r'(\d+)\s*\*\s*(\d+)',
                r'(\d+)\s*/\s*(\d+)',
            ]
            
            for pattern in math_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        a = int(match.group(1))
                        b = int(match.group(2))
                        
                        if '+' in text:
                            result = a + b
                        elif '-' in text:
                            result = a - b
                        elif '*' in text:
                            result = a * b
                        elif '/' in text:
                            result = a / b if b != 0 else 0
                        else:
                            result = a + b
                        
                        return CaptchaResult(
                            success=True,
                            captcha_type='math',
                            solution=str(int(result) if isinstance(result, float) and result.is_integer() else result),
                            confidence=text_result.confidence * 0.9,
                            processing_time=time.time() - start_time,
                            metadata={'expression': f"{a} + {b}"}
                        )
                    except:
                        continue
            
            return CaptchaResult(
                success=False,
                captcha_type='math',
                error="Could not parse math expression",
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error solving math captcha: {e}")
            return CaptchaResult(
                success=False,
                captcha_type='math',
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def post_process_text(self, text: str) -> str:
        """Post-process OCR result"""
        # Remove common OCR errors
        replacements = {
            '0': 'O',
            '1': 'I',
            '5': 'S',
            '8': 'B',
            ' ': '',
        }
        
        # Remove non-alphanumeric
        text = re.sub(r'[^a-zA-Z0-9]', '', text)
        
        # Apply replacements
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text.upper()

if __name__ == "__main__":
    # Test if run directly
    solver = CaptchaSolver()
    
    if OCR_AVAILABLE:
        print("CAPTCHA Solver initialized successfully")
    else:
        print("Warning: OCR dependencies not installed")
        print("Install with: pip install pytesseract pillow")

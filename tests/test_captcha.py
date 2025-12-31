#!/usr/bin/env python3
"""
Unit tests untuk CaptchaSolver
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import base64
from io import BytesIO
from PIL import Image, ImageDraw

# Mock untuk optional dependencies
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    # Create mock
    class pytesseract:
        @staticmethod
        def image_to_string(image, config=None):
            return "TEST123"

from src.captcha_solver import CaptchaSolver, CaptchaResult

class TestCaptchaSolver(unittest.TestCase):
    
    def setUp(self):
        """Setup sebelum setiap test"""
        self.solver = CaptchaSolver()
        
        # Buat test image
        self.create_test_image()
    
    def create_test_image(self):
        """Buat test image dengan teks"""
        # Create image
        img = Image.new('RGB', (200, 80), color='white')
        d = ImageDraw.Draw(img)
        
        # Try to use font
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = None
        
        d.text((20, 20), "TEST123", fill='black', font=font)
        
        # Save ke bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        self.test_image_bytes = img_bytes.getvalue()
        
        # Convert ke base64
        self.test_image_base64 = base64.b64encode(self.test_image_bytes).decode('utf-8')
        self.test_image_data_url = f"data:image/png;base64,{self.test_image_base64}"
    
    def test_load_image_from_base64_valid(self):
        """Test load image dari base64 valid"""
        image = self.solver.load_image_from_base64(self.test_image_data_url)
        
        self.assertIsNotNone(image)
        self.assertEqual(image.size, (200, 80))
    
    def test_load_image_from_base64_invalid(self):
        """Test load image dari base64 invalid"""
        image = self.solver.load_image_from_base64("invalid_base64")
        
        self.assertIsNone(image)
    
    def test_load_image_from_base64_no_prefix(self):
        """Test load image dari base64 tanpa data URL prefix"""
        image = self.solver.load_image_from_base64(self.test_image_base64)
        
        self.assertIsNotNone(image)
    
    @unittest.skipIf(not OCR_AVAILABLE, "OCR dependencies not installed")
    def test_preprocess_image(self):
        """Test preprocessing image"""
        image = self.solver.load_image_from_base64(self.test_image_data_url)
        processed = self.solver.preprocess_image(image)
        
        self.assertIsNotNone(processed)
        self.assertEqual(processed.mode, '1')  # Binary mode setelah threshold
    
    @patch('src.captcha_solver.pytesseract.image_to_string')
    def test_solve_text_captcha_success(self, mock_tesseract):
        """Test solve text CAPTCHA berhasil"""
        # Mock Tesseract
        mock_tesseract.return_value = "TEST123"
        
        result = self.solver.solve_text_captcha(self.test_image_data_url)
        
        self.assertTrue(result.success)
        self.assertEqual(result.solution, "TEST123")
        self.assertEqual(result.captcha_type, 'text')
        self.assertGreater(result.confidence, 0)
        self.assertGreater(result.processing_time, 0)
    
    def test_solve_text_captcha_ocr_not_available(self):
        """Test solve text CAPTCHA ketika OCR tidak tersedia"""
        # Simulate OCR not available
        with patch('src.captcha_solver.OCR_AVAILABLE', False):
            result = self.solver.solve_text_captcha(self.test_image_data_url)
            
            self.assertFalse(result.success)
            self.assertIn("OCR dependencies", result.error)
    
    def test_solve_text_captcha_load_image_fails(self):
        """Test solve text CAPTCHA ketika load image gagal"""
        result = self.solver.solve_text_captcha("invalid_data")
        
        self.assertFalse(result.success)
        self.assertIn("Failed to load", result.error)
    
    @patch('src.captcha_solver.pytesseract.image_to_string')
    def test_solve_text_captcha_no_text_found(self, mock_tesseract):
        """Test solve text CAPTCHA ketika tidak ada teks ditemukan"""
        mock_tesseract.return_value = ""
        
        result = self.solver.solve_text_captcha(self.test_image_data_url)
        
        self.assertFalse(result.success)
        self.assertIn("No text found", result.error)
    
    @patch('src.captcha_solver.CaptchaSolver.solve_text_captcha')
    def test_solve_math_captcha_success(self, mock_solve_text):
        """Test solve math CAPTCHA berhasil"""
        # Mock text solving
        mock_solve_text.return_value = CaptchaResult(
            success=True,
            captcha_type='text',
            solution="2 + 3",
            confidence=0.8,
            processing_time=0.5
        )
        
        result = self.solver.solve_math_captcha(self.test_image_data_url)
        
        self.assertTrue(result.success)
        self.assertEqual(result.solution, "5")
        self.assertEqual(result.captcha_type, 'math')
    
    @patch('src.captcha_solver.CaptchaSolver.solve_text_captcha')
    def test_solve_math_captcha_text_fails(self, mock_solve_text):
        """Test solve math CAPTCHA ketika text solving gagal"""
        mock_solve_text.return_value = CaptchaResult(
            success=False,
            captcha_type='text',
            error="OCR failed"
        )
        
        result = self.solver.solve_math_captcha(self.test_image_data_url)
        
        self.assertFalse(result.success)
        self.assertIn("Failed to extract", result.error)
    
    @patch('src.captcha_solver.CaptchaSolver.solve_text_captcha')
    def test_solve_math_captcha_no_math_found(self, mock_solve_text):
        """Test solve math CAPTCHA ketika tidak ada ekspresi matematika"""
        mock_solve_text.return_value = CaptchaResult(
            success=True,
            captcha_type='text',
            solution="Hello World",  # Bukan matematika
            confidence=0.8
        )
        
        result = self.solver.solve_math_captcha(self.test_image_data_url)
        
        self.assertFalse(result.success)
        self.assertIn("Could not parse", result.error)
    
    def test_post_process_text(self):
        """Test post-processing text"""
        test_cases = [
            ("AB0D123", "AB0D123"),
            ("A B C D", "ABCD"),
            ("ab1d123", "AB1D123"),
            ("o12345", "O12345"),
            ("test@123#", "TEST123"),
        ]
        
        for input_text, expected in test_cases:
            result = self.solver.post_process_text(input_text)
            self.assertEqual(result, expected, f"Input: {input_text}")

if __name__ == '__main__':
    unittest.main()

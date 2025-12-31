"""
Test suite for AB Links Solver package.

This module contains unit tests, integration tests, and performance tests
for the AB Links Solver package.

Test Structure:
    test_ab_links.py: Tests for EnhancedABLinksSolver
    test_captcha.py: Tests for CaptchaSolver
    test_rektcaptcha.py: Tests for RektCaptchaSolver
"""

import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

__version__ = "1.0.0"
__test__ = True  # Mark this as a test package

# Test configuration
TEST_TIMEOUT = 300  # 5 minutes default timeout
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Ensure test data directory exists
if not os.path.exists(TEST_DATA_DIR):
    os.makedirs(TEST_DATA_DIR)

# Test utilities
def create_test_captcha_image(text="TEST123", size=(200, 80)):
    """
    Create a test CAPTCHA image for testing.
    
    Args:
        text: Text to render in image
        size: Image size (width, height)
    
    Returns:
        PIL Image object
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        # Create image
        img = Image.new('RGB', size, color='white')
        d = ImageDraw.Draw(img)
        
        # Try to use a font
        try:
            # Try common font paths
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "arial.ttf",
                "Arial.ttf",
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 36)
                    break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Add some noise
        for _ in range(100):
            x = random.randint(0, size[0]-1)
            y = random.randint(0, size[1]-1)
            d.point((x, y), fill=(random.randint(200, 255), 
                                  random.randint(200, 255), 
                                  random.randint(200, 255)))
        
        # Draw text
        text_position = (20, 20)
        d.text(text_position, text, fill='black', font=font)
        
        # Add some lines
        for _ in range(5):
            x1 = random.randint(0, size[0]-1)
            y1 = random.randint(0, size[1]-1)
            x2 = random.randint(0, size[0]-1)
            y2 = random.randint(0, size[1]-1)
            d.line([(x1, y1), (x2, y2)], 
                   fill=(random.randint(100, 200), 
                         random.randint(100, 200), 
                         random.randint(100, 200)), 
                   width=1)
        
        return img
        
    except ImportError:
        # Return None if PIL is not available
        return None

def get_test_url(service='adfly'):
    """
    Get a test URL for a specific service.
    
    Args:
        service: Service name ('adfly', 'linkvertise', etc.)
    
    Returns:
        Test URL string
    """
    test_urls = {
        'adfly': 'https://adf.ly/1234567/https://example.com',
        'linkvertise': 'https://linkvertise.com/1234567/example',
        'gyanilinks': 'https://gyanilinks.com/1234567/example',
        'shortconnect': 'https://shortconnect.com/abc123',
        'ouo': 'https://ouo.io/abc123',
    }
    
    return test_urls.get(service, 'https://example.com')

# Test data for CAPTCHA solver
TEST_CAPTCHA_IMAGES = {
    'text': [
        {"text": "ABCD123", "description": "Simple alphanumeric"},
        {"text": "123456", "description": "Numbers only"},
        {"text": "CAPTCHA", "description": "Letters only"},
    ],
    'math': [
        {"expression": "2 + 3", "answer": "5"},
        {"expression": "10 - 4", "answer": "6"},
        {"expression": "3 * 3", "answer": "9"},
    ]
}

# Import test classes for easy access
try:
    from .test_ab_links import TestEnhancedABLinksSolver
    from .test_captcha import TestCaptchaSolver
    from .test_rektcaptcha import TestRektCaptchaSolver
except ImportError:
    # Define placeholder test classes if imports fail
    class TestEnhancedABLinksSolver:
        """Placeholder test class"""
        pass
    
    class TestCaptchaSolver:
        """Placeholder test class"""
        pass
    
    class TestRektCaptchaSolver:
        """Placeholder test class"""
        pass

# Test runner helper function
def run_all_tests(verbosity=1):
    """
    Run all tests in the test suite.
    
    Args:
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose)
    
    Returns:
        Boolean indicating if all tests passed
    """
    import unittest
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(__file__), pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()

# Module initialization
if __name__ == "__main__":
    print(f"AB Links Solver Test Suite v{__version__}")
    print("=" * 50)
    
    # Run tests if module is executed directly
    success = run_all_tests(verbosity=2)
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

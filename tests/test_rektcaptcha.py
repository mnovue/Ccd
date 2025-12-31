#!/usr/bin/env python3
"""
Unit tests untuk RektCaptchaSolver
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import re
from src.rektcaptcha_solver import RektCaptchaSolver, ReCaptchaResult

class TestRektCaptchaSolver(unittest.TestCase):
    
    def setUp(self):
        """Setup sebelum setiap test"""
        self.solver = RektCaptchaSolver()
        
        # Contoh HTML untuk testing
        self.html_v2 = '''
        <html>
            <div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"></div>
        </html>
        '''
        
        self.html_v2_invisible = '''
        <html>
            <div class="g-recaptcha" data-sitekey="6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-"
                 data-size="invisible"></div>
        </html>
        '''
        
        self.html_v3 = '''
        <html>
            <script src="https://www.google.com/recaptcha/api.js?render=6LcR_ckUAAAAAJQZ8JQZ8JQZ8JQZ8JQZ8JQZ8JQZ"></script>
            <script>
                grecaptcha.execute('6LcR_ckUAAAAAJQZ8JQZ8JQZ8JQZ8JQZ8JQZ8JQZ', {action: 'submit'});
            </script>
        </html>
        '''
        
        self.page_url = "https://example.com/test"
    
    def test_extract_recaptcha_params_v2(self):
        """Test ekstraksi parameter reCAPTCHA v2"""
        params = self.solver.extract_recaptcha_params(self.html_v2, self.page_url)
        
        self.assertEqual(params['sitekey'], "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-")
        self.assertEqual(params['type'], 'v2')
        self.assertEqual(params['theme'], 'light')
        self.assertEqual(params['size'], 'normal')
        self.assertEqual(params['page_url'], self.page_url)
        self.assertFalse(params['enterprise'])
    
    def test_extract_recaptcha_params_v2_invisible(self):
        """Test ekstraksi parameter reCAPTCHA v2 invisible"""
        params = self.solver.extract_recaptcha_params(self.html_v2_invisible, self.page_url)
        
        self.assertEqual(params['type'], 'v2-invisible')
        self.assertEqual(params['size'], 'invisible')
    
    def test_extract_recaptcha_params_no_sitekey(self):
        """Test ekstraksi parameter ketika tidak ada sitekey"""
        html_no_recaptcha = "<html><body>No reCAPTCHA here</body></html>"
        
        params = self.solver.extract_recaptcha_params(html_no_recaptcha, self.page_url)
        
        self.assertIsNone(params['sitekey'])
    
    def test_extract_recaptcha_params_multiple_patterns(self):
        """Test ekstraksi parameter dengan multiple patterns"""
        html_multiple = '''
        <html>
            <div class="g-recaptcha" data-sitekey="SITEKEY1"></div>
            <script>sitekey: "SITEKEY2"</script>
        </html>
        '''
        
        params = self.solver.extract_recaptcha_params(html_multiple, self.page_url)
        
        # Should find first sitekey
        self.assertEqual(params['sitekey'], "SITEKEY1")
    
    def test_solve_recaptcha_v2_success(self):
        """Test solve reCAPTCHA v2 berhasil"""
        sitekey = "test_sitekey_123"
        
        result = self.solver.solve_recaptcha_v2(sitekey, self.page_url)
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.solution)
        self.assertIn("mock_token", result.solution)
        self.assertEqual(result.method, 'mock')
        self.assertGreater(result.execution_time, 0)
        self.assertIsNotNone(result.metadata)
        self.assertEqual(result.metadata['sitekey'], sitekey)
    
    def test_solve_recaptcha_v2_exception(self):
        """Test solve reCAPTCHA v2 dengan exception"""
        # Buat solver yang akan raise exception
        with patch.object(self.solver, 'solve_recaptcha_v2') as mock_solve:
            mock_solve.side_effect = Exception("Test exception")
            
            # Create new instance to avoid infinite recursion
            solver2 = RektCaptchaSolver()
            with patch.object(solver2, 'solve_recaptcha_v2') as mock_solve2:
                mock_solve2.side_effect = Exception("Test exception")
                
                result = solver2.solve_recaptcha_v2("test", self.page_url)
                
                self.assertFalse(result.success)
                self.assertIn("Test exception", result.error)
    
    def test_solve_from_page_success(self):
        """Test solve dari halaman berhasil"""
        # Mock extract params dan solve
        with patch.object(self.solver, 'extract_recaptcha_params') as mock_extract, \
             patch.object(self.solver, 'solve_recaptcha_v2') as mock_solve:
            
            mock_extract.return_value = {
                'sitekey': 'test_sitekey',
                'type': 'v2'
            }
            
            mock_solve.return_value = ReCaptchaResult(
                success=True,
                solution='mock_token_123',
                method='mock'
            )
            
            result = self.solver.solve_from_page(self.page_url)
            
            self.assertTrue(result.success)
            self.assertEqual(result.solution, 'mock_token_123')
            mock_extract.assert_called_once()
            mock_solve.assert_called_once()
    
    def test_solve_from_page_no_recaptcha(self):
        """Test solve dari halaman tanpa reCAPTCHA"""
        with patch.object(self.solver, 'extract_recaptcha_params') as mock_extract:
            mock_extract.return_value = {'sitekey': None}
            
            result = self.solver.solve_from_page(self.page_url)
            
            self.assertFalse(result.success)
            self.assertIn("No reCAPTCHA found", result.error)
    
    def test_solve_from_page_exception(self):
        """Test solve dari halaman dengan exception"""
        with patch.object(self.solver, 'extract_recaptcha_params') as mock_extract:
            mock_extract.side_effect = Exception("HTML parsing error")
            
            result = self.solver.solve_from_page(self.page_url)
            
            self.assertFalse(result.success)
            self.assertIn("HTML parsing error", result.error)
    
    def test_recaptcha_token_format(self):
        """Test format token reCAPTCHA"""
        result = self.solver.solve_recaptcha_v2("test_sitekey", self.page_url)
        
        # Token harus string
        self.assertIsInstance(result.solution, str)
        
        # Token harus mengandung mock_token
        if result.success:
            self.assertIn("mock_token", result.solution)
        
        # Execution time harus positif
        self.assertGreater(result.execution_time, 0)
    
    def test_metadata_structure(self):
        """Test struktur metadata hasil"""
        result = self.solver.solve_recaptcha_v2("test_sitekey", self.page_url)
        
        if result.success and result.metadata:
            # Metadata harus dictionary
            self.assertIsInstance(result.metadata, dict)
            
            # Harus ada sitekey di metadata
            self.assertIn('sitekey', result.metadata)
            self.assertEqual(result.metadata['sitekey'], "test_sitekey")

if __name__ == '__main__':
    unittest.main()

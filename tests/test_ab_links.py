#!/usr/bin/env python3
"""
Unit tests untuk EnhancedABLinksSolver
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.ab_links_solver import EnhancedABLinksSolver, SolveResult

class TestEnhancedABLinksSolver(unittest.TestCase):
    
    def setUp(self):
        """Setup sebelum setiap test"""
        self.solver = EnhancedABLinksSolver()
        
        # Test URLs
        self.test_urls = {
            'adfly': 'https://adf.ly/1234567/https://example.com',
            'linkvertise': 'https://linkvertise.com/1234567/example',
            'gyanilinks': 'https://gyanilinks.com/1234567/example',
            'shortconnect': 'https://shortconnect.com/abc123',
            'unknown': 'https://example.com/unknown',
        }
    
    def test_detect_service(self):
        """Test deteksi service dari URL"""
        test_cases = [
            (self.test_urls['adfly'], 'adfly'),
            (self.test_urls['linkvertise'], 'linkvertise'),
            (self.test_urls['gyanilinks'], 'gyanilinks'),
            (self.test_urls['shortconnect'], 'shortconnect'),
            (self.test_urls['unknown'], 'unknown'),
        ]
        
        for url, expected in test_cases:
            result = self.solver.detect_service(url)
            self.assertEqual(result, expected, f"URL: {url}")
    
    def test_detect_service_adfly_variants(self):
        """Test deteksi AdFly variants"""
        adfly_variants = [
            'https://adf.ly/1234567/link',
            'https://adfoc.us/1234567/link',
            'https://j.gs/1234567/link',
            'https://q.gs/1234567/link',
        ]
        
        for url in adfly_variants:
            service = self.solver.detect_service(url)
            self.assertEqual(service, 'adfly', f"Failed for: {url}")
    
    def test_detect_service_linkvertise_variants(self):
        """Test deteksi Linkvertise variants"""
        variants = [
            'https://linkvertise.com/1234567/link',
            'https://link-to.net/1234567/link',
            'https://link-center.net/1234567/link',
            'https://link-hub.net/1234567/link',
        ]
        
        for url in variants:
            service = self.solver.detect_service(url)
            self.assertEqual(service, 'linkvertise', f"Failed for: {url}")
    
    @patch('src.ab_links_solver.EnhancedABLinksSolver.safe_request')
    def test_extract_adfly_link_success(self, mock_safe_request):
        """Test ekstraksi AdFly link berhasil"""
        # Mock response
        mock_response = Mock()
        mock_response.text = '''
            <script>var ysmm = 'MTIzdGVzdGluZzEyMw==';</script>
        '''
        mock_safe_request.return_value = mock_response
        
        result = self.solver.extract_adfly_link(self.test_urls['adfly'])
        
        # Karena decoding sederhana, hasil bisa None atau string
        self.assertIsNotNone(result)
    
    @patch('src.ab_links_solver.EnhancedABLinksSolver.safe_request')
    def test_extract_adfly_link_no_ysmm(self, mock_safe_request):
        """Test ekstraksi AdFly link tanpa ysmm variable"""
        mock_response = Mock()
        mock_response.text = '<html>No ysmm here</html>'
        mock_safe_request.return_value = mock_response
        
        result = self.solver.extract_adfly_link(self.test_urls['adfly'])
        
        self.assertIsNone(result)
    
    @patch('src.ab_links_solver.EnhancedABLinksSolver.safe_request')
    def test_extract_adfly_link_request_fails(self, mock_safe_request):
        """Test ekstraksi AdFly link ketika request gagal"""
        mock_safe_request.return_value = None
        
        result = self.solver.extract_adfly_link(self.test_urls['adfly'])
        
        self.assertIsNone(result)
    
    def test_solve_single_success(self):
        """Test solve single URL berhasil"""
        # Mock extract method
        with patch.object(self.solver, 'extract_adfly_link') as mock_extract:
            mock_extract.return_value = 'https://solved-link.com'
            
            result = self.solver.solve_single(self.test_urls['adfly'])
            
            self.assertTrue(result.success)
            self.assertEqual(result.solved_url, 'https://solved-link.com')
            self.assertEqual(result.service, 'adfly')
            self.assertGreater(result.response_time, 0)
    
    def test_solve_single_failure(self):
        """Test solve single URL gagal"""
        with patch.object(self.solver, 'extract_adfly_link') as mock_extract:
            mock_extract.return_value = None
            
            result = self.solver.solve_single(self.test_urls['adfly'])
            
            self.assertFalse(result.success)
            self.assertIsNone(result.solved_url)
    
    def test_solve_single_exception(self):
        """Test solve single URL dengan exception"""
        with patch.object(self.solver, 'extract_adfly_link') as mock_extract:
            mock_extract.side_effect = Exception("Test exception")
            
            result = self.solver.solve_single(self.test_urls['adfly'])
            
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)
            self.assertIn("Test exception", result.error)
    
    def test_solve_batch(self):
        """Test solve batch URLs"""
        urls = [
            self.test_urls['adfly'],
            self.test_urls['linkvertise'],
            self.test_urls['unknown'],
        ]
        
        # Mock extract methods
        with patch.object(self.solver, 'extract_adfly_link') as mock_adfly, \
             patch.object(self.solver, 'extract_linkvertise_link') as mock_linkvertise:
            
            mock_adfly.return_value = 'https://solved-adfly.com'
            mock_linkvertise.return_value = 'https://solved-linkvertise.com'
            
            results = self.solver.solve_batch(urls, max_workers=1)
            
            self.assertEqual(len(results), 3)
            self.assertTrue(results[0].success)
            self.assertTrue(results[1].success)
            self.assertFalse(results[2].success)
            
            # Urutan harus tetap sama
            self.assertEqual(results[0].original_url, urls[0])
            self.assertEqual(results[1].original_url, urls[1])
            self.assertEqual(results[2].original_url, urls[2])
    
    def test_export_results_json(self):
        """Test export results ke JSON"""
        results = [
            SolveResult(
                original_url='https://adf.ly/123',
                service='adfly',
                solved_url='https://real.com',
                success=True,
                response_time=1.5
            ),
            SolveResult(
                original_url='https://linkvertise.com/123',
                service='linkvertise',
                solved_url=None,
                success=False,
                response_time=2.0,
                error='Failed'
            )
        ]
        
        json_output = self.solver.export_results(results, 'json')
        
        # Parse untuk verify
        import json as json_module
        data = json_module.loads(json_output)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['original_url'], 'https://adf.ly/123')
        self.assertEqual(data[1]['error'], 'Failed')
    
    def test_export_results_csv(self):
        """Test export results ke CSV"""
        results = [
            SolveResult(
                original_url='https://test.com',
                service='test',
                solved_url='https://solved.com',
                success=True,
                response_time=1.0
            )
        ]
        
        csv_output = self.solver.export_results(results, 'csv')
        
        self.assertIn('original_url', csv_output)
        self.assertIn('https://test.com', csv_output)
        self.assertIn('https://solved.com', csv_output)
    
    def test_export_results_text(self):
        """Test export results ke text"""
        results = [
            SolveResult(
                original_url='https://test.com',
                service='test',
                solved_url='https://solved.com',
                success=True,
                response_time=1.0
            )
        ]
        
        text_output = self.solver.export_results(results, 'text')
        
        self.assertIn('https://test.com', text_output)
        self.assertIn('✓', text_output)  # Success indicator

if __name__ == '__main__':
    unittest.main()

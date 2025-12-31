#!/usr/bin/env python3
"""
Enhanced AB Links Solver
Support: AdFly, Linkvertise, GyaniLinks, ShortConnect, etc.
"""

import re
import time
import random
import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

@dataclass
class SolveResult:
    """Data class untuk hasil solve"""
    original_url: str
    service: str
    solved_url: Optional[str]
    success: bool
    error: Optional[str] = None
    response_time: Optional[float] = None
    metadata: Optional[Dict] = None

class EnhancedABLinksSolver:
    """Main solver class"""
    
    def __init__(self, use_proxy: bool = False, max_retries: int = 3):
        self.session = requests.Session()
        self.max_retries = max_retries
        self.use_proxy = use_proxy
        
        # Service patterns
        self.service_patterns = {
            'adfly': [
                r'https?://(?:www\.)?adf\.ly/\d+/(.+)',
                r'https?://(?:www\.)?adfoc\.us/\d+/(.+)',
            ],
            'linkvertise': [
                r'https?://(?:www\.)?linkvertise\.com/(?:\d+/)?(.+)',
                r'https?://(?:www\.)?link-to\.net/\d+/(.+)',
            ],
            'gyanilinks': [
                r'https?://(?:www\.)?gyanilinks\.com/\d+/(.+)',
            ],
            'shortconnect': [
                r'https?://(?:www\.)?shortconnect\.com/[A-Za-z0-9]+',
            ],
        }
        
        # User agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
    
    def detect_service(self, url: str) -> str:
        """Deteksi layanan dari URL"""
        for service, patterns in self.service_patterns.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return service
        return 'unknown'
    
    def safe_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Lakukan request dengan retry"""
        for attempt in range(self.max_retries):
            try:
                headers = kwargs.get('headers', {})
                headers['User-Agent'] = random.choice(self.user_agents)
                kwargs['headers'] = headers
                
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = 30
                
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                else:
                    response = self.session.request(method, url, **kwargs)
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    return None
                time.sleep(2 ** attempt)
        
        return None
    
    def extract_adfly_link(self, url: str) -> Optional[str]:
        """Ekstrak link dari AdFly"""
        try:
            response = self.safe_request(url, allow_redirects=False)
            if not response:
                return None
            
            html = response.text
            
            # Cari ysmm variable
            patterns = [
                r'var\s+ysmm\s*=\s*["\']([^"\']+)["\']',
                r'ysmm\s*=\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    ysmm = match.group(1)
                    # Simple decode (simplified)
                    decoded = ''
                    for i in range(len(ysmm)):
                        if i % 2 == 0:
                            decoded += ysmm[i]
                        else:
                            decoded = ysmm[i] + decoded
                    
                    # Cari URL dalam decoded string
                    url_match = re.search(r'(https?://[^\s<>"\']+)', decoded)
                    if url_match:
                        return url_match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting AdFly link: {e}")
            return None
    
    def extract_linkvertise_link(self, url: str) -> Optional[str]:
        """Ekstrak link dari Linkvertise"""
        try:
            # Simple implementation
            response = self.safe_request(url, allow_redirects=True)
            if response and response.url != url:
                return response.url
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Linkvertise link: {e}")
            return None
    
    def solve_single(self, url: str) -> SolveResult:
        """Solve single URL"""
        start_time = time.time()
        service = self.detect_service(url)
        
        result = SolveResult(
            original_url=url,
            service=service,
            solved_url=None,
            success=False
        )
        
        try:
            if service == 'adfly':
                solved_url = self.extract_adfly_link(url)
            elif service == 'linkvertise':
                solved_url = self.extract_linkvertise_link(url)
            elif service == 'gyanilinks':
                # Similar to AdFly
                solved_url = self.extract_adfly_link(url)
            elif service == 'shortconnect':
                response = self.safe_request(url, allow_redirects=True)
                solved_url = response.url if response else None
            else:
                solved_url = None
            
            result.solved_url = solved_url
            result.success = solved_url is not None
            
        except Exception as e:
            result.error = str(e)
        
        result.response_time = time.time() - start_time
        return result
    
    def solve_batch(self, urls: List[str], max_workers: int = 5) -> List[SolveResult]:
        """Solve multiple URLs concurrently"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.solve_single, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append(SolveResult(
                        original_url=url,
                        service='unknown',
                        solved_url=None,
                        success=False,
                        error=str(e)
                    ))
        
        # Sort by original order
        url_order = {url: i for i, url in enumerate(urls)}
        results.sort(key=lambda x: url_order.get(x.original_url, 0))
        
        return results
    
    def export_results(self, results: List[SolveResult], format: str = 'text') -> str:
        """Export results dalam berbagai format"""
        if format == 'json':
            data = []
            for result in results:
                data.append({
                    'original_url': result.original_url,
                    'service': result.service,
                    'solved_url': result.solved_url,
                    'success': result.success,
                    'response_time': result.response_time,
                    'error': result.error
                })
            return json.dumps(data, indent=2)
        
        elif format == 'csv':
            lines = ['original_url,service,solved_url,success,response_time,error']
            for result in results:
                lines.append(
                    f'"{result.original_url}","{result.service}","{result.solved_url or ""}",'
                    f'{result.success},{result.response_time or 0},"{result.error or ""}"'
                )
            return '\n'.join(lines)
        
        else:  # text
            output = []
            for i, result in enumerate(results, 1):
                output.append(f"{i}. {result.original_url}")
                output.append(f"   Service: {result.service}")
                if result.success:
                    output.append(f"   ✓ Solved: {result.solved_url}")
                else:
                    output.append(f"   ✗ Failed: {result.error or 'Unknown error'}")
                output.append(f"   Time: {result.response_time:.2f}s")
                output.append("")
            return '\n'.join(output)

# Untuk testing jika dijalankan langsung
if __name__ == "__main__":
    solver = EnhancedABLinksSolver()
    
    test_urls = [
        "https://example.com/test1",
        "https://example.com/test2",
    ]
    
    print("Testing AB Links Solver...")
    results = solver.solve_batch(test_urls)
    
    for result in results:
        print(f"\nURL: {result.original_url}")
        print(f"Success: {result.success}")
        if result.solved_url:
            print(f"Result: {result.solved_url}")

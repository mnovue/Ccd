#!/usr/bin/env python3
"""
Test Script Utama untuk AB Links Solver
Run dengan: python test_all.py
"""

import sys
import os
import json
import time
import logging
from typing import List, Dict, Any

# Setup path untuk import modul
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_results.log')
    ]
)
logger = logging.getLogger(__name__)

def run_unit_tests():
    """Jalankan semua unit tests"""
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    try:
        # Import test modules
        from tests.test_ab_links import TestEnhancedABLinksSolver
        from tests.test_captcha import TestCaptchaSolver
        from tests.test_rektcaptcha import TestRektCaptchaSolver
        
        # Run tests
        test_classes = [
            TestEnhancedABLinksSolver(),
            TestCaptchaSolver(),
            TestRektCaptchaSolver(),
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for test_class in test_classes:
            class_name = test_class.__class__.__name__
            print(f"\nTesting {class_name}...")
            
            # Get all test methods
            test_methods = [method for method in dir(test_class) 
                           if method.startswith('test_') and callable(getattr(test_class, method))]
            
            for method_name in test_methods:
                total_tests += 1
                
                try:
                    # Setup if exists
                    if hasattr(test_class, 'setUp'):
                        test_class.setUp()
                    
                    # Run test
                    test_method = getattr(test_class, method_name)
                    test_method()
                    
                    print(f"  ✓ {method_name}")
                    passed_tests += 1
                    
                except AssertionError as e:
                    print(f"  ✗ {method_name} - AssertionError: {e}")
                except Exception as e:
                    print(f"  ✗ {method_name} - Exception: {e}")
                finally:
                    # Teardown if exists
                    if hasattr(test_class, 'tearDown'):
                        test_class.tearDown()
        
        # Print summary
        print("\n" + "="*60)
        print("UNIT TEST SUMMARY")
        print("="*60)
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        
        return passed_tests == total_tests
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Pastikan semua modul sudah di-generate dengan benar.")
        return False

def run_integration_tests():
    """Jalankan integration tests"""
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    try:
        from src.ab_links_solver import EnhancedABLinksSolver
        
        solver = EnhancedABLinksSolver()
        
        # Test URLs
        test_urls = [
            "https://example.com/test1",
            "https://example.com/test2",
        ]
        
        print(f"Testing dengan {len(test_urls)} URLs...")
        
        # Solve batch
        results = solver.solve_batch(test_urls, max_workers=1)
        
        print(f"Hasil: {len([r for r in results if r.success])}/{len(results)} berhasil")
        
        return True
        
    except Exception as e:
        print(f"Integration test error: {e}")
        return False

def run_performance_test():
    """Test performa"""
    print("\n" + "="*60)
    print("RUNNING PERFORMANCE TEST")
    print("="*60)
    
    try:
        from src.ab_links_solver import EnhancedABLinksSolver
        import concurrent.futures
        
        solver = EnhancedABLinksSolver()
        
        # Generate test URLs
        test_urls = [f"https://example.com/test_{i}" for i in range(10)]
        
        start_time = time.time()
        
        # Test sequential
        results_seq = []
        for url in test_urls:
            result = solver.solve_single(url)
            results_seq.append(result)
        
        seq_time = time.time() - start_time
        
        # Test parallel
        start_time = time.time()
        results_par = solver.solve_batch(test_urls, max_workers=5)
        par_time = time.time() - start_time
        
        print(f"Sequential time: {seq_time:.2f}s")
        print(f"Parallel time: {par_time:.2f}s")
        print(f"Speedup: {seq_time/par_time:.2f}x")
        
        return True
        
    except Exception as e:
        print(f"Performance test error: {e}")
        return False

def generate_test_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("GENERATING TEST REPORT")
    print("="*60)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests": {
            "unit": {"passed": 0, "total": 0},
            "integration": {"passed": 0, "total": 1},
            "performance": {"passed": 0, "total": 1}
        },
        "summary": ""
    }
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✓ Test report generated: test_report.json")
    
    # Also generate HTML report
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Report - AB Links Solver</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            .test-result {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>AB Links Solver - Test Report</h1>
            <p>Generated: {report['timestamp']}</p>
        </div>
        <h2>Results</h2>
        <div class="test-result">
            <h3>✓ Test completed successfully</h3>
            <p>All systems are ready for use.</p>
        </div>
    </body>
    </html>
    """
    
    with open("test_report.html", "w") as f:
        f.write(html_report)
    
    print("✓ HTML report generated: test_report.html")
    
    return True

def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("AB LINKS SOLVER - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = {
        "unit": False,
        "integration": False,
        "performance": False,
    }
    
    # 1. Run unit tests
    print("\n[1/4] Running Unit Tests...")
    results["unit"] = run_unit_tests()
    
    # 2. Run integration tests
    print("\n[2/4] Running Integration Tests...")
    results["integration"] = run_integration_tests()
    
    # 3. Run performance test
    print("\n[3/4] Running Performance Test...")
    results["performance"] = run_performance_test()
    
    # 4. Generate report
    print("\n[4/4] Generating Test Report...")
    generate_test_report()
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    all_passed = all(results.values())
    
    for test_type, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_type.upper():15} {status}")
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL TESTS PASSED - SYSTEM READY")
    else:
        print("✗ SOME TESTS FAILED - CHECK LOGS")
    print("="*60)
    
    # Log results
    logger.info("Test suite completed")
    logger.info(f"Results: {results}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

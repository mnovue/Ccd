#!/usr/bin/env python3
"""
Command-line interface for AB Links Solver
"""

import sys
import argparse
from . import (
    create_solver,
    EnhancedABLinksSolver,
    UniversalReCaptchaSolver,
    get_version,
)

def main():
    parser = argparse.ArgumentParser(
        description="AB Links Solver - Decrypt URL shorteners"
    )
    
    parser.add_argument(
        'urls',
        nargs='*',
        help='URLs to solve'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['basic', 'captcha', 'recaptcha', 'universal'],
        default='basic',
        help='Type of solver to use'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='File containing URLs (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'AB Links Solver {get_version()}'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Collect URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
    
    if not urls:
        print("Error: No URLs provided")
        parser.print_help()
        sys.exit(1)
    
    # Create solver
    try:
        if args.type == 'basic':
            solver = EnhancedABLinksSolver()
        elif args.type == 'universal':
            solver = UniversalReCaptchaSolver()
        else:
            solver = create_solver(args.type)
    except Exception as e:
        print(f"Error creating solver: {e}")
        sys.exit(1)
    
    # Solve URLs
    results = []
    for url in urls:
        try:
            if args.type == 'basic':
                result = solver.solve_single(url)
            else:
                result = solver.solve(url)
            results.append(result)
        except Exception as e:
            print(f"Error solving {url}: {e}")
            continue
    
    # Output results
    if args.output == 'json':
        import json
        output = []
        for result in results:
            if hasattr(result, '__dict__'):
                output.append(result.__dict__)
            else:
                output.append(result)
        print(json.dumps(output, indent=2, default=str))
    
    elif args.output == 'csv':
        print('URL,Success,Result,Error,Time')
        for result in results:
            url = getattr(result, 'original_url', 'Unknown')
            success = getattr(result, 'success', False)
            solved = getattr(result, 'solved_url', getattr(result, 'solution', ''))
            error = getattr(result, 'error', '')
            time = getattr(result, 'response_time', getattr(result, 'execution_time', 0))
            print(f'"{url}","{success}","{solved}","{error}",{time}')
    
    else:  # text format
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {getattr(result, 'original_url', 'Unknown')}")
            
            success = getattr(result, 'success', False)
            if success:
                print(f"   ✅ Success")
                result_value = getattr(result, 'solved_url', getattr(result, 'solution', ''))
                print(f"   Result: {result_value}")
            else:
                print(f"   ❌ Failed")
                error = getattr(result, 'error', 'Unknown error')
                print(f"   Error: {error}")
            
            # Show additional info if verbose
            if args.verbose:
                for key, value in result.__dict__.items():
                    if key not in ['original_url', 'success', 'solved_url', 'solution', 'error']:
                        print(f"   {key}: {value}")

if __name__ == "__main__":
    main()

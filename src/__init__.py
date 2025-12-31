"""
AB Links Solver - Decrypt URL shorteners with CAPTCHA solving capabilities

This package provides tools to solve and decrypt various URL shortener services
including AdFly, Linkvertise, GyaniLinks, etc. with integrated CAPTCHA solving.

Modules:
    ab_links_solver: Main solver for URL shorteners
    captcha_solver: Solver for text and math CAPTCHAs
    rektcaptcha_solver: Solver for reCAPTCHA challenges
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2024"

# Package metadata
__all__ = [
    'EnhancedABLinksSolver',
    'CaptchaSolver',
    'RektCaptchaSolver',
    'UniversalReCaptchaSolver',
    'SolveResult',
    'CaptchaResult',
    'ReCaptchaResult',
]

# Version tuple for comparison
version_info = (1, 0, 0)

# Import key classes for easy access
try:
    from .ab_links_solver import EnhancedABLinksSolver, SolveResult
    from .captcha_solver import CaptchaSolver, CaptchaResult
    from .rektcaptcha_solver import RektCaptchaSolver, ReCaptchaResult, UniversalReCaptchaSolver
    
    # Convenience function
    def create_solver(solver_type='basic', **kwargs):
        """
        Create a solver instance based on type.
        
        Args:
            solver_type: 'basic', 'captcha', or 'universal'
            **kwargs: Additional arguments for solver
        
        Returns:
            Solver instance
        """
        if solver_type == 'basic':
            return EnhancedABLinksSolver(**kwargs)
        elif solver_type == 'captcha':
            return CaptchaSolver(**kwargs)
        elif solver_type == 'universal':
            return UniversalReCaptchaSolver(**kwargs)
        elif solver_type == 'recaptcha':
            return RektCaptchaSolver(**kwargs)
        else:
            raise ValueError(f"Unknown solver type: {solver_type}")
            
    # Package level functions
    def get_version():
        """Return package version as string"""
        return __version__
        
    def get_version_info():
        """Return package version as tuple"""
        return version_info
        
except ImportError as e:
    # Handle partial imports gracefully
    print(f"Warning: Some imports failed: {e}")
    
    # Define placeholder classes if imports fail
    class EnhancedABLinksSolver:
        """Placeholder - Failed to import actual class"""
        def __init__(self, *args, **kwargs):
            raise ImportError("Failed to import EnhancedABLinksSolver")
    
    class SolveResult:
        """Placeholder - Failed to import actual class"""
        pass
    
    class CaptchaSolver:
        """Placeholder - Failed to import actual class"""
        def __init__(self, *args, **kwargs):
            raise ImportError("Failed to import CaptchaSolver")
    
    class CaptchaResult:
        """Placeholder - Failed to import actual class"""
        pass
    
    class RektCaptchaSolver:
        """Placeholder - Failed to import actual class"""
        def __init__(self, *args, **kwargs):
            raise ImportError("Failed to import RektCaptchaSolver")
    
    class ReCaptchaResult:
        """Placeholder - Failed to import actual class"""
        pass
    
    class UniversalReCaptchaSolver:
        """Placeholder - Failed to import actual class"""
        def __init__(self, *args, **kwargs):
            raise ImportError("Failed to import UniversalReCaptchaSolver")

# Logging configuration
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create package logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Package initialization message
logger.info(f"AB Links Solver v{__version__} initialized")

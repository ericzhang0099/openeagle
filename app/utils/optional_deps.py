"""
Optional Dependencies Handler

Handles optional dependencies gracefully.
If torch is not installed, provides fallback implementations or clear errors.
"""

import importlib.util
import warnings

# Check if torch is available
_torch_available = importlib.util.find_spec("torch") is not None

if _torch_available:
    import torch
    import torch.nn as nn
else:
    # Create dummy classes for type hints
    class torch:
        class Tensor:
            pass
        @staticmethod
        def tensor(*args, **kwargs):
            raise ImportError("PyTorch is not installed. Install with: pip install torch")
    
    class nn:
        class Module:
            pass

# Check if networkx is available
_nx_available = importlib.util.find_spec("networkx") is not None

if not _nx_available:
    warnings.warn(
        "networkx is not installed. Causal graph visualization will not work. "
        "Install with: pip install networkx",
        UserWarning
    )


def require_torch(func):
    """Decorator to check if torch is available."""
    def wrapper(*args, **kwargs):
        if not _torch_available:
            raise ImportError(
                "PyTorch is required for this feature. "
                "Install with: pip install torch torchvision "
                "or use: pip install -r requirements-full.txt"
            )
        return func(*args, **kwargs)
    return wrapper


def is_torch_available():
    """Check if PyTorch is available."""
    return _torch_available

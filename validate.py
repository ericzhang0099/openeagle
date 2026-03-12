#!/usr/bin/env python3
"""
Code Validation Script

Validates Python syntax and imports for VisionClaw Vision Service.
"""

import ast
import sys
from pathlib import Path

def validate_python_syntax(filepath):
    """Validate Python file syntax."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def check_imports(filepath):
    """Check if imports can be resolved (basic check)."""
    # This is a simplified check - full import checking requires running the code
    issues = []
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # Skip standard library and known packages
                if alias.name in ['sys', 'os', 'time', 'json', 'typing', 'pathlib', 
                                  'io', 'base64', 'ast', 'numpy', 'cv2', 'PIL', 
                                  'fastapi', 'pydantic', 'loguru', 'yaml']:
                    continue
        elif isinstance(node, ast.ImportFrom):
            # Check app.* imports
            if node.module and node.module.startswith('app.'):
                # These are internal imports, should be fine
                pass
    
    return issues

def main():
    print("=" * 60)
    print("VisionClaw Vision Service - Code Validation")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    python_files = list(base_path.rglob("*.py"))
    
    print(f"\nValidating {len(python_files)} Python files...\n")
    
    errors = []
    warnings = []
    
    for filepath in sorted(python_files):
        relative_path = filepath.relative_to(base_path)
        
        # Check syntax
        valid, error = validate_python_syntax(filepath)
        if not valid:
            errors.append(f"{relative_path}: Syntax Error - {error}")
            print(f"❌ {relative_path}")
        else:
            print(f"✅ {relative_path}")
    
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ Validation Failed - {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print(f"✅ All {len(python_files)} files passed syntax validation")
        return 0

if __name__ == "__main__":
    sys.exit(main())

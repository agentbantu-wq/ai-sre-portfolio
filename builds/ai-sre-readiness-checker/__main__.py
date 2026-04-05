#!/usr/bin/env python3

"""
AI-SRE-Readiness-Checker
Lightweight evaluation framework for AI SRE tools
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Optionally run CLI
if __name__ == '__main__':
    from src.cli import main
    main()

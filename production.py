#!/usr/bin/env python3
"""
Production deployment for ASIMOV AI - Forces correct application loading
"""

# Import the exact same application that's working in console
from bulletproof_startup import start_bulletproof_asimov

if __name__ == "__main__":
    # Use the same startup process that works in console
    start_bulletproof_asimov()
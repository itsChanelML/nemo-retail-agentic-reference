"""
Vercel serverless entry point.
Vercel runs Python functions via the @vercel/python runtime.
This file re-exports the FastAPI app instance.
"""

import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "api"))

from main import app  # noqa: F401 — Vercel expects `app`

"""
Vercel serverless entry point.
Vercel runs Python functions via the @vercel/python runtime.
This file re-exports the FastAPI app instance.
"""

import sys
import os

# Add this file's own directory (api/) to the path
sys.path.insert(0, os.path.dirname(__file__))

from main import app  # noqa: F401 — Vercel expects `app`

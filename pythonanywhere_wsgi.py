"""
WSGI Configuration for PythonAnywhere
Auto-detects project path - works after git pull without manual edits
"""

import sys
import os
from pathlib import Path

# 1. Auto-detect project root from this file location
# This file sits at: servicoscrc/pythonanywhere_wsgi.py
# So parent is the project root
project_home = str(Path(__file__).resolve().parent)

# 2. Set BASE_DIR env var for prefrio_stats.py and other modules
os.environ['BASE_DIR'] = project_home

# 3. Add to Python path
if project_home not in sys.path:
    sys.path.insert(0, project_home)
    sys.path.insert(0, os.path.join(project_home, 'backend/scripts'))

# 4. Force production mode BEFORE importing app
# Ensures IS_PRODUCTION=true regardless of .env state
os.environ.setdefault('IS_PRODUCTION', 'true')

# 5. Load environment variables from .env
# load_dotenv respects existing env vars (won't overwrite)
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

# Debug output (visible in PythonAnywhere error log)
print(f"[WSGI] Project home: {project_home}")
print(f"[WSGI] BASE_DIR: {os.environ.get('BASE_DIR')}")
print(f"[WSGI] IS_PRODUCTION: {os.environ.get('IS_PRODUCTION')}")
print(f"[WSGI] .env loaded from: {env_path}")
print(f"[WSGI] .env exists: {os.path.exists(env_path)}")

# 6. Import Flask application
from backend.scripts.app import app as application

# Variable 'application' is the standard uWSGI/PythonAnywhere expects

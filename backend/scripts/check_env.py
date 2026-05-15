"""
Check and print Config values loaded by the backend.
Run from backend directory with virtualenv activated:

  cd /Users/ekakhoirotin/Sites/MiroFish/backend
  source .venv/bin/activate
  python scripts/check_env.py

This will help verify whether MiroFish/backend/app/config.py successfully loads your .env.
"""

import os
import sys
_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_root = os.path.dirname(_this_dir)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from app.config import Config

def mask(s: str) -> str:
    if not s:
        return '<EMPTY>'
    if len(s) <= 8:
        return s
    return s[:4] + '...' + s[-4:]

print('Loaded Config values:')
print('  LLM_API_KEY:', mask(Config.LLM_API_KEY))
print('  LLM_BASE_URL:', Config.LLM_BASE_URL)
print('  LLM_MODEL_NAME:', Config.LLM_MODEL_NAME)
print('  ZEP_API_KEY:', mask(Config.ZEP_API_KEY))
print('\nAlso show environment variables visible to this process:')
for k in ['LLM_API_KEY', 'LLM_BASE_URL', 'LLM_MODEL_NAME', 'ZEP_API_KEY']:
    print(f'  env {k}:', mask(os.environ.get(k)))

print('\n.env location expected by config.py:')
print('  backend/app/config.py looks for .env at:', os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', '.env')))

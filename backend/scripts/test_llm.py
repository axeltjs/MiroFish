"""
Simple script to test LLM connectivity using project's LLMClient.
Run from project backend directory (activate venv if any):

  python scripts/test_llm.py

It will print the raw response and any exception (including traceback) to help debug 500 errors in ontology generation.
"""

import os
import sys
import traceback

# Ensure backend package is importable regardless of current working directory
# This file lives at: MiroFish/backend/scripts/test_llm.py
# We want to add MiroFish/backend to sys.path so `import app` works.
_this_dir = os.path.dirname(os.path.abspath(__file__))
_backend_root = os.path.dirname(_this_dir)
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from app.utils.llm_client import LLMClient


def main():
    try:
        client = LLMClient()
        messages = [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Say hello in one sentence."}
        ]
        print("Calling LLM.chat(...)")
        resp = client.chat(messages=messages, temperature=0.0, max_tokens=100)
        print("Raw chat response:\n", resp)

        print("Calling LLM.chat_json(...) (expecting valid JSON)")
        # Use a simple JSON response format to test parser path
        messages_json = [
            {"role": "system", "content": "You are a JSON-only assistant. Reply with a JSON object only."},
            {"role": "user", "content": "{\"greeting\": \"hello\"}"}
        ]
        resp_json = client.chat_json(messages=messages_json, temperature=0.0, max_tokens=200)
        print("Parsed JSON response:\n", resp_json)

    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()


if __name__ == '__main__':
    main()

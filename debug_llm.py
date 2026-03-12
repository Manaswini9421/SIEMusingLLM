import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env
env_path = Path("backend/.env")
load_dotenv(dotenv_path=env_path)

print(f"HF Key: {os.getenv('HUGGINGFACE_API_KEY')}")

from backend.services.llm_service import LLMService

try:
    print("Initializing LLM Service...")
    llm = LLMService()
    print("Sending test prompt...")
    response = llm.get_response("Hello, are you working?")
    print(f"LLM Response: {response}")
except Exception as e:
    print(f"LLM EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

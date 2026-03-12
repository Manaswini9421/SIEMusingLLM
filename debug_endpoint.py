import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env
env_path = Path("backend/.env")
load_dotenv(dotenv_path=env_path)

from backend.main import chat_endpoint
from backend.models import ChatRequest

async def test():
    print("Starting test...")
    req = ChatRequest(session_id="test", message="hello", index_name="wazuh-alerts-*")
    try:
        resp = await chat_endpoint(req)
        print("Response:", resp)
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")

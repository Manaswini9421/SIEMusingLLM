import google.generativeai as genai
from backend.config import GOOGLE_API_KEY
import traceback
import time

class LLMService:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def get_response(self, prompt: str):
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                print(f"LLM Error on attempt {attempt + 1}/{self.max_retries}: {str(e)[:200]}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    print("ERROR: Cannot reach Gemini API. Returning fallback response.")
                    return self._get_fallback_response(prompt)

        # If all retries failed
        return self._get_fallback_response(prompt)

    def _get_fallback_response(self, prompt: str):
        """Provide basic fallback responses when LLM is unavailable"""
        if "Elasticsearch DSL" in prompt or "User Query:" in prompt:
            return '''
            {
                "query": {
                    "match_all": {}
                },
                "size": 100
            }
            '''
        elif "cybersecurity data" in prompt or "Query Intent:" in prompt:
            return '''
            {
                "summary": "Unable to analyze data - LLM service is currently unavailable. The query executed successfully, but detailed analysis cannot be provided. Please check your API key or try again later.",
                "metrics": {
                    "Status": "LLM Offline",
                    "Query Result": "Available"
                }
            }
            '''
        return "LLM service unavailable. Please check your API key and try again."

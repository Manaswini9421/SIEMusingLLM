from huggingface_hub import InferenceClient
from backend.config import HUGGINGFACE_API_KEY
import traceback
import time

class LLMService:
    def __init__(self):
        # Use the InferenceClient (current recommended way)
        # Using Qwen2.5-7B-Instruct which is very strong and usually warm on Inference API
        self.model_id = "Qwen/Qwen2.5-7B-Instruct"
        self.client = InferenceClient(
            model=self.model_id,
            token=HUGGINGFACE_API_KEY,
            timeout=30  # Add timeout
        )
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def get_response(self, prompt: str):
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                # chat_completion is more robust for instruct models
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat_completion(
                    messages=messages,
                    max_tokens=1024
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check if it's a network/connection error
                if 'failed to resolve' in error_str or 'max retries' in error_str or 'connection' in error_str:
                    print(f"Network error on attempt {attempt + 1}/{self.max_retries}: {str(e)[:200]}")
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        # Final attempt - return fallback template
                        print("ERROR: Cannot reach Hugging Face API. Returning fallback response.")
                        return self._get_fallback_response(prompt)
                else:
                    # Non-network error, try text_generation fallback
                    print(f"LLM Error (chat_completion): {str(e)[:200]}")
                    try:
                        return self.client.text_generation(prompt, max_new_tokens=1024)
                    except Exception as e2:
                        print(f"LLM Error (text_generation): {str(e2)[:200]}")
                        if attempt < self.max_retries - 1:
                            time.sleep(self.retry_delay)
                            continue
                        else:
                            return self._get_fallback_response(prompt)
        
        # If all retries failed
        return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str):
        """Provide basic fallback responses when LLM is unavailable"""
        # Check if this is a query generation request
        if "Elasticsearch DSL" in prompt or "User Query:" in prompt:
            # Return a basic match_all query
            return '''
            {
                "query": {
                    "match_all": {}
                },
                "size": 100
            }
            '''
        
        # Check if this is a response formatting request
        elif "cybersecurity data" in prompt or "Query Intent:" in prompt:
            return '''
            {
                "summary": "Unable to analyze data - LLM service is currently unavailable. The query executed successfully, but detailed analysis cannot be provided. Please check your internet connection or try again later.",
                "metrics": {
                    "Status": "LLM Offline",
                    "Query Result": "Available"
                }
            }
            '''
        
        # Generic fallback
        return "LLM service unavailable. Please check your internet connection and try again."

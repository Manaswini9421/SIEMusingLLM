from huggingface_hub import InferenceClient
from backend.config import HUGGINGFACE_API_KEY
import traceback

class LLMService:
    def __init__(self):
        # Use the InferenceClient (current recommended way)
        # Using Qwen2.5-7B-Instruct which is very strong and usually warm on Inference API
        self.model_id = "Qwen/Qwen2.5-7B-Instruct"
        self.client = InferenceClient(
            model=self.model_id,
            token=HUGGINGFACE_API_KEY
        )

    def get_response(self, prompt: str):
        try:
            # chat_completion is more robust for instruct models
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error (InferenceClient): {str(e)}")
            # Fallback to older text_generation if chat_completion not supported for model
            try:
                return self.client.text_generation(prompt, max_new_tokens=1024)
            except Exception as e2:
                traceback.print_exc()
                return str(e)

import json
import traceback
import re
from backend.services.llm_service import LLMService

class QueryGenerator:
    def __init__(self):
        self.llm_service = LLMService()

    def generate_dsl(self, user_query: str, index_mapping: dict, history: str = "") -> dict:
        """
        Generates Elasticsearch DSL from natural language query.
        """
        try:
            prompt = f"""
            You are an expert in Elasticsearch and cybersecurity.
            Your task is to translate the following natural language query into a valid Elasticsearch DSL query (JSON format).
            
            Index Mapping (Schema):
            {json.dumps(index_mapping, indent=2)[:2000]} # Truncated for token limit safety
            
            Conversation History:
            {history}
            
            User Query: "{user_query}"
            
            Guidelines:
            1. Output ONLY the JSON DSL query. 
            2. Do not include markdown formatting or explanations.
            3. Ensure the JSON is valid and properly closed.
            4. Do not generate excessively long strings for match values unless specifically requested.
            """
            
            response = self.llm_service.get_response(prompt)
            
            # 1. Clean up surrounding markdown or extra text
            clean_response = response.strip()
            if "```" in clean_response:
                # Try to extract content between triple backticks
                json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_response, re.DOTALL)
                if json_match:
                    clean_response = json_match.group(1)
                else:
                    clean_response = clean_response.replace("```json", "").replace("```", "").strip()

            # 2. Extract only the first complete JSON object (handles extra text after JSON)
            json_match = re.search(r"(\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})", clean_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(1)
            
            # 3. Heuristic repair for missing closing braces (common in truncated LLM outputs)
            open_braces = clean_response.count('{')
            close_braces = clean_response.count('}')
            if open_braces > close_braces:
                # Basic attempt to close JSON
                clean_response += '}' * (open_braces - close_braces)
            
            try:
                return json.loads(clean_response)
            except json.JSONDecodeError as e:
                # If still failing, try one more aggressive extraction
                print(f"JSON decode error: {e}")
                print(f"Problematic JSON: {clean_response[:500]}")
                json_match = re.search(r"(\{[^}]*\})", clean_response)
                if json_match:
                    return json.loads(json_match.group(1))
                raise

        except Exception as e:
            traceback.print_exc()
            return {
                "error": "Failed to generate valid JSON DSL", 
                "message": str(e),
                "raw_response": clean_response if 'clean_response' in locals() else str(e)
            }

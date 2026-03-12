import traceback
from backend.services.llm_service import LLMService

class ResponseFormatter:
    def __init__(self):
        self.llm_service = LLMService()

    def format_response(self, raw_data, query_intent: str) -> dict:
        """
        Formats the raw Elasticsearch results into a narrative summary and structured data.
        """
        try:
            data_str = str(raw_data)[:5000] # Truncate for token limit
            
            prompt = f"""
            Analyze the following cybersecurity data returned from a SIEM query.
            
            Query Intent: "{query_intent}"
            
            Data:
            {data_str}
            
            Please provide:
            1. A concise narrative summary of the findings (max 3-4 sentences).
            2. Structured metrics for visualization. Include at least 3-4 numeric values if possible (e.g., total_events, high_severity, unique_sources, failed_logins).
            
            Output format should be STRICT JSON:
            {{
                "summary": "...",
                "metrics": {{
                    "Total Events": 10,
                    "High Severity": 2,
                    "Unique Sources": 5,
                    ...
                }}
            }}
            """
            
            response = self.llm_service.get_response(prompt)
            
            # Robust cleanup
            clean_response = response.strip()
            
            # Remove markdown code blocks
            if "```" in clean_response:
                import re
                json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_response, re.DOTALL)
                if json_match:
                    clean_response = json_match.group(1)
                else:
                    clean_response = clean_response.replace("```json", "").replace("```", "").strip()
            
            # Extract only the JSON object (handle extra text after JSON)
            import re
            json_match = re.search(r"(\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\})", clean_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(1)
            
            import json
            return json.loads(clean_response)
        except Exception as e:
            traceback.print_exc()
            # If everything fails, return basic info
            return {"summary": str(raw_data)[:500], "metrics": {"error": str(e)}}

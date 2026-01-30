from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ChatRequest, ChatResponse
from backend.services.siem_connector import SIEMConnector
from backend.services.query_generator import QueryGenerator
from backend.services.context_manager import ContextManager
from backend.services.response_formatter import ResponseFormatter
import uvicorn
import os
import traceback

app = FastAPI(title="SIEM LLM Interface")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
siem_connector = SIEMConnector()
query_generator = QueryGenerator()
context_manager = ContextManager()
response_formatter = ResponseFormatter()

@app.get("/")
def read_root():
    return {"status": "online", "message": "SIEM LLM Interface Backend"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Update Context
        context_manager.add_message(request.session_id, "user", request.message)
        history = context_manager.get_history_string(request.session_id)
        
        # 2. Get Index Mapping (Mocking 'auditbeat-*' or taking from request if we want to be dynamic)
        # Ideally we should infer or have a default. Let's try to fetch all indices or a specific one.
        # For this MVP, we will fetch mapping of 'wazuh-alerts-*' or 'filebeat-*' or similar if available,
        # or just pass a generic schema if connection fails.
        
        # Check if we have any data at all
        indices = siem_connector.get_indices()
        if not indices:
            raise HTTPException(
                status_code=503,
                detail="Connected to Elasticsearch, but no data found. Please ensure your SIEM (Wazuh/Filebeat) is ingesting logs."
            )

        # Try getting mapping for the specific target
        target_index = request.index_name if request.index_name else "wazuh-alerts-*"
        mapping = siem_connector.get_mapping(target_index)
        
        if not mapping or "error" in mapping:
            err_msg = mapping.get("error") if mapping else "Index not found"
            raise HTTPException(
                status_code=404, 
                detail=f"Index '{target_index}' not found or has no mapping. Available indices: {[i.get('index') for i in indices]}"
            )

        # 3. Generate DSL
        dsl_query = query_generator.generate_dsl(request.message, mapping, history)
        
        if "error" in dsl_query:
            # If generation failed
            return ChatResponse(response_text="Failed to generate query.", dsl_query=dsl_query)
            
        # 4. Execute Query
        raw_results = siem_connector.execute_query(target_index, dsl_query)
        
        # 5. Format Response
        formatted = response_formatter.format_response(raw_results, request.message)
        
        # 6. Final Response Construction
        reply_text = formatted.get("summary", "Query executed successfully.")
        
        context_manager.add_message(request.session_id, "assistant", reply_text)
        
        return ChatResponse(
            response_text=reply_text,
            data=formatted.get("metrics", {}),
            dsl_query=dsl_query
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

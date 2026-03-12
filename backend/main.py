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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:3000",  # Common alternative port
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
siem_connector = SIEMConnector()
query_generator = QueryGenerator()
context_manager = ContextManager()
response_formatter = ResponseFormatter()

@app.on_event("startup")
async def startup_event():
    print("\n" + "="*50)
    print("SIEM LLM Interface Startup Check")
    print("="*50)
    if siem_connector.mock_mode:
        print("STATUS: Running in MOCK MODE (Sample Data)")
        print("FIX: Set MOCK_SIEM=false in backend/.env to use real data.")
    else:
        print(f"STATUS: Attempting to connect to SIEM at {siem_connector.url}...")
        indices = siem_connector.get_indices()
        if isinstance(indices, dict) and "error" in indices:
            print(f"WARNING: SIEM Connection Failed!")
            print(f"ERROR: {indices['error']}")
            print("REMEDY: Start your Elasticsearch/Wazuh server or set MOCK_SIEM=true in backend/.env")
        else:
            print("STATUS: SIEM Connected Successfully!")
    print("="*50 + "\n")

@app.get("/")
def read_root():
    return {"status": "online", "message": "SIEM LLM Interface Backend"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Update Context
        print("DEBUG: Step 1 - Update Context")
        context_manager.add_message(request.session_id, "user", request.message)
        history = context_manager.get_history_string(request.session_id)
        
        # 2. Get Index Mapping
        print("DEBUG: Step 2 - Get Indices")
        indices = siem_connector.get_indices()
        print(f"DEBUG: Indices result: {indices}")
        
        if isinstance(indices, dict) and "error" in indices:
            err_msg = indices['error']
            status_code = 503 if "Connection" in err_msg else 500
            raise HTTPException(
                status_code=status_code,
                detail=f"SIEM Connectivity Error: {err_msg}"
            )
        
        if not indices:
            raise HTTPException(
                status_code=404,
                detail="Connected to SIEM, but no active indices were found."
            )

        # Try getting mapping for the specific target
        target_index = request.index_name if request.index_name else "wazuh-alerts-*"
        print(f"DEBUG: Step 2b - Get Mapping for {target_index}")
        mapping = siem_connector.get_mapping(target_index)
        print(f"DEBUG: Mapping result type: {type(mapping)}")
        
        # Check if mapping is an error
        if isinstance(mapping, dict) and "error" in mapping:
            err_msg = mapping.get("error", "Unknown error")
            print(f"DEBUG: Mapping error: {err_msg}")
            # Get index names safely
            index_names = [i.get('index', 'unknown') for i in indices if isinstance(i, dict)]
            raise HTTPException(
                status_code=404, 
                detail=f"Index '{target_index}' not found or has no mapping. Available indices: {index_names}. Error: {err_msg}"
            )
        
        if not mapping:
            raise HTTPException(
                status_code=404,
                detail=f"Index '{target_index}' returned empty mapping"
            )

        # 3. Generate DSL
        print("DEBUG: Step 3 - Generate DSL")
        dsl_query = query_generator.generate_dsl(request.message, mapping, history)
        print(f"DEBUG: DSL Query: {dsl_query}")
        
        if "error" in dsl_query:
            # If generation failed
            return ChatResponse(response_text="Failed to generate query.", dsl_query=dsl_query)
            
        # 4. Execute Query
        print("DEBUG: Step 4 - Execute Query")
        raw_results = siem_connector.execute_query(target_index, dsl_query)
        print(f"DEBUG: Raw Results Type: {type(raw_results)}")
        
        # 5. Format Response
        print("DEBUG: Step 5 - Format Response")
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

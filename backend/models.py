from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    session_id: str
    message: str
    index_name: Optional[str] = None # Optional, normally inferred or global

class ChatResponse(BaseModel):
    response_text: str
    data: Optional[Any] = None
    dsl_query: Optional[dict] = None

class ReportRequest(BaseModel):
    topic: str
    time_range: str = "last 24 hours"

class ReportResponse(BaseModel):
    summary: str
    charts_data: Optional[Any] = None

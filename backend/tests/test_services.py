from unittest.mock import MagicMock, patch
from backend.services.context_manager import ContextManager
from backend.services.response_formatter import ResponseFormatter

# --- Context Manager Tests ---
def test_context_manager_add_and_get_history():
    cm = ContextManager()
    session_id = "test_session_123"
    
    # Initial state should be empty string
    assert cm.get_history_string(session_id) == ""

    # Add user message
    cm.add_message(session_id, "user", "Hello")
    history = cm.get_history_string(session_id)
    assert "user: Hello" in history

    # Add assistant message
    cm.add_message(session_id, "assistant", "Hi there")
    history = cm.get_history_string(session_id)
    assert "user: Hello" in history
    assert "assistant: Hi there" in history

def test_context_manager_limit():
    cm = ContextManager()
    session_id = "test_session_limit"
    
    # Add many messages
    for i in range(20):
        cm.add_message(session_id, "user", f"msg {i}")
    
    history = cm.get_history_string(session_id)
    assert "msg 19" in history

# --- Response Formatter Tests ---
@patch("backend.services.response_formatter.LLMService")
def test_response_formatter_empty(mock_llm_cls):
    # Setup Mock LLM
    mock_llm = mock_llm_cls.return_value
    mock_llm.get_response.return_value = '{"summary": "No results found", "metrics": {"total_hits": 0}}'
    
    rf = ResponseFormatter()
    raw_results = {"hits": {"total": {"value": 0}, "hits": []}}
    
    formatted = rf.format_response(raw_results, "Find something")
    assert formatted["metrics"]["total_hits"] == 0
    assert "No results found" in formatted["summary"]

@patch("backend.services.response_formatter.LLMService")
def test_response_formatter_hits(mock_llm_cls):
    # Setup Mock LLM
    mock_llm = mock_llm_cls.return_value
    mock_llm.get_response.return_value = '{"summary": "Found 5 events", "metrics": {"total_hits": 5, "records": [{"msg": "error"}]}}'

    rf = ResponseFormatter()
    raw_results = {
        "hits": {
            "total": {"value": 5},
            "hits": [
                {"_source": {"timestamp": "2023-01-01", "message": "error occurred"}}
            ]
        }
    }
    
    formatted = rf.format_response(raw_results, "Show errors")
    assert formatted["metrics"]["total_hits"] == 5
    assert len(formatted["metrics"]["records"]) == 1
    assert "Found 5 events" in formatted["summary"]

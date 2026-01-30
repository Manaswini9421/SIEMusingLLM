import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from backend.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "message": "SIEM LLM Interface Backend"}

@patch("backend.main.siem_connector")
@patch("backend.main.query_generator")
@patch("backend.main.context_manager")
@patch("backend.main.response_formatter")
def test_chat_endpoint(mock_formatter, mock_context, mock_query_generator, mock_siem):
    # Setup Mocks
    mock_siem.get_mapping.return_value = {"properties": {}}
    mock_siem.execute_query.return_value = {"hits": {"total": {"value": 1}, "hits": []}}
    
    mock_query_generator.generate_dsl.return_value = {"query": {"match_all": {}}}
    
    mock_context.get_history_string.return_value = "user: test"
    
    mock_formatter.format_response.return_value = {
        "summary": "Everything looks normal.",
        "metrics": {"threat_level": "low"}
    }
    
    # Test Request
    payload = {
        "message": "Find failed logins",
        "session_id": "test_sess",
        "index_name": "wazuh-alerts-*"
    }
    
    response = client.post("/chat", json=payload)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "response_text" in data
    assert "dsl_query" in data
    assert data["dsl_query"] == {"query": {"match_all": {}}}
    
    # Verify interactions
    mock_context.add_message.assert_called()
    mock_siem.execute_query.assert_called_once()


@patch("backend.main.query_generator")
def test_chat_dsl_failure(mock_query_generator):
    # Test handling of DSL generation error
    mock_query_generator.generate_dsl.return_value = {"error": "Cannot generate"}
    
    payload = {
        "message": "Bad query",
        "session_id": "test_sess"
    }
    
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["response_text"] == "Failed to generate query."

# Copilot Instructions for SIEM LLM Interface

## Project Overview
This is a full-stack application that enables natural language querying of SIEM data (Elasticsearch/Wazuh). It translates user queries to Elasticsearch DSL using an LLM, executes them, and formats results for display.

**Core workflow:** User query → LLM generates DSL → Execute against SIEM → Format/summarize results

## Architecture

### Backend (Python FastAPI)
- **Entry:** [main.py](../../backend/main.py) - FastAPI app with `/chat` endpoint
- **Services layer:**
  - `SIEMConnector` - Elasticsearch HTTP client with auth (API key or user/password)
  - `QueryGenerator` - Converts natural language → Elasticsearch DSL using LLM
  - `LLMService` - Hugging Face Inference API (Qwen2.5-7B-Instruct model)
  - `ContextManager` - In-memory session-based conversation history
  - `ResponseFormatter` - Summarizes raw Elasticsearch results using LLM
- **Models:** [models.py](../../backend/models.py) - `ChatRequest` (session_id, message, index_name), `ChatResponse` (response_text, data, dsl_query)

### Frontend (React + Vite + Tailwind)
- **Entry:** [main.jsx](../../frontend/src/main.jsx)
- **Core component:** [ChatInterface.jsx](../../frontend/src/components/ChatInterface.jsx) - Chat UI with message history, loading states, visualization support
- **API layer:** [api.js](../../frontend/src/services/api.js) - Axios client wrapping `/chat` endpoint

### Data Flow
1. Frontend sends `ChatRequest` to `/chat`
2. `ContextManager` adds user message to session history
3. `SIEMConnector` fetches index mapping from Elasticsearch
4. `QueryGenerator` prompts LLM with: user query + mapping schema + conversation history → DSL
5. `SIEMConnector` executes DSL query
6. `ResponseFormatter` prompts LLM to summarize results with metrics
7. Response returned with narrative summary + structured data for charts

## Critical Patterns & Conventions

### LLM Integration Pattern
- **Model:** Qwen2.5-7B-Instruct via Hugging Face (warm cache on inference API)
- **Prompts include context:** schema info, history, task guidelines
- **Post-processing:** Strip markdown backticks, fix JSON truncation (add missing closing braces)
- **Fallback:** If `chat_completion` fails, retry with `text_generation`
- **Location:** [llm_service.py](../../backend/services/llm_service.py)

### Query Generation Pattern
- **Input:** User natural language query + Elasticsearch mapping + chat history
- **Process:** LLM generates raw DSL → regex extraction from markdown → JSON repair
- **Common issue:** LLM outputs can be truncated or wrapped in backticks
- **Repair heuristic:** Count opening/closing braces, add missing `}`
- **Location:** [query_generator.py](../../backend/services/query_generator.py) (lines 30-40 for cleanup logic)

### Error Handling Strategy
- **HTTP exceptions:** Catch and return 400/404/503 with descriptive messages
- **Missing indices:** Return 503 if no indices exist in Elasticsearch
- **Query generation failures:** Return `ChatResponse` with "Failed to generate query" and error dict
- **Graceful degradation:** Response formatter falls back to raw data string + error metrics if JSON parsing fails

### Session Management
- **Lightweight:** In-memory dictionary keyed by session_id
- **No persistence:** Sessions lost on backend restart
- **Scalability note:** For production, replace with Redis/database
- **Location:** [context_manager.py](../../backend/services/context_manager.py)

### Configuration
- **Env-based:** Load from `.env` in backend directory (see [config.py](../../backend/config.py))
- **Required vars:** `HUGGINGFACE_API_KEY`, `ELASTICSEARCH_URL`, `ELASTICSEARCH_USER`, `ELASTICSEARCH_PASSWORD`
- **Optional:** `ELASTICSEARCH_API_KEY` (takes precedence over user/password)

## Development Workflows

### Running the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- Reload mode watches for changes
- Accessible at `http://localhost:8000` or `https://localhost:8000` (HTTPS for ES)

### Running the Frontend
```bash
cd frontend
npm install
npm run dev
```
- Vite dev server at `http://localhost:5173`
- Hot module replacement enabled

### Testing
- **Backend:** Use pytest with mocking (see [test_api.py](../../backend/tests/test_api.py))
- **Mocking pattern:** Mock `SIEMConnector`, `QueryGenerator`, `ContextManager`, `ResponseFormatter` in main
- **Run:** `pytest backend/tests/`

### SSL/HTTPS Notes
- Elasticsearch uses self-signed certs locally (suppress warnings with `urllib3.disable_warnings()`)
- Frontend makes requests to backend via CORS (wildcard origins enabled)

## Key Files & Responsibilities

| File | Purpose | Key Implementation Detail |
|------|---------|---------------------------|
| [main.py](../../backend/main.py) | API orchestration | 6-step flow: update context → get mapping → generate DSL → execute → format → return |
| [llm_service.py](../../backend/services/llm_service.py) | LLM wrapper | Qwen2.5-7B, chat_completion with fallback to text_generation |
| [query_generator.py](../../backend/services/query_generator.py) | DSL generation | Prompts include schema truncation (2000 chars) for token budget |
| [response_formatter.py](../../backend/services/response_formatter.py) | Result summarization | Requires JSON parsing; returns `{summary, metrics}` |
| [siem_connector.py](../../backend/services/siem_connector.py) | Elasticsearch client | Generic `_request()` method with auth delegation |
| [context_manager.py](../../backend/services/context_manager.py) | Session state | Simple dict; format is `{role: "user/assistant", content: "..."}` |
| [ChatInterface.jsx](../../frontend/src/components/ChatInterface.jsx) | Chat UI | Auto-scroll, loading state, renders markdown responses + metrics visualization |

## Common Modification Points

1. **Change LLM model:** Modify `model_id` in [llm_service.py](../../backend/services/llm_service.py)
2. **Adjust prompt structure:** Edit templates in [query_generator.py](../../backend/services/query_generator.py) or [response_formatter.py](../../backend/services/response_formatter.py)
3. **Add indices dynamically:** Extend [main.py](../../backend/main.py) chat endpoint to accept/infer index selection
4. **Persist sessions:** Replace in-memory dict in [context_manager.py](../../backend/services/context_manager.py) with database
5. **Add visualization types:** Extend [Visualizer.jsx](../../frontend/src/components/Visualizer.jsx) with new chart components (already uses Recharts)

## External Dependencies
- **Elasticsearch 8.12.0** - SIEM data source (supports both API key and user/password auth)
- **Hugging Face Inference API** - LLM provider (Qwen2.5-7B-Instruct)
- **FastAPI + Uvicorn** - Backend framework
- **React 19 + Vite** - Frontend framework
- **Recharts** - Data visualization

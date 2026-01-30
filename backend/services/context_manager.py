class ContextManager:
    def __init__(self):
        # In-memory storage: {session_id: [messages]}
        # message format: {"role": "user/assistant", "content": "..."}
        self.conversations = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str) -> list:
        return self.conversations.get(session_id, [])

    def get_history_string(self, session_id: str) -> str:
        history = self.get_history(session_id)
        return "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

    def clear_history(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]

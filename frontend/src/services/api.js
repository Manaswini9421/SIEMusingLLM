import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const sendMessage = async (sessionId, message, indexName) => {
    return api.post('/chat', { session_id: sessionId, message, index_name: indexName });
};

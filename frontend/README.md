# React + Vite

This front end is a chat UI for an AI agent that talks to a Python REST API.

## Chat API

- Base URL: `VITE_API_BASE_URL`
- Default: `http://localhost:8000`
- Endpoint: `POST /chat`
- Request body: `{ chatId, message, messages }`
- Expected response fields: `reply`, `message`, or `response`

Example request:

```json
{
  "chatId": "chat-123",
  "message": "Summarize the dataset",
  "messages": [
    { "role": "user", "content": "Summarize the dataset" }
  ]
}
```
# WebSocket Events Documentation

This document describes the WebSocket endpoints and events available in the application.

## Chat WebSocket Endpoint

**Endpoint Base URL:** `ws/chat/<room_name>/`

This endpoint allows clients to connect to a specific chat room to send and receive real-time messages.

### Authentication

This endpoint uses Django's standard **session-cookie authentication** — the same mechanism as every other API in the project. The browser must have a valid `sessionid` cookie (obtained by logging in via the REST API) before opening the WebSocket connection. `AuthMiddlewareStack` in `core/asgi.py` reads that cookie and populates `scope["user"]` automatically.

Unauthenticated WebSocket connections are briefly accepted so the server can send a clear application-specific close code. The connection is then immediately closed with code `4001`, which this project defines as `AUTHENTICATION_FAILED`.

### Connection
To connect to a chat room, establish a WebSocket connection to the endpoint with the desired `room_name`. A valid session cookie must be present in the request.
```
wss://localhost:8443/ws/chat/<room_name>/
```

### Sending Messages (Client to Server)

The server expects incoming messages to be in JSON format. The payload is validated using the `ChatMessageSerializer`.

**Payload Schema:**
```json
{
  "message": "Your text message here (max 500 characters)"
}
```

### Receiving Messages (Server to Client)

#### 1. Valid Message Broadcast
When a valid message is sent to the chat room, the server broadcasts it to all connected clients in the room (including the sender).

**Payload Schema:**
```json
{
  "message": "The text message",
  "sender_username": "Mr. Player",
  "timestamp": "2026-04-07T12:34:56.789Z"
}
```
`sender_username` is the `username` of the authenticated user who sent the message, read directly from `scope["user"]`.

#### 2. Invalid Message Error
If the client sends a payload that does not match the expected schema or exceeds the maximum length, the server responds with an error message to the sender.

**Payload Schema:**
```json
{
  "error": "Invalid message format.",
  "details": {
    "message": ["Ensure this field has no more than 500 characters."]
  }
}
```
## Game WebSocket Endpoint

**Endpoint Base URL:** `ws/game/<session_uuid>/`

This endpoint allows clients to connect to a specific game session to send actions and receive real-time game state updates (snapshots).

### Connection
To connect to a game session, establish a WebSocket connection to the endpoint with the desired `session_uuid`.
```
wss://localhost:8443/ws/game/<session_uuid>/
```

### Sending Actions (Client to Server)

The server expects incoming messages to be in JSON format containing an `action` string and a `payload` object.

**General Schema:**
```json
{
  "action": "action_name",
  "payload": {}
}
```

#### Available Actions:

**1. Start Game**
Starts the game session. Requires the session to be in the `LOBBY` state and at least 2 players to be connected. Available only for host of the session.
```json
{
  "action": "start_game",
  "payload": {}
}
```

**2. Submit Answer**
Submits an answer to the current question. Requires the session to be in the `ANSWERING` state and the sender to be the `current_player`.
```json
{
  "action": "submit_answer",
  "payload": {
    "answer": "Your answer text here" 
  }
}
```
*(Note: To simulate a timeout, send an empty string or omit the answer field).*

**3. Nominate Player**
Nominates the next player to answer. Requires the session to be in the `NOMINATION` state and the sender to be the `last_correct_player`.
```json
{
  "action": "nominate_player",
  "payload": {
    "target_player_id": 2
  }
}
```

### Receiving Messages (Server to Client)

#### 1. Game State Snapshot
Whenever the game state changes (e.g., player joins, turn changes, points are awarded), the server broadcasts a full snapshot of the current game state to all connected clients.

**Payload Schema (Example):**
```json
{
  "snapshot": {
    "session_uuid": "123e4567-e89b-12d3-a456-426614174000",
    "current_status": "ANSWERING",
    "current_player": 1,
    "last_correct_player": null,
    "last_nominated_player": null,
    "players": [
      { "id": 1, "display_name": "Player 1", "seat_number": 1, "lives": 3, "points": 0, "answered_count": 0, "is_alive": true }
    ],
    "current_question": {
      "id": 1,
      "question": { "question_text": "What is 5 + 5?", "category": "Math" },
      "order_index": 0
    },
    "answer_time_limit_ms": 20000,
    "winner": null,
    "end_reason": null,
    "question_asked_count": 1,
    "total_questions_count": 10
  }
}
```

#### 2. Error Message
If the client sends an invalid action, lacks permissions (e.g., trying to answer out of turn), or a game logic rule is violated, the server responds with an error message to the sender.

**Payload Schema:**
```json
{
  "type": "error",
  "error": "Only current player can submit answer"
}
```

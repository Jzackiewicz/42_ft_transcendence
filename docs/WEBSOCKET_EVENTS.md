# WebSocket Events Documentation

This document describes the WebSocket endpoints and events available in the application.

## Chat WebSocket

**Endpoint Base URL:** `ws/chat/<room_name>/`

This endpoint allows clients to connect to a specific chat room to send and receive real-time messages.

### Connection
To connect to a chat room, establish a WebSocket connection to the endpoint with the desired `room_name`.
```
ws://127.0.0.1:8000/ws/chat/<room_name>/
```
*Note: Authentication via JWT token is planned for the future.*

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
*Note: Current `sender_username` is a placeholder ("Mr. Player") and will be dynamically assigned from the authenticated user's JWT token in the future.*

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

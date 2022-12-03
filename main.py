from app import app, socketio

# WebSocket
import websocket.socketio

if __name__ == "__main__":
  socketio.run(app, port=5500, debug=True)
  # socketio.run(app, port=5500, debug=True, use_reloader=True)
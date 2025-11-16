"""
FastAPI Backend for Flappy Bird AI Challenge
Provides WebSocket for real-time game updates and hot-reload for ai_controller.py
"""

import asyncio
import importlib
import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import uvicorn

from game_engine import GameEngine
from levels import get_level, get_all_levels
import ai_controller

app = FastAPI()

# Global state
game_instances = {}
ai_module_reload_flag = False


class AIControllerReloadHandler(FileSystemEventHandler):
    """Watch for changes to ai_controller.py and trigger reload"""

    def on_modified(self, event):
        global ai_module_reload_flag
        if event.src_path.endswith("ai_controller.py"):
            print(f"🔄 Detected change in ai_controller.py - will reload on next frame")
            ai_module_reload_flag = True


def reload_ai_controller():
    """Reload the ai_controller module"""
    global ai_module_reload_flag
    if ai_module_reload_flag:
        try:
            importlib.reload(ai_controller)
            print("✅ ai_controller.py reloaded successfully")
            ai_module_reload_flag = False
            return True
        except Exception as e:
            print(f"❌ Error reloading ai_controller.py: {e}")
            ai_module_reload_flag = False
            return False
    return False


# Setup file watcher for hot-reload
def setup_file_watcher():
    """Setup watchdog to monitor ai_controller.py"""
    event_handler = AIControllerReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    print("👀 File watcher started - monitoring ai_controller.py for changes")
    return observer


@app.on_event("startup")
async def startup_event():
    """Start file watcher on app startup"""
    app.state.observer = setup_file_watcher()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop file watcher on app shutdown"""
    app.state.observer.stop()
    app.state.observer.join()


@app.get("/")
async def get_index():
    """Serve the main HTML page"""
    html_path = Path("static/index.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Error: static/index.html not found</h1>", status_code=404)


@app.get("/api/levels")
async def get_levels():
    """Get all available levels"""
    return get_all_levels()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for game communication"""
    await websocket.accept()

    # Create game instance for this connection
    game = GameEngine()
    client_id = id(websocket)
    game_instances[client_id] = game

    print(f"🎮 Client {client_id} connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "load_level":
                # Load a specific level
                level_id = data.get("level_id", "simple")
                level_config = get_level(level_id)
                game.load_level(level_config)
                await websocket.send_json({
                    "type": "level_loaded",
                    "level_id": level_id,
                    "state": game.get_render_state()
                })
                print(f"📦 Loaded level: {level_id}")

            elif action == "start_manual":
                # Start manual mode
                game.autopilot = False
                await websocket.send_json({
                    "type": "mode_changed",
                    "mode": "manual"
                })
                print("🎮 Started manual mode")

            elif action == "start_autopilot":
                # Start autopilot mode
                game.autopilot = True
                await websocket.send_json({
                    "type": "mode_changed",
                    "mode": "autopilot"
                })
                print("🤖 Started autopilot mode")

            elif action == "jump":
                # Manual jump command
                if not game.autopilot:
                    game.jump()

            elif action == "update":
                # Update game state for one frame
                should_jump = False

                # Check if ai_controller needs to be reloaded
                reload_ai_controller()

                if game.autopilot and not game.game_over:
                    # Get AI decision
                    try:
                        game_state = game.get_game_state()
                        should_jump = ai_controller.shouldJump(game_state)
                    except Exception as e:
                        print(f"❌ Error in shouldJump: {e}")
                        should_jump = False

                # Update game
                game.update(should_jump)

                # Send updated state
                await websocket.send_json({
                    "type": "state_update",
                    "state": game.get_render_state(),
                    "shouldJump": should_jump
                })

            elif action == "reset":
                # Reset game
                game.reset()
                await websocket.send_json({
                    "type": "reset",
                    "state": game.get_render_state()
                })
                print("🔄 Game reset")

    except WebSocketDisconnect:
        print(f"👋 Client {client_id} disconnected")
        del game_instances[client_id]
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        if client_id in game_instances:
            del game_instances[client_id]


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    print("🚀 Starting Flappy Bird AI Challenge Server")
    print("📍 Open http://localhost:3000 in your browser")
    print("📝 Edit ai_controller.py and save to see changes live!")
    print("=" * 60)

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3000,
        reload=False  # We handle reload ourselves for ai_controller.py
    )

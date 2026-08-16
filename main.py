import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from config import settings, sovereign_adapter
from db import init_db, seed_db
from agent import AntigravityPharmaAgent
from security import MultiTenantSecurityManager

app = FastAPI(title=settings.APP_NAME)

# Mount Static Assets
app.mount("/static", StaticFiles(directory="static"), name="static")

agent = AntigravityPharmaAgent()

@app.on_event("startup")
def startup_event():
    init_db()
    seed_db()

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "HEALTHY",
        "env": settings.ENV,
        "sovereign_routing": sovereign_adapter.get_routing_header()
    }

@app.websocket("/ws/agent-stream")
def agent_websocket(websocket: WebSocket):
    async def run():
        await websocket.accept()
        try:
            while True:
                raw_data = await websocket.receive_text()
                data = json.loads(raw_data)

                # Security Sanitization
                tenant_id = data.get("tenant_id", "tenant-alpha")
                api_material = MultiTenantSecurityManager.mask_pii(data.get("api_material", "Paracetamol Fine Powder GXP"))
                quantity_kg = float(data.get("quantity_kg", 5000))
                strategy = data.get("strategy", "balanced")
                custom_cap = float(data.get("concession_cap", 10.0))

                # Stream response
                async for chunk in agent.execute_agent_stream(tenant_id, api_material, quantity_kg, strategy, custom_cap):
                    await websocket.send_text(chunk)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))

    import asyncio
    asyncio.create_task(run())

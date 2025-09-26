from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import uvicorn
import os

app = FastAPI()

# ===== Models =====
class PairRequest(BaseModel):
    code: str

class AskRequest(BaseModel):
    query: str

class Item(BaseModel):
    name: str
    price: float
    qty: int

class CheckoutRequest(BaseModel):
    cart: List[Item]

# ===== API Endpoints =====
@app.post("/api/pair")
def pair_cart(req: PairRequest):
    if req.code.upper() == "SC1234":
        return {"success": True, "cartId": 1234, "battery": 94}
    return {"success": False, "error": "Invalid code"}

@app.post("/api/ask")
def ask_ai(req: AskRequest):
    return {"response": f"🤖 Suggestion: Try Store Brand to save 10% on {req.query}"}

@app.post("/api/checkout")
def checkout(req: CheckoutRequest):
    total = sum(item.price * item.qty for item in req.cart)
    return {"success": True, "message": "Payment successful", "total": total}

# ===== WebSocket =====
@app.websocket("/ws/cart/{cart_id}")
async def cart_ws(websocket: WebSocket, cart_id: int):
    await websocket.accept()
    await websocket.send_text(f"Connected to cart {cart_id}")
    await websocket.send_text("Head to Aisle 3 for Bread")
    await websocket.send_text("Proceed to Aisle 7 for Milk")
    await websocket.send_text("Checkout lane ready")
    await websocket.close()

# ===== Serve Frontend =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "AIBOTCART.html")

@app.get("/")
def serve_home():
    return FileResponse(HTML_FILE)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


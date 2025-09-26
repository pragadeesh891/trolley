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

# Add this inside your FastAPI app (main.py)

# ---- Brand Dictionaries ----
product_brands = {
    "milk": ["Amul", "Mother Dairy", "Nestlé", "Heritage", "Aavin"],
    "fruits": ["Apple (Shimla)", "Banana (Yelakki)", "Mango (Alphonso)"],
    "juice": ["Tropicana", "Real", "Minute Maid"],
    "maggi": ["Maggi 2-Minute", "Top Ramen", "Yippee"],
    "shampoo": ["Dove", "Pantene", "Head & Shoulders"],
    "ice cream": ["Amul", "Kwality Walls", "Baskin Robbins"],
    "snacks": ["Lays", "Kurkure", "Bingo"],
    "bakery": ["Britannia Bread", "Modern Bakery", "Local Fresh Cakes"],
    "skin and topical care": ["Nivea", "Vaseline", "Himalaya Herbal"]
}

product_aliases = {
    "milk": ["milk", "leche", "lait", "doodh"],
    "fruits": ["fruits", "frutas", "früchte", "phalon"],
    "juice": ["juice", "jugo", "jus", "raas"],
    "maggi": ["maggi", "noodles", "instant noodles"],
    "shampoo": ["shampoo", "champu", "haarshampoo"],
    "ice cream": ["ice cream", "helado", "glace"],
    "snacks": ["snacks", "bocadillos", "namkeen"],
    "bakery": ["bakery", "bread", "pastries"],
    "skin and topical care": ["skin care", "skincare", "topical care", "piel", "hautpflege", "twacha"],
}

def normalize_product(user_input: str) -> str | None:
    text = user_input.lower().strip()
    for key, synonyms in product_aliases.items():
        if text in [s.lower() for s in synonyms]:
            return key
    return None

# ---- API Endpoint ----
@app.post("/api/brands")
def get_brands(req: AskRequest):
    key = normalize_product(req.query)
    if key and key in product_brands:
        return {"success": True, "product": key, "brands": product_brands[key]}
    return {"success": False, "error": "Product not recognized"}

# ===== Serve Frontend =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "index.html")

@app.get("/")
def serve_home():
    return FileResponse(HTML_FILE)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)


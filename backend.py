from fastapi import FastAPI, Request, WebSocket, UploadFile, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
import uvicorn
import os, tempfile
from typing import List, Optional
import openai
from fastapi.staticfiles import StaticFiles



openai.api_key = os.environ.get("OPENAI_API_KEY")  # Securely

class AIRequest(BaseModel):
    query: str
    cart: List[str] = []


# ==== Setup ====
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==== Models ====
class PairRequest(BaseModel):
    code: str

class AskRequest(BaseModel):
    query: str

class Item(BaseModel):
    name: str
    price: float
    qty: int

class AIAssistRequest(BaseModel):
    query: str  # The user's question or prompt
    cart_items: Optional[List[str]] = []  # Optional: list of items currently in the cart
    session_id: Optional[str] = None 

class CheckoutRequest(BaseModel):
    cart: List[Item]
@app.post("/api/ai-assist")
async def ai_assist(req: AIRequest):
    """
    Uses OpenAI GPT to assist shopping.
    Considers items in user's cart to give context-aware guidance.
    """
    prompt = (
        f"You are a helpful shopping assistant. The user has the following items in their cart: {req.cart}.\n"
        f"Answer their query: {req.query}\n"
        f"Give step-by-step guidance or suggestions for shopping in a supermarket."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = response['choices'][0]['message']['content']
        return {"response": answer}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

# ==== Barcode → Product Mapping ====
barcode_products = {
    "8901001": "milk",
    "8901002": "fruits",
    "8901003": "juice",
    "8901004": "maggi",
    "8901005": "shampoo",
    "8901006": "ice cream",
    "8901007": "snacks",
    "8901008": "bakery",
    "8901009": "skin and topical care",
    "8902519012159": "Notepad",
}

product_brands = {
    "milk": ["Amul", "Mother Dairy", "Nestlé", "Heritage", "Aavin"],
    "fruits": ["Apple (Shimla)", "Banana (Yelakki)", "Mango (Alphonso)"],
    "juice": ["Tropicana", "Real", "Minute Maid"],
    "maggi": ["Maggi 2-Minute", "Top Ramen", "Yippee"],
    "shampoo": ["Dove", "Pantene", "Head & Shoulders"],
    "ice cream": ["Amul", "Kwality Walls", "Baskin Robbins"],
    "snacks": ["Lays", "Kurkure", "Bingo"],
    "bakery": ["Britannia Bread", "Modern Bakery", "Local Fresh Cakes"],
    "skin and topical care": ["Nivea", "Vaseline", "Himalaya Herbal"],
}

# ==== API Endpoints ====
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

@app.post("/api/barcode")
def scan_barcode(req: AskRequest):
    code = req.query.strip()
    if code in barcode_products:
        product = barcode_products[code]
        return {
            "success": True,
            "product": product,
            "brands": product_brands.get(product, [])
        }
    return {"success": False, "error": "Unknown barcode"}

# ==== WebSocket for Live Guidance ====
@app.websocket("/ws/cart/{cart_id}")
async def cart_ws(websocket: WebSocket, cart_id: int):
    await websocket.accept()
    await websocket.send_text(f"Connected to cart {cart_id}")
    await websocket.send_text("Head to Aisle 3 for Bread")
    await websocket.send_text("Proceed to Aisle 7 for Milk")
    await websocket.send_text("Checkout lane ready")
    await websocket.close()

# ==== Routes for Frontend ====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("AIBOTCART.html", {"request": request})

@app.get("/scan", response_class=HTMLResponse)
def scan(request: Request):
    return templates.TemplateResponse("scanner.html", {"request": request})

@app.get("/voice", response_class=HTMLResponse)
def voice_assistant_page(request: Request):
    return templates.TemplateResponse("voice.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

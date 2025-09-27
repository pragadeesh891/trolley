"""
Smart Trolley with voice feedback
Listen to voice commands and speak answers.
"""

import stripe
import speech_recognition as sr
import pyttsx3
from collections import deque

# ------------ Text-to-Speech ------------
tts = pyttsx3.init()
def speak(msg):
    """Speak and print a message."""
    print(msg)
    tts.say(msg)
    tts.runAndWait()

# ------------ Store Layout & Products ------------
rows, cols = 4, 3
products = {
    "milk": {"loc": (1, 1), "price": 50, "stock": 60, "barcode": "8901001"},
    "fruits": {"loc": (0, 1), "price": 60, "stock": 50, "barcode": "8901002"},
    "juice": {"loc": (0, 2), "price": 80, "stock": 30, "barcode": "8901003"},
    "maggi": {"loc": (1, 0), "price": 25, "stock": 40, "barcode": "8901004"},
    "shampoo": {"loc": (1, 2), "price": 120, "stock": 20, "barcode": "8901005"},
    "ice cream": {"loc": (2, 0), "price": 70, "stock": 25, "barcode": "8901006"},
    "snacks": {"loc": (2, 1), "price": 40, "stock": 80, "barcode": "8901007"},
    "bakery": {"loc": (2, 2), "price": 90, "stock": 30, "barcode": "8901008"},
    "skin and topical care": {"loc": (3, 1), "price": 150, "stock": 15, "barcode": "8901009"},
}

moves = [(0, 1, "right"), (0, -1, "left"), (1, 0, "down"), (-1, 0, "up")]

def bfs(start, goal):
    """Shortest path between grid cells."""
    queue = deque([(start, [])])
    visited = {start}
    while queue:
        (x, y), path = queue.popleft()
        if (x, y) == goal:
            return path
        for dx, dy, d in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                queue.append(((nx, ny), path + [d]))
                visited.add((nx, ny))
    return []

# ------------ Cart Management ------------
cart = []
total_amount = 0
current_position = (0, 0)  # entrance

def add_to_cart(product_name, quantity):
    global current_position, total_amount
    name = product_name.lower()
    if name not in products:
        speak("Product not found.")
        return
    if quantity > products[name]["stock"]:
        speak("Not enough stock.")
        return

    goal = products[name]["loc"]
    path = bfs(current_position, goal)
    current_position = goal

    products[name]["stock"] -= quantity
    price = products[name]["price"] * quantity
    total_amount += price
    cart.append((name, quantity, price))

    speak(f"Added {quantity} {name}. "
          f"Navigate {' → '.join(path)}. "
          f"Subtotal rupees {price}. "
          f"Current total rupees {total_amount}.")

# ------------ Input Modes ------------
def scan_barcode():
    code = input("Scan/enter barcode: ").strip()
    for name, data in products.items():
        if data["barcode"] == code:
            return name
    speak("Barcode not recognized.")
    return None

def voice_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say a product name.")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        speak(f"You said {text}")
        return text.lower()
    except Exception:
        speak("Sorry, I didn't catch that.")
        return None

# ------------ Payment ------------
def process_payment(amount_rupees):
    stripe.api_key = "sk_test_your_test_key_here"  # store securely!
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount_rupees * 100),
            currency="inr",
            payment_method_types=["card"],
        )
        speak("Payment initiated. Use the Stripe front-end to finish checkout.")
        print("Client secret:", intent.client_secret)
    except Exception as e:
        speak("Payment error.")
        print("Error:", e)

# ------------ Main Loop ------------
speak("Welcome to the Smart Trolley.")
while True:
    mode = input("\nMode: (b)arcode, (v)oice, (m)anual, (done): ").lower()
    if mode == "done":
        break
    if mode == "b":
        product = scan_barcode()
    elif mode == "v":
        product = voice_command()
    else:
        product = input("Product name: ").lower()

    if product:
        qty = input("Quantity: ")
        if qty.isdigit():
            add_to_cart(product, int(qty))

speak("Here is your bill.")
print("\n------ BILL ------")
for item, q, amt in cart:
    line = f"{item.title():20s} {q} pcs  ₹{amt}"
    print(line)
    speak(line)
print(f"TOTAL: ₹{total_amount}")
speak(f"Total is rupees {total_amount}")

if input("Proceed to payment? (y/n): ").lower() == "y":
    process_payment(total_amount)
    speak("Payment process started. Thank you for shopping!")
else:
    speak("Payment cancelled. Thank you for shopping!")



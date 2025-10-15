# Friend Access Guide - Smart Shopping Trolley

## For You (Host):

### Step 1: Ensure Server is Running
Make sure the Smart Shopping Trolley application is running:
- Open a command prompt in the project folder
- Run: `uvicorn main:app --host 0.0.0.0 --port 8000`
- Keep this window open

### Step 2: Create Public Tunnel
To allow your friend to access it from anywhere:

1. Double-click on `create_tunnel.bat` file
2. When prompted, press any key to start
3. You may see a security message - type "yes" and press Enter
4. You'll get a unique URL like: `https://abc123.serveo.net`
5. Share this URL with your friend

## For Your Friend (User):

### Step 1: Access the Application
1. Open any web browser (Chrome, Firefox, Safari, etc.)
2. Enter the URL provided by your friend
3. The Smart Shopping Trolley interface should load

### Step 2: Use the Application
The application works the same way as if it were running locally:
- Scan QR codes to add products to cart
- Use voice commands for assistance
- Navigate the store with the guidance system
- Make payments using UPI or Card options

## Features Available:
- ✅ Multilingual support (10 Indian languages + English)
- ✅ Voice-controlled shopping assistant
- ✅ QR code scanning for products
- ✅ Real-time cart management
- ✅ Store navigation system
- ✅ Multiple payment options (UPI, Card)
- ✅ Email receipt generation

## Troubleshooting:

### If the URL doesn't work:
1. Ask your friend to restart the tunnel
2. Make sure their computer hasn't gone to sleep
3. Check that their firewall isn't blocking the connection

### If features aren't working:
1. Ensure your friend is using a modern browser
2. Refresh the page if anything seems stuck
3. For voice features, ensure microphone permissions are granted

## Important Notes:
- The application is only accessible while your computer is on and the server is running
- No signup or payment is required for either of you
- The tunnel URL changes each time you create a new tunnel
- For best performance, both you and your friend should have good internet connections
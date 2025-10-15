"""
Test script to verify email functionality
"""

from main import send_receipt_email

# Test data
test_cart = [
    {"name": "Apple iPhone 15", "price": 799.99, "qty": 1},
    {"name": "Samsung Galaxy S24", "price": 699.99, "qty": 1}
]

test_total = sum(item["price"] * item["qty"] for item in test_cart)

# Test sending email
print("Testing email functionality...")
print("Enter an email address to send a test receipt:")
email = input("> ")

if email:
    print(f"Sending test receipt to {email}...")
    success = send_receipt_email(email, test_cart, test_total, "Test Payment")
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")
else:
    print("No email provided. Skipping test.")
"""
Email configuration for Smart Shopping Trolley
Store your email credentials here (but don't commit to version control!)

To enable real email sending:
1. Follow the instructions in EMAIL_SETUP.md
2. Replace the placeholder values below with your actual credentials
"""

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your_email@gmail.com",  # Replace with your Gmail address
    "sender_password": "your_app_password"   # Replace with your Gmail app password
}

# For testing purposes, you can use these dummy credentials
# In production, replace with actual Gmail credentials

# To set up real email sending:
# 1. Read EMAIL_SETUP.md for detailed instructions
# 2. Enable 2-factor authentication on your Google account
# 3. Generate an App Password
# 4. Replace the placeholder values above
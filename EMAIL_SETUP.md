# Email Setup Guide

To enable real email sending for receipts, you need to configure your Gmail account with an App Password.

## Step 1: Enable 2-Factor Authentication

1. Go to your Google Account settings: https://myaccount.google.com/
2. Click on "Security" in the left sidebar
3. Under "Signing in to Google," click on "2-Step Verification"
4. Follow the steps to set up 2-factor authentication

## Step 2: Generate an App Password

1. Stay in the "Security" section of your Google Account
2. Scroll down to "Signing in to Google" and click on "App passwords"
3. If prompted, enter your password
4. Under "Select app," choose "Mail"
5. Under "Select device," choose "Other" and type "SmartCart"
6. Click "Generate"
7. Copy the 16-character password (without spaces)

## Step 3: Configure the Application

1. Open the `email_config.py` file in your project
2. Replace `"your_email@gmail.com"` with your actual Gmail address
3. Replace `"your_app_password"` with the 16-character app password you generated
4. Save the file

Example:
```python
# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "youremail@gmail.com",  # Your actual Gmail address
    "sender_password": "abcd efgh ijkl mnop"  # Your app password (without spaces)
}
```

## Step 4: Test the Configuration

1. Restart your server
2. Make a test purchase and enter an email address
3. Check if the receipt is sent to that email

## Alternative Email Providers

If you prefer not to use Gmail, you can configure other email providers:

### Outlook/Hotmail:
```python
EMAIL_CONFIG = {
    "smtp_server": "smtp-mail.outlook.com",
    "smtp_port": 587,
    "sender_email": "your_email@outlook.com",
    "sender_password": "your_password"
}
```

### Yahoo:
```python
EMAIL_CONFIG = {
    "smtp_server": "smtp.mail.yahoo.com",
    "smtp_port": 587,
    "sender_email": "your_email@yahoo.com",
    "sender_password": "your_app_password"
}
```

## Troubleshooting

### If emails aren't sending:
1. Check that you've enabled 2-factor authentication
2. Verify that you're using an App Password, not your regular password
3. Ensure the App Password is entered correctly (without spaces)
4. Check that your Gmail account isn't blocked for security reasons

### If you get SSL/TLS errors:
1. Make sure your system time is correct
2. Try using a different network connection
3. Check if your firewall is blocking outgoing connections on port 587

### If you get authentication errors:
1. Double-check your email address and App Password
2. Generate a new App Password and try again
3. Make sure you're not using your regular Gmail password

## Security Notes

- Never commit your email_config.py file to version control if it contains real credentials
- App Passwords are more secure than regular passwords as they can be revoked individually
- The App Password only works for the specific app you created it for
- If you suspect your App Password has been compromised, revoke it and generate a new one
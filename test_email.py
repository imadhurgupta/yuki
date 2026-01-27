import smtplib
from email.mime.text import MIMEText

# --- CONFIGURATION (Match what is in your app.py) ---
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'madhurguptaofficial@gmail.com'  # <--- REPLACE THIS
APP_PASSWORD = 'zydu tzxg damh gksi'         # <--- REPLACE THIS (16-digit App Password)
RECIPIENT_EMAIL = 'madhurguptaofficial@gmail.com' # Send to yourself to test

def send_test_email():
    try:
        print("1. Connecting to Gmail Server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        
        print("2. Logging in...")
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        print("3. Sending Email...")
        msg = MIMEText("If you see this, your App Password works!")
        msg['Subject'] = "Test Email from Python"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(">> SUCCESS! Email sent. Your config is correct.")
        
    except Exception as e:
        print("\n>> FAILED. Here is the exact error:")
        print(e)
        print("\n------------------------------------------------")
        print("COMMON FIXES:")
        print("1. If error says 'Username and Password not accepted':")
        print("   - You are likely using your Login Password.")
        print("   - You MUST use an 'App Password' (16 digits).")
        print("2. If error says 'Please log in via your web browser':")
        print("   - Go to https://accounts.google.com/DisplayUnlockCaptcha and click Continue.")

if __name__ == "__main__":
    send_test_email()
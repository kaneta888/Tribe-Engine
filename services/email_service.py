"""
Email service for sending password reset emails.
For MVP: Prints to console
For Production: Use SendGrid or SMTP
"""

def send_password_reset_email(user_email, reset_url):
    """
    Send password reset email to user.
    In MVP mode, prints to console instead of sending actual email.
    """
    print("\n" + "="*60)
    print("📧 PASSWORD RESET EMAIL")
    print("="*60)
    print(f"To: {user_email}")
    print(f"Subject: パスワードリセットのご案内")
    print("\n以下のリンクをクリックしてパスワードをリセットしてください：")
    print(f"\n{reset_url}")
    print("\nこのリンクは1時間有効です。")
    print("="*60 + "\n")
    
    # For production, use SendGrid:
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    # ...

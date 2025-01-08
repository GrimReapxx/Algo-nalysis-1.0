import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    # Outlook SMTP configuration
    smtp_server = 'smtp.office365.com'
    smtp_port = 587
    from_email = 'ericinnocent04@outlook.com'
    password = 'Monc.Ashborn04'  # Use an app password if 2FA is enabled

    # Create the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Upgrade to a secure connection
            server.login(from_email, password)  # Log in to the server
            server.send_message(msg)  # Send the email
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage
send_email("Test Subject", "This is a test email body.", "jayy.shoreoff@gmail.com")
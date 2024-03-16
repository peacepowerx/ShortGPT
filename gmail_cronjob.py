import imaplib
import email
import time
import os
from email.header import decode_header

# Environment variables for Gmail credentials
os.environ['GMAIL_USER'] = 'yourgmail@gmail.com'
os.environ['GMAIL_PASSWORD'] = 'yourapppassword'

def check_email():
    user = os.environ.get('GMAIL_USER')
    password = os.environ.get('GMAIL_PASSWORD')
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993

    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(user, password)
    mail.select('inbox')

    # Search for specific emails
    status, messages = mail.search(None, '(FROM "pixie@example.com" SUBJECT "Start Video")')
    # messages is a list of email IDs
    for msg_num in messages[0].split():
        # Fetch each email's details
        _, msg_data = mail.fetch(msg_num, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the message
                msg = email.message_from_bytes(response_part[1])
                # Decode email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)
                # Extract sender's email address
                from_ = msg.get("From")
                print("Got an email from:", from_)
                print("Subject:", subject)
                
                # Check if email has the trigger for video processing
                if subject == "Start Video":
                    # Call your email_video API here
                    call_email_video_api(from_)

def call_email_video_api(email_address):
    # Insert the logic to call your `email_video` API using the email address
    # ...
    pass

if __name__ == '__main__':
    while True:
        check_email()
        time.sleep(60 * 5)  # Check every 5 minutes

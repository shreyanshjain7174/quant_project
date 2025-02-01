import imaplib
import email
import os
from email import policy
from email.parser import BytesParser
from config.settings import EMAIL_HOST, EMAIL_USER, EMAIL_PASS, EMAIL_FOLDER
import logging

def fetch_emails():
    """Fetch .eml attachments from email inbox and save them to disk."""
    if not EMAIL_USER or not EMAIL_PASS:
        logging.info("⚠️ Email credentials are not provided. Skipping email fetching.")
        return
    
    # Ensure the save path exists
    os.makedirs(EMAIL_FOLDER, exist_ok=True)

    # Connect to email server
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select(EMAIL_FOLDER)

    # Search for unread emails with attachments
    result, data = mail.search(None, "UNSEEN")
    email_ids = data[0].split()

    for email_id in email_ids:
        # Fetch email
        result, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        # Parse email
        msg = email.message_from_bytes(raw_email, policy=policy.default)
        
        # Extract attachments
        for part in msg.walk():
            if part.get_content_type() in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text/csv"]:
                filename = part.get_filename()
                if filename and filename.startswith("TradeFile"):
                    filepath = os.path.join(EMAIL_FOLDER, filename)
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))
                    logging.info(f"✅ Saved: {filepath}")

    mail.logout()

if __name__ == "__main__":
    fetch_emails()

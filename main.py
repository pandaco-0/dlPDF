import imaplib
import email
import os

# Email credentials and IMAP server details
EMAIL = '@gmail.com'
PASSWORD = 'your_password'
IMAP_SERVER = 'imap.gmail.com'  # or another email provider
IMAP_PORT = 993

# Directory where PDFs will be saved (Windows-friendly paths)
SAVE_DIR = r'attachments\\'

# Connect to the email server and login
def connect_to_email():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    return mail

# Refactored: Main function to download PDF attachments
def download_pdf_attachments(mail):
    mail.select('inbox')  # Select the mailbox you want to scan
    email_ids = get_email_ids(mail)
    if not email_ids:
        print("No emails found.")
        return

    for email_id in email_ids:
        process_email(mail, email_id)

# Refactored: Get all email IDs from the inbox
def get_email_ids(mail):
    status, data = mail.search(None, 'ALL')
    if status != 'OK':
        print("Error fetching emails.")
        return None
    return data[0].split()

# Refactored: Process each email by fetching and handling its attachments
def process_email(mail, email_id):
    status, msg_data = mail.fetch(email_id, '(RFC822)')
    if status != 'OK':
        print(f"Error fetching email ID {email_id}.")
        return
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            handle_email(msg)

# Refactored: Handle the email by checking its subject and downloading attachments
def handle_email(msg):
    subject = get_email_subject(msg)
    print(f"Processing email: {subject}")
    
    if msg.is_multipart():
        for part in msg.walk():
            handle_part(part)

# Refactored: Get and decode the email subject
def get_email_subject(msg):
    subject, encoding = email.header.decode_header(msg['subject'])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or 'utf-8')
    return subject

# Refactored: Handle each part of the email to check for and download PDF attachments
def handle_part(part):
    if is_attachment(part) and is_pdf(part):
        download_attachment(part)

# Refactored: Check if the part is an attachment
def is_attachment(part):
    return part.get_content_disposition() == 'attachment'

# Refactored: Check if the attachment is a PDF file
def is_pdf(part):
    filename = part.get_filename()
    return filename and filename.endswith('.pdf')

# Refactored: Download the attachment
def download_attachment(part):
    filename = part.get_filename()
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    filepath = os.path.join(SAVE_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(part.get_payload(decode=True))
    print(f"Downloaded: {filename}")

# Main function
def main():
    mail = connect_to_email()
    download_pdf_attachments(mail)
    mail.logout()

if __name__ == '__main__':
    main()
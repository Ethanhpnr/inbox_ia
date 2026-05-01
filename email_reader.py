import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def clean_text(text):
    if isinstance(text, bytes):
        return text.decode("utf-8", errors="ignore")
    return text

def read_emails():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    mail_ids = messages[0].split()

    print(f"📨 {len(mail_ids)} emails trouvés\n")

    for i in mail_ids[-5:]:  # derniers 5 mails
        status, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(msg["subject"])[0]
        subject = clean_text(subject)

        from_ = clean_text(msg.get("From"))

        print("📩 Sujet :", subject)
        print("👤 De :", from_)

        # contenu
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True)
                    print("📝 Contenu :", clean_text(body)[:200])
                    break
        else:
            body = msg.get_payload(decode=True)
            print("📝 Contenu :", clean_text(body)[:200])

        print("-" * 50)

    mail.logout()

if __name__ == "__main__":
    read_emails()
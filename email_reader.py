import imaplib
import email
from email.header import decode_header
from ai_processor import analyze_email
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")


def clean_text(text):
    if isinstance(text, bytes):
        return text.decode("utf-8", errors="ignore")
    return text


def decode_mime_words(s):
    if not s:
        return ""
    decoded = decode_header(s)
    result = ""
    for part, encoding in decoded:
        if isinstance(part, bytes):
            result += part.decode(encoding or "utf-8", errors="ignore")
        else:
            result += part
    return result


def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def get_email_body(msg):
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" in content_disposition:
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            payload = clean_text(payload)

            if content_type == "text/plain":
                return payload

            if content_type == "text/html" and not body:
                body = extract_text_from_html(payload)

    else:
        payload = msg.get_payload(decode=True)
        if payload:
            body = clean_text(payload)

    return body


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

        subject = decode_mime_words(msg.get("Subject"))
        from_ = decode_mime_words(msg.get("From"))

        body = get_email_body(msg)

        print("📩 Sujet :", subject)
        print("👤 De :", from_)
        print("📝 Body :", body[:300], "...\n")

        # 🔥 Appel IA (si ton module existe)
        try:
            analysis = analyze_email(subject, from_, body)
            print("🤖 Analyse IA :", analysis, "\n")
        except Exception as e:
            print("⚠️ Erreur IA :", e, "\n")

    mail.logout()


if __name__ == "__main__":
    read_emails()
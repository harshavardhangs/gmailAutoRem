import os
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google import genai
from twilio.rest import Client

# Load environment variables from .env
load_dotenv()

# Configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")


def get_gmail_service():
    """Authenticates the user and returns an authorized Gmail API service instance."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_unread_emails(service, max_results=10):
    """Fetches unread emails from the inbox with basic subject/sender/snippet extraction."""
    results = (
        service.users()
        .messages()
        .list(userId="me", q="is:unread label:INBOX", maxResults=max_results)
        .execute()
    )
    messages = results.get("messages", [])

    if not messages:
        return []

    email_data = []
    for msg_meta in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_meta["id"], format="full")
            .execute()
        )
        headers = msg.get("payload", {}).get("headers", [])

        subject = next(
            (h["value"] for h in headers if h["name"].lower() == "subject"),
            "No Subject",
        )
        sender = next(
            (h["value"] for h in headers if h["name"].lower() == "from"),
            "Unknown Sender",
        )
        snippet = msg.get("snippet", "")

        email_data.append(
            {"from": sender, "subject": subject, "snippet": snippet}
        )

    return email_data


def summarize_with_gemini(emails):
    """Uses Gemini to summarize the retrieved emails for WhatsApp."""
    if not emails:
        return "No unread emails found in your inbox."

    email_text_dump = ""
    for idx, e in enumerate(emails, 1):
        email_text_dump += (
            f"\nEmail {idx}:\nFrom: {e['from']}\nSubject: {e['subject']}\nPreview: {e['snippet']}\n"
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are an executive assistant preparing a concise WhatsApp brief. 
Summarize the following unread emails into key bullet points.

Requirements:
- Start with a quick one-line count/summary.
- Use bold markers for key highlights and deadlines.
- Keep the language punchy and suitable for mobile chat.
- Total length must be under 1200 characters.

Emails:
{email_text_dump}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text.strip()


def send_whatsapp_message(body_text):
    """Sends the summary text directly to WhatsApp using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=body_text,
        to=MY_WHATSAPP_NUMBER,
    )
    print(f"Message sent successfully to WhatsApp! SID: {message.sid}")


def run():
    print("1. Connecting to Gmail...")
    service = get_gmail_service()

    print("2. Fetching unread emails...")
    emails = fetch_unread_emails(service, max_results=10)

    if not emails:
        print("No unread emails found. Skipping message.")
        return

    print(f"3. Summarizing {len(emails)} emails with Gemini...")
    summary = summarize_with_gemini(emails)

    print("4. Sending summary via Twilio WhatsApp...")
    send_whatsapp_message(summary)


if __name__ == "__main__":
    run()
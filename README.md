# 📬 Gmail Auto-Digest via WhatsApp

An automated serverless pipeline that checks unread Gmail inbox messages, creates an executive brief using Google's Gemini AI, and delivers the summary directly to WhatsApp every 2 hours via Twilio.

---

## ⚡ Features

- **Automated Polling:** Scheduled GitHub Actions runner executes every 2 hours without needing a dedicated 24/7 server.
- **AI-Powered Summarization:** Uses Gemini Flash (`google-genai` SDK) to filter out newsletter fluff, surface action items, and create readable bullet points under 1,200 characters.
- **WhatsApp Integration:** Instant mobile delivery through the Twilio WhatsApp Sandbox API.
- **Zero Ongoing Cost:** Operates 100% within the free tiers of GitHub Actions, Google AI Studio, and Twilio.
- **Keepalive Safeguard:** Includes an automated scheduled commit on the 1st and 15th of every month to bypass GitHub's 60-day scheduled workflow inactivity pause.

---

## 🏗️ Architecture
[ Gmail Inbox ]
│
▼ (Gmail API / OAuth 2.0)
[ GitHub Actions Runner (Cron: '15 */2 * * *') ]
│
▼ (google-genai SDK)
[ Gemini Model Summarization ]
│
▼ (Twilio REST API)
[ WhatsApp Delivery ]

---

## 🔐 Required Secrets (Repository Settings)

To run this pipeline, configure the following repository secrets under **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Description |
| :--- | :--- |
| `GEMINI_API_KEY` | API Key generated via [Google AI Studio](https://aistudio.google.com/) |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID found in the Twilio Console dashboard |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token from the Twilio Console dashboard |
| `TWILIO_WHATSAPP_NUMBER` | Twilio Sandbox Number (e.g., `whatsapp:+14155238886`) |
| `MY_WHATSAPP_NUMBER` | Your personal registered number (e.g., `whatsapp:+91XXXXXXXXXX`) |
| `GMAIL_TOKEN_JSON` | Full JSON string from your authenticated local `token.json` |

---

## 🛠️ Local Setup & Token Generation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/gmailAutoRem.git

2. **Install dependencies:**
```bash
pip install google-genai google-api-python-client google-auth-oauthlib google-auth-httplib2 twilio python-dotenv

```


3. **Configure Google Cloud Console:**
* Enable the **Gmail API** under your Google Cloud project.
* Configure the **OAuth Consent Screen** (User type: *External*, add your email under *Test Users*).
* Create an **OAuth 2.0 Client ID** (Desktop Application) and download it as `credentials.json` into the root directory.


4. **Generate `token.json` locally:**
```bash
python email_digest.py

```


*Authorize the app in your browser window when prompted. Once complete, copy the contents of the generated `token.json` into the `GMAIL_TOKEN_JSON` GitHub secret.*

---

## ⚙️ Repository Permissions

To allow the workflow to commit the keepalive heartbeat:

1. Navigate to **Settings** → **Actions** → **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions** and click **Save**.

---

## 📄 License

MIT License

```

```
   cd gmailAutoRem


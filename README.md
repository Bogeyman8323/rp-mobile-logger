# Workout Logger — Google Drive (Mobile)

Mobile-friendly Streamlit app that:
- Signs in with Google (Authorization Code flow)
- Lets the user pick an Excel file from Google Drive (Google Picker)
- Guides sets/reps recommendations and logs weight/reps into a `Logs` sheet
- Saves back to the same file in Drive

## Google Cloud Setup
1. Enable **Google Drive API** and **Google Picker API** in the same project.
2. Create **OAuth 2.0 Client** (Web application). Add your Streamlit URL as **Authorized redirect URI**.
3. Create an **API key**. Restrict it to **HTTP referrers** (your Streamlit domain) and to **Google Picker API**.
4. Note your **Project Number** (App ID for Picker).

## Streamlit Secrets
Paste values in Streamlit Cloud → App → Settings → Secrets:

```toml
[google]
client_id     = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"
redirect_uri  = "https://your-app.streamlit.app"
scopes        = ["https://www.googleapis.com/auth/drive.file"]
api_key       = "YOUR_RESTRICTED_API_KEY"
app_id        = "YOUR_PROJECT_NUMBER"
```

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
# create .streamlit/secrets.toml from example
streamlit run app.py
```

## Deploy (Streamlit Cloud)
- Set **Main file path** = `app.py`.
- Add Secrets.

## Troubleshooting
- 403 `access_denied` before consent → Publish OAuth app or add yourself as **Test user**; check redirect URI.
- Picker init issues → ensure API key restricted to your domain + Picker API, App ID = Project Number, all in same project.
- Drive 404 on file after picking → with `drive.file` scope, you only have access to files you **explicitly pick** (or create).

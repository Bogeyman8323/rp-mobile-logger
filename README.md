
# PR: Google Picker + `drive.file` Integration

This PR switches the mobile app to least‑privilege Google Drive access using the **Google Picker** and the **`drive.file`** scope.

## What changed
- Added **picker_component/** (a tiny web component) that opens the official Google Picker.
- Updated **streamlit_mobile_app_gdrive.py** to:
  - Request `drive.file` scope.
  - Pass OAuth access token to Picker via `setOAuthToken` and receive selected `fileId`.
  - Download and update the selected file with Drive v3.
- Updated **.streamlit/secrets.example.toml** to include `api_key` and `app_id` (Project Number).
- Ensured **requirements.txt** contains Google client libraries.

## Cloud setup
1. Enable **Google Drive API** and **Google Picker API** in Google Cloud Console.
2. Create **OAuth client (Web application)** with redirect URI = your Streamlit URL.
3. Create **API key** and **restrict** it (HTTP referrers to your Streamlit URL; API restriction = Google Picker API).
4. Put values in Streamlit **Secrets**.

## After deploy
- Sign in → Click **Open Google Drive Picker** → choose your tracker `.xlsx` → *Open from Drive* → log sets → *Save back to Drive*.

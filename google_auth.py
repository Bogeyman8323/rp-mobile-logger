# google_auth.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CREDS_KEY = "_g_creds"

def _client_config():
    g = st.secrets["google"]
    return {
        "web": {
            "client_id": g["client_id"],
            "client_secret": g["client_secret"],
            "redirect_uris": [g["redirect_uri"]],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

def build_auth_url():
    g = st.secrets["google"]
    flow = Flow.from_client_config(_client_config(), scopes=list(g["scopes"]))
    flow.redirect_uri = g["redirect_uri"]
    url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return url

def exchange_code_for_token():
    params = getattr(st, "query_params", None)
    params = params.to_dict() if params else st.experimental_get_query_params()
    code = params.get("code")
    if isinstance(code, list): code = code[0]
    if not code: return None

    g = st.secrets["google"]
    flow = Flow.from_client_config(_client_config(), scopes=list(g["scopes"]))
    flow.redirect_uri = g["redirect_uri"]
    flow.fetch_token(code=code)
    creds = flow.credentials
    st.session_state[CREDS_KEY] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }
    try: st.query_params.clear()
    except Exception: st.experimental_set_query_params()
    return creds

def get_creds():
    data = st.session_state.get(CREDS_KEY)
    if not data: return None
    creds = Credentials(**data)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        st.session_state[CREDS_KEY]["token"] = creds.token
    return creds

def sign_out():
    st.session_state.pop(CREDS_KEY, None)

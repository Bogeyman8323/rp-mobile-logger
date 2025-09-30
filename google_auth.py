# google_auth.py
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

CREDS_KEY = "_g_creds"
STATE_KEY = "_g_state"

def _client_config():
    conf = st.secrets["google"]
    # Streamlit secrets should contain client_id, client_secret, redirect_uri
    return {
        "web": {
            "client_id": conf["client_id"],
            "client_secret": conf["client_secret"],
            "redirect_uris": [conf["redirect_uri"]],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

def build_auth_url():
    """Return a URL the user clicks to start Google sign-in (Authorization Code flow)."""
    conf = st.secrets["google"]
    flow = Flow.from_client_config(_client_config(), scopes=list(conf["scopes"]))
    flow.redirect_uri = conf["redirect_uri"]
    # offline access => refresh token; include_granted_scopes merges prior consent
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"  # force consent so we reliably get refresh_token in multi-tenant cases
    )
    st.session_state[STATE_KEY] = state
    return auth_url

def exchange_code_for_token():
    """If a ?code= is present in the URL, exchange it for tokens and stash in session."""
    # Streamlit introduced st.query_params; keep fallback for older versions
    params = getattr(st, "query_params", None)
    if params is None:
        params = st.experimental_get_query_params()
    else:
        params = params.to_dict()

    code = params.get("code")
    if isinstance(code, list):
        code = code[0]
    if not code:
        return None

    conf = st.secrets["google"]
    flow = Flow.from_client_config(_client_config(), scopes=list(conf["scopes"]))
    flow.redirect_uri = conf["redirect_uri"]
    flow.fetch_token(code=code)

    creds = flow.credentials
    # Persist the minimal fields we need to rebuild Credentials later
    st.session_state[CREDS_KEY] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes or []),
    }
    return creds

def get_creds():
    """Return a valid, refreshed google.oauth2.credentials.Credentials or None."""
    data = st.session_state.get(CREDS_KEY)
    if not data:
        return None
    creds = Credentials(**data)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # keep the latest access token in session
        st.session_state[CREDS_KEY]["token"] = creds.token
    return creds

def sign_out():
    """Clear cached credentials."""
    st.session_state.pop(CREDS_KEY, None)
    st.session_state.pop(STATE_KEY, None)

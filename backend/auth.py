import streamlit as st
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_flow():
    return Flow.from_client_config(
        st.secrets["google"],
        scopes=SCOPES,
        redirect_uri=st.secrets["google"]["web"]["redirect_uris"][0],
    )

def get_auth_url():
    flow = get_flow()
    auth_url, state = flow.authorization_url(prompt="consent")
    st.session_state["state"] = state
    return auth_url

def fetch_token(code):
    flow = get_flow()
    flow.fetch_token(code=code)
    return flow.credentials
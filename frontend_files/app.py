
import os
import streamlit as st
import requests

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

# Docker deployment: BACKEND_URL=http://aurorastay-backend:7860
# Local development fallback
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:7860"
).rstrip("/")

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AuroraStay Hotels | Policy Assistant",
    page_icon="🏨",
    layout="wide"
)

# ---------------------------------------------------------
# Sidebar - Model parameters
# ---------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Parameters")

    k = st.slider(
        "k (chunks to retrieve)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of relevant policy chunks retrieved."
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1
    )

    max_tokens = st.slider(
        "Max tokens",
        min_value=64,
        max_value=2048,
        value=512,
        step=64
    )

# ---------------------------------------------------------
# Main area
# ---------------------------------------------------------

st.title("🏨 AuroraStay Hotels")
st.write(
    "AI-powered assistant for hotel staff to answer guest "
    "questions using official property and policy documents."
)
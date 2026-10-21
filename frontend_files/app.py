
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
# ---------------------------------------------------------
# Staff guidance
# ---------------------------------------------------------

st.info(
    "Answers are based on available hotel policy documents. "
    "Verify the live property profile before confirming "
    "property-specific fees, availability, or restrictions."
)

# ---------------------------------------------------------
# Response selection
# ---------------------------------------------------------

response_type = st.radio(
    "Response mode",
    ["Answer only", "Answer + Relevant Chunks"],
    horizontal=True
)

# ---------------------------------------------------------
# Question input
# ---------------------------------------------------------

query = st.text_input(
    "Your question",
    placeholder="e.g., What is the pet fee at ASH-CHI Loop?"
)

# ---------------------------------------------------------
# Submit
# ---------------------------------------------------------

if st.button("Submit", type="primary"):

    if not query.strip():
        st.warning("Please enter a question.")

    else:
        endpoint = (
            "/v1/answer"
            if response_type == "Answer only"
            else "/v1/answer_with_relevant_chunks"
        )

        payload = {
            "query": query,
            "k": k,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            with st.spinner("Searching hotel policies..."):
                response = requests.post(
                    f"{BACKEND_URL}{endpoint}",
                    json=payload,
                    timeout=180
                )

            response.raise_for_status()
            result = response.json()

            st.subheader("Answer")
            st.write(
                result.get("answer", "No answer was returned.")
            )

            if response_type == "Answer + Relevant Chunks":
                st.subheader("Supporting Policy Information")

                chunks = result.get("relevant_chunks", [])

                if chunks:
                    for i, chunk in enumerate(chunks, start=1):
                        with st.expander(f"Retrieved Policy Chunk {i}"):
                            st.text(chunk)
                else:
                    st.warning("No supporting policy chunks returned.")

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")

        except requests.exceptions.ConnectionError:
            st.error(
                "Unable to connect to the Flask backend. "
                "Please check that the backend service is running."
            )

        except requests.exceptions.RequestException as e:
            st.error(
                f"The backend request failed: {type(e).__name__}"
            )
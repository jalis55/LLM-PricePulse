# streamlit_app.py
import streamlit as st
import pandas as pd

from app import generate_sql, fetch_data

st.set_page_config(page_title="PricePulse", layout="centered")
st.title("PricePulse 📈")
st.subheader("Instruments Price History")


# --- Input ---
prompt = st.text_area("Enter your prompt:", placeholder="e.g. Show me last 7 days closing price of aci")

# --- (Mock) Processing ---
@st.cache_data(show_spinner=False)
def mock_df_from_prompt(p: str) -> pd.DataFrame:
    """
    Replace this function with whatever logic turns your prompt
    into a real DataFrame (LLM call, SQL query, API, etc.).
    For the demo we just return a tiny static table.
    """
    query = generate_sql(p)
    return fetch_data(query)

# --- Output ---
if st.button("Run", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    with st.spinner("Generating ……"):
        result = mock_df_from_prompt(prompt)

    if isinstance(result, str):
        st.warning(result)
    else:
        st.success("Done!")
        st.dataframe(result, use_container_width=True)   # interactive table

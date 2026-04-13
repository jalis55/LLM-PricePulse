# streamlit_app.py
import streamlit as st
import pandas as pd

from app import generate_sql, fetch_data

st.set_page_config(page_title="PricePulse", layout="centered")
st.title("PricePulse 📈")
st.subheader("Instruments Price History")


# --- Input ---
prompt = st.text_area("Enter your prompt:", placeholder="e.g. Show me last 7 days closing price of aci")

# --- Processing ---
def run_prompt(p: str) -> pd.DataFrame:
    query = generate_sql(p)
    return fetch_data(query)

# --- Output ---
if st.button("Run", type="primary"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    with st.spinner("Generating ……"):
        result = run_prompt(prompt)

    if isinstance(result, str):
        st.warning(result)
    else:
        st.success("Done!")
        st.dataframe(result, use_container_width=True)   # interactive table

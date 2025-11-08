import streamlit as st, pandas as pd
from sqlalchemy import create_engine, text
import os

st.set_page_config(page_title="Footy Predictor", layout="wide")
st.title("⚽ Footy Predictor (EPL & UCL)")

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

st.subheader("Match Predictions (coming soon)")
st.caption("This app connects to your database. After the first data fetch, tables will appear here.")

# Simple sanity check: how many fixtures do we have?
try:
    n = pd.read_sql(text("select count(*) as n from fixtures"), engine)["n"][0]
    st.write(f"Fixtures in DB: **{n}**")
except Exception as e:
    st.info("No data yet or DB not connected. Once the GitHub workflow runs, this will fill.")

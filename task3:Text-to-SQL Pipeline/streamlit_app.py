import streamlit as st
import pandas as pd
from executor import run_pipeline

st.set_page_config(page_title="Text-to-SQL Pipeline", layout="wide")

st.title("🗄️ Text-to-SQL Pipeline and Query Execution System")
st.markdown("""
A prompt-chaining LLM approach to generate PostgreSQL SQL queries from natural language, 
run validations, execute them, and automatically self-correct errors via a single retry.
""")

with st.sidebar:
    st.header("About")
    st.markdown("""
    **Pipeline Steps:**
    1. **Decompose:** Natural Language ➡️ JSON Structure
    2. **Generate:** JSON Structure ➡️ Raw SQL
    3. **Validate:** Checks against destructive commands (DML)
    4. **Execute:** Run against DB
    5. **Self-Correct (Retry):** If execution fails, send error + SQL back to LLM for one fix attempt.
    """)

# Custom CSS for chat-like interface
st.markdown("""
<style>
.user-msg { background-color: #2b313e; padding: 10px; border-radius: 10px; margin-bottom: 10px; }
.sys-msg { background-color: #1e2530; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #454d5e;}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

# Display history
for item in st.session_state.history:
    st.markdown(f'<div class="user-msg">🧑‍💻 <b>You:</b> {item["question"]}</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="sys-msg">', unsafe_allow_html=True)
    if item["status"] == "success":
        st.success("Execution Successful!!")
    else:
        st.error(f"Execution Failed: {item['error_message']}")

    st.code(item["sql"], language="sql")
    
    if item["retry_needed"]:
        st.warning("⚠️ A retry was needed and attempted to fix an initial error.")
        
    if item["result"] and item["status"] == "success":
        df = pd.DataFrame(item["result"], columns=item["columns"])
        st.dataframe(df, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# User input form
with st.form("query_form", clear_on_submit=True):
    col1, col2 = st.columns([8, 1])
    with col1:
        question = st.text_input("Ask a question about the ClassicModels DB...", placeholder="e.g., Which product has the highest quantity in stock?")
    with col2:
        submit = st.form_submit_button("Send")

if submit and question:
    with st.spinner("Processing through LLM Pipeline..."):
        res = run_pipeline(question)
        st.session_state.history.append(res)
        st.rerun()

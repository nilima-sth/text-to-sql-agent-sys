import streamlit as st
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(ROOT, "..")))

from app.agents.orchestrator import run_workflow  # Updated import

st.set_page_config(page_title="Text2SQL Agent", layout="wide")

st.title("Agentic Text-to-SQL Assistant")
st.write("Ask questions about the provided PostgreSQL schema in natural language.")

query = st.text_input("Enter your query", "")

if st.button("Run") and query:
    with st.spinner("Running agent..."):
        res = run_workflow(query)

    st.subheader("Answer")
    final = res.get("summary") or ""

    # Parse the structured bullet output the summarizer returns
    lines = [l.strip() for l in final.splitlines() if l.strip()]
    parsed = {
        "Generated SQL": None,
        "Validated SQL": None,
        "Executed SQL": None,
        "Summary": None,
    }
    for l in lines:
        if l.startswith("* **Generated SQL:**"):
            parsed["Generated SQL"] = l.split("**Generated SQL:**", 1)[1].strip()
        elif l.startswith("* **Validated SQL:**"):
            parsed["Validated SQL"] = l.split("**Validated SQL:**", 1)[1].strip()
        elif l.startswith("* **Executed SQL:**"):
            parsed["Executed SQL"] = l.split("**Executed SQL:**", 1)[1].strip()
        elif l.startswith("* **Summary:**"):
            parsed["Summary"] = l.split("**Summary:**", 1)[1].strip()

    st.markdown("**Generated SQL**")
    st.code(parsed["Generated SQL"] or (res.get("generated_sql") or "No SQL generated"), language="sql")

    st.markdown("**Validated**")
    if parsed["Validated SQL"]:
        if parsed["Validated SQL"].lower().startswith("yes"):
            st.success(parsed["Validated SQL"])
        else:
            st.error(parsed["Validated SQL"])
    else:
        st.write("Unknown")

    st.markdown("**Executed**")
    if parsed["Executed SQL"]:
        if parsed["Executed SQL"].lower().startswith("yes"):
            st.success(parsed["Executed SQL"])
        else:
            st.error(parsed["Executed SQL"])
    else:
        st.write("Unknown")

    st.markdown("**Summary**")
    st.write(parsed["Summary"] or "")

    with st.expander("Workflow details"):
        st.markdown("**SQL**")
        st.code(res.get("generated_sql") or "No SQL generated", language="sql")
        if not res.get("is_valid_sql"):
            st.error(f"Validation: {res.get('validation_error')}")
        st.markdown("**Raw results**")
        rows = res.get("execution_results") or []
        st.write("Showing only the first 10 rows")
        st.json(rows[:10])

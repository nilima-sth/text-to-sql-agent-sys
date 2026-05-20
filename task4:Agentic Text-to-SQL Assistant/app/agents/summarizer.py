from app.agents.llm import chat_complete
from app.prompts import SUMMARIZER_PROMPT, SUMMARY_ONLY_PROMPT
import json


def summarize_results(query: str, sql: str, results, validated: bool, executed: bool) -> str:
    """Produce the requested structured response.

    We ask the LLM only for a short natural-language summary of the results,
    then assemble the exact required bullet list in code to guarantee formatting.
    """
    system = "You are a concise data summarization assistant."

    # Serialize results for passing to the LLM
    try:
        results_json = json.dumps(results, default=str)
    except Exception:
        results_json = str(results)

    # If empty, short summary is explicit
    if results_json.strip() in ("[]", "null", "None", ""):
        summary_text = "No matching rows were found in the database for that query."
    else:
        # Ask the LLM for a 1-2 sentence summary only
        user = SUMMARY_ONLY_PROMPT.format(query=query, results=results_json)
        summary_text = chat_complete(system, user, max_tokens=200, temperature=0.0).strip()

    # Build the exact required structured output (guaranteed formatting)
    generated_sql_line = sql or ""
    validated_line = "Yes" if validated else "No"
    executed_line = "Yes" if executed else "No"

    structured = []
    structured.append(f"* **Generated SQL:** {generated_sql_line}")
    structured.append(f"* **Validated SQL:** {validated_line}")
    structured.append(f"* **Executed SQL:** {executed_line}")
    structured.append(f"* **Summary:** {summary_text}")

    return "\n".join(structured)

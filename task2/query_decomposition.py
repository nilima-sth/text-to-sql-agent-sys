"""Task 2: Query Decomposition for Agentic Text-to-SQL pipeline.

This script:
1. Loads GEMINI_API_KEY from .env.
2. Reads questions from CSV (first column, header row expected).
3. Calls Gemini 2.5 Flash with strict system instructions.
4. Writes decomposed outputs to task2_decomposed_answers.csv.
5. Retries transient failures and records any non-recoverable errors.
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import types


SYSTEM_INSTRUCTION = """You are an expert SQL query decomposition assistant.

Given a natural language analytics question, decompose it into exactly these 5 lines and nothing else:
Intent: [Goal]
Tables: [Tables involved]
Columns: [Columns needed]
Filters: [Conditions or 'None']
Joins: [ON conditions or 'None']

Rules:
- Output exactly five lines in the exact labels/order above.
- Use only tables/columns that exist in the schema.
- If unknown, infer the most likely table/column names from schema only.
- No markdown, no bullets, no explanations, no extra text.
- Keep answers concise and SQL-oriented.
"""

SCHEMA_CONTEXT = """Sample database schema (for decomposition reference):

customers(
  customerNumber PK,
  customerName,
  contactLastName,
  contactFirstName,
  phone,
  addressLine1,
  city,
  state,
  postalCode,
  country,
  salesRepEmployeeNumber FK -> employees.employeeNumber,
  creditLimit
)

orders(
  orderNumber PK,
  orderDate,
  requiredDate,
  shippedDate,
  status,
  comments,
  customerNumber FK -> customers.customerNumber
)

orderdetails(
  orderNumber FK -> orders.orderNumber,
  productCode FK -> products.productCode,
  quantityOrdered,
  priceEach,
  orderLineNumber,
  PK(orderNumber, productCode)
)

products(
  productCode PK,
  productName,
  productLine,
  productScale,
  productVendor,
  quantityInStock,
  buyPrice,
  MSRP
)

payments(
  customerNumber FK -> customers.customerNumber,
  checkNumber,
  paymentDate,
  amount,
  PK(customerNumber, checkNumber)
)

employees(
  employeeNumber PK,
  lastName,
  firstName,
  extension,
  email,
  officeCode FK -> offices.officeCode,
  reportsTo FK -> employees.employeeNumber,
  jobTitle
)

offices(
  officeCode PK,
  city,
  phone,
  addressLine1,
  state,
  country,
  postalCode,
  territory
)
"""


EXPECTED_LABELS = ["Intent", "Tables", "Columns", "Filters", "Joins"]
REQUEST_DELAY_SECONDS = 6


def validate_and_normalize_output(text: str) -> str:
    """Ensure output has exactly required five lines; best-effort normalize."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    if len(lines) == 5 and all(lines[i].startswith(f"{label}:") for i, label in enumerate(EXPECTED_LABELS)):
        return "\n".join(lines)

    # Best-effort parsing in case model returns slightly noisy output.
    extracted = {label: "None" for label in EXPECTED_LABELS}
    for line in lines:
        for label in EXPECTED_LABELS:
            m = re.match(rf"^{label}\s*:\s*(.*)$", line, flags=re.IGNORECASE)
            if m:
                value = m.group(1).strip() or "None"
                extracted[label] = value
                break

    return "\n".join(f"{label}: {extracted[label]}" for label in EXPECTED_LABELS)


def serialize_response(response: object) -> str:
    """Best-effort JSON serialization for Gemini response objects."""
    if hasattr(response, "model_dump_json"):
        try:
            return response.model_dump_json(indent=None)
        except Exception:
            pass
    if hasattr(response, "model_dump"):
        try:
            return json.dumps(response.model_dump(), ensure_ascii=False)
        except Exception:
            pass
    if hasattr(response, "to_dict"):
        try:
            return json.dumps(response.to_dict(), ensure_ascii=False)
        except Exception:
            pass
    return json.dumps({"raw_str": str(response)}, ensure_ascii=False)


def call_gemini_with_retry(
    client: genai.Client,
    model_name: str,
    question: str,
    max_retries: int = 5,
    initial_delay: float = 1.5,
) -> tuple[str, str]:
    """Call Gemini API with exponential backoff for transient failures."""
    user_prompt = (
        f"{SCHEMA_CONTEXT}\n"
        f"Question: {question}\n\n"
        "Return decomposition now."
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.0,
                ),
            )

            raw_text = (response.text or "").strip()
            if not raw_text:
                raise ValueError("Empty response from Gemini API.")

            normalized = validate_and_normalize_output(raw_text)
            raw_json = serialize_response(response)
            return normalized, raw_json

        except Exception as exc:  # Handles rate limits, network, and API-side errors.
            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed after {max_retries} attempts: {exc}"
                ) from exc

            sleep_s = initial_delay * (2 ** (attempt - 1))
            print(
                f"[WARN] Attempt {attempt}/{max_retries} failed for question. "
                f"Retrying in {sleep_s:.1f}s. Error: {exc}"
            )
            time.sleep(sleep_s)

    # Defensive fallback (loop either returns or raises above).
    raise RuntimeError("Unexpected retry loop exit.")


def read_questions(csv_path: Path) -> List[str]:
    """Read questions from first column of CSV with header row."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    questions: List[str] = []
    with csv_path.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.reader(infile)
        next(reader, None)  # skip header
        for row in reader:
            if not row:
                continue
            q = row[0].strip()
            if q:
                questions.append(q)

    if not questions:
        raise ValueError(f"No questions found in CSV: {csv_path}")

    return questions


def write_outputs(output_path: Path, rows: List[dict]) -> None:
    """Write decomposition results to output CSV."""
    fieldnames = ["question_no", "question", "decomposition", "raw_json_response"]
    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    """Main entrypoint."""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not found. Add it to .env (see .env.template)."
        )

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"

    script_dir = Path(__file__).resolve().parent
    input_csv = script_dir / "SQL_QUESTIONS - sql_questions_only.csv"
    # Fallback to user-mentioned alternate name if present.
    fallback_csv = script_dir / "question_only.csv"
    output_csv = script_dir / "task2_decomposed_answers.csv"

    source_csv = input_csv if input_csv.exists() else fallback_csv
    questions = read_questions(source_csv)

    total = len(questions)
    print(f"Loaded {total} questions from: {source_csv}")

    results = []
    for idx, question in enumerate(questions, start=1):
        print(f"[{idx}/{total}] Decomposing question...")
        try:
            decomposition, raw_json_response = call_gemini_with_retry(
                client=client,
                model_name=model_name,
                question=question,
            )
        except Exception as exc:
            # Gracefully capture unrecoverable failures in output file.
            decomposition = (
                "Intent: ERROR\n"
                "Tables: ERROR\n"
                "Columns: ERROR\n"
                f"Filters: API_ERROR ({str(exc)[:200]})\n"
                "Joins: ERROR"
            )
            raw_json_response = json.dumps(
                {"error": str(exc)[:500]}, ensure_ascii=False
            )
            print(f"[ERROR] Question {idx} failed: {exc}")

        results.append(
            {
                "question_no": idx,
                "question": question,
                "decomposition": decomposition,
                   "raw_json_response": raw_json_response,
            }
        )

        # Throttle requests to stay within free-tier API rate limits.
        if idx < total:
            print("Sleeping for 6 seconds to respect API rate limits...")
            time.sleep(REQUEST_DELAY_SECONDS)

    write_outputs(output_csv, results)
    print(f"Done. Wrote {len(results)} rows to: {output_csv}")


if __name__ == "__main__":
    main()

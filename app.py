import os
import re

import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from few_shot_examples import FEW_SHOT_EXAMPLES

# Load environment variables from the parent directory
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# database connection
engine = create_engine(os.getenv('DATABASE_URL'))

class Query(BaseModel):
    query: str = Field(description="The SQL query to execute")

# configure agent

model="groq:qwen/qwen3-32b"
agent=create_agent(
        model=model,
        response_format=Query,

    )

SYSTEM_PROMPT = """
You are an expert PostgreSQL SQL generator.

Your job is to return exactly one valid PostgreSQL SELECT query for the user's request.
Return only the SQL query. Do not return explanations, markdown, comments, or code fences.

Database:
- Server: PostgreSQL
- Database: dse_price
- Table: price_file_data

Schema:
- date: date in YYYY-MM-DD format
- inst_code: instrument code in text format
- open: open price in float format
- high: high price in float format
- low: low price in float format
- close: close price in float format
- ltp: last trade price in float format
- trade: number of trades in integer format
- value: traded value in float format, in millions
- volume: total traded shares in integer format

Important PostgreSQL rules:
- Use PostgreSQL syntax only.
- Only query from price_file_data.
- Generate read-only SQL. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, GRANT, or REVOKE.
- For ranked, lag/lead, rolling, cumulative, or comparison requests, use window functions when appropriate.
- Prefer CTEs for complex queries if it improves correctness.
- When the user asks for recent dates, use ORDER BY date DESC with LIMIT unless they explicitly ask for ascending order.
- For case-insensitive instrument matching, prefer UPPER(inst_code) = UPPER('ACI').
- If the user mentions moving average, running total, previous day, highest per group, nth row, gain/loss streak, or ranking, use PostgreSQL window functions.
- If a request is ambiguous, make the safest reasonable assumption and still return one executable query.
"""

def select_few_shot_examples(prompt: str, max_examples: int = 2) -> str:
    prompt_lower = prompt.lower()
    selected = []

    for item in FEW_SHOT_EXAMPLES:
        if any(keyword in prompt_lower for keyword in item["keywords"]):
            selected.append(item["example"])
        if len(selected) >= max_examples:
            break

    if not selected:
        selected.append(FEW_SHOT_EXAMPLES[0]["example"])

    return "\n\nRelevant examples:\n\n" + "\n\n".join(selected)

def normalize_sql(raw_sql: str) -> str:
    cleaned = raw_sql.strip()
    cleaned = re.sub(r"^```sql\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()
    cleaned = re.sub(r";+\s*$", "", cleaned)
    return cleaned


def validate_sql(sql: str) -> str:
    normalized = sql.strip().lower()
    if not normalized.startswith(("select", "with")):
        raise ValueError("Only SELECT queries are allowed.")

    blocked = ("insert ", "update ", "delete ", "drop ", "alter ", "create ", "truncate ", "grant ", "revoke ")
    if any(keyword in normalized for keyword in blocked):
        raise ValueError("Generated query contains a blocked SQL operation.")

    return sql


def extract_sql(response) -> str:
    structured = getattr(response, "get", None)
    if callable(structured):
        structured = response.get("structured_response")
    else:
        structured = None

    if structured and getattr(structured, "query", None):
        return structured.query

    if isinstance(response, dict):
        messages = response.get("messages") or []
        for message in reversed(messages):
            content = getattr(message, "content", None) or message.get("content")
            if isinstance(content, str) and content.strip():
                return content

    raise ValueError("Model did not return a SQL query.")


def generate_sql(propmt):
    try:
        prompt_with_examples = f"{SYSTEM_PROMPT}{select_few_shot_examples(propmt)}"
        messages = [
            {"role": "system", "content": prompt_with_examples},
            {"role": "user", "content": f"{propmt}"}
        ]
        response = agent.invoke({"messages": messages})
        sql = normalize_sql(extract_sql(response))
        validate_sql(sql)
        return sql
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def fetch_data(query):
    try:
        if isinstance(query, str) and query.startswith("Error generating SQL:"):
            return query

        with engine.connect() as connection:
            result = pd.read_sql(text(query), con=connection)
            if result.empty:
                return "No data found"
        return result
    except Exception as e:
        return f"Error fetching data: {str(e)}\nGenerated SQL: {query}"

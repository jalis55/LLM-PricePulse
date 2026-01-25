from sqlalchemy import create_engine,text
from dotenv import load_dotenv
import os
from langchain.agents import create_agent
from pydantic import BaseModel,Field
import pandas as pd

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
You are a SQL expert.Your task is to generate a SQL query based on the table schema.The table schema is as follows:
Database Server: PostgreSQL
Database Name: dse_price
table_name:price_file_data
columns:
    - date: date in YYYY-MM-DD format
    - inst_code: insturment name in string format
    - open: open price in float format
    - high: high price in float format
    - low: low price in float format
    - close: close price in float format
    - ltp: last trade price in float format
    - trade: number of trades in int format
    - value: value in float format in million
    - volume: total share buy/sell in int format

Your task is to generate a SQL query based on the table schema and it should just the query not the explanation.
output example:
    select * from price_file_data where date = '2022-01-01' and inst_code = 'ACI';

"""

def generate_sql(propmt):
    try:
        messages = [
            {"role": "system", "content":f"{SYSTEM_PROMPT} "},
            {"role": "user", "content": f"{propmt}"}
        ]
        response = agent.invoke({"messages": messages})
        return response
    except Exception as e:
        return f"Error generating SQL: {str(e)}"

def fetch_data(query):
    try:
        with engine.connect() as connection:
            result = pd.read_sql(query['structured_response'].query, con=connection)
            if result.empty:
                return "No data found"
        return result
    except Exception as e:
        return f"Error fetching data: {str(e)}"


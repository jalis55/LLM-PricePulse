# PricePulse

This project is a Streamlit-based application that allows users to query stock price history using natural language. It leverages Groq's LLM (Powered by Qwen) via LangChain to translate user questions into SQL queries, which are then executed against a PostgreSQL database.

## Features

- **Natural Language Interface**: Ask questions like "Show me the closing price of ACI for the last 7 days".
- **SQL Generation**: Automatically generates accurate SQL queries based on the database schema.
- **Data Visualization**: Displays the retrieved data in an interactive table.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL Database
- Groq API Key

## Installation

1.  **Install Dependencies**:
    Ensure you have `pip` installed, then run:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Setup**:
    Create a `.env` file in the project root directory and add your environment variables:

    ```env
    GROQ_API_KEY=your_groq_api_key_here
    DATABASE_URL=postgresql://username:password@localhost:5432/dse_price
    ```

## Database Schema

The application expects a table named `price_file_data` in the database with the following columns:

- `date`: (Date) YYYY-MM-DD
- `inst_code`: (String) Instrument name
- `open`: (Float) Open price
- `high`: (Float) High price
- `low`: (Float) Low price
- `close`: (Float) Close price
- `ltp`: (Float) Last trade price
- `trade`: (Integer) Number of trades
- `value`: (Float) Value in millions
- `volume`: (Integer) Total share buy/sell

## Usage

To run the application, use the Streamlit CLI:

```bash
streamlit run chat_ui.py
```

The application will open in your default web browser. You can then enter queries in the text area and click "Run" to see the results.

## Project Structure

- `app.py`: Contains the core logic for the LangChain agent, SQL generation, and database connection.
- `chat_ui.py`: The Streamlit frontend interface.
- `requirements.txt`: List of Python dependencies.

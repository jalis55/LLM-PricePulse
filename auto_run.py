import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# SQLAlchemy 1.4+ and 2.0 require 'postgresql://' instead of 'postgres://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)
BD_TIMEZONE = ZoneInfo("Asia/Dhaka")
WEEKEND_DAYS = {"friday", "saturday"}


def scraper(from_dt, to_dt):
    url = f"https://dsebd.org/day_end_archive.php?startDate={from_dt}&endDate={to_dt}&inst=All%20Instrument&archive=data"
    print(f"Scraping data from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        table = soup.find('table', class_='table table-bordered background-white shares-table fixedHeader')
        if not table:
            print("Target table not found on the page.")
            return None
            
        tbody = table.find('tbody')
        if not tbody:
            print("Table body (tbody) not found.")
            return None
            
        tbody_trs = tbody.find_all('tr')
        if not tbody_trs:
            print("No rows (tr) found in the table.")
            return None
            
        print(f"Found {len(tbody_trs)} potential rows.")
        rows = []
        for tr in tbody_trs:
            tds = tr.find_all('td')
            if len(tds) < 11:
                continue
            # Extract data from columns
            try:
                row = [td.text.strip() for td in tds[1:3]]
                # numeric columns are from index 3 onwards
                numeric_data = [float(td.text.strip().replace(',','')) if td.text.strip() and td.text.strip() != '--' else 0.0 for td in tds[3:]]
                row = row + numeric_data
                rows.append(row)
            except (ValueError, IndexError) as e:
                # Skip rows that don't match expected format
                continue
        return rows
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None

cols = ['date', 'inst_code', 'ltp', 'high', 'low', 'open', 'close', 'ycp', 'trade', 'value', 'volume']


def should_run_today(now: datetime) -> bool:
    return now.strftime("%A").lower() not in WEEKEND_DAYS


def main() -> None:
    now = datetime.now(BD_TIMEZONE)
    date_str = now.strftime("%Y-%m-%d")

    if not should_run_today(now):
        print(f"Skipping run for {date_str} because it is {now.strftime('%A')} in Bangladesh.")
        return

    rows = scraper(date_str, date_str)
    if rows and rows != [[]]:
        df = pd.DataFrame(rows, columns=cols)
        df.to_sql('price_file_data', engine, if_exists='append', index=False)
        print(f"Successfully written {len(df)} rows to PostgreSQL")
    else:
        print(f"No rows found for {date_str}.")


if __name__ == "__main__":
    main()

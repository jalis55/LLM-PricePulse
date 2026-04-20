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
    raise ValueError("DATABASE_URL is not set in the .env file.")

engine = create_engine(DATABASE_URL)
BD_TIMEZONE = ZoneInfo("Asia/Dhaka")
WEEKEND_DAYS = {"friday", "saturday"}


def scraper(from_dt, to_dt):
    url = f"https://dsebd.org/day_end_archive.php?startDate={from_dt}&endDate={to_dt}&inst=All%20Instrument&archive=data"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tbody_trs = soup.find('table', class_='table table-bordered background-white shares-table fixedHeader').find('tbody').find_all('tr')
        rows = []
        for tr in tbody_trs:
            tds = tr.find_all('td')
            row = [td.text.strip() for td in tds[1:3]]
            row = row + [float(td.text.strip().replace(',','')) for td in tds[3:]]
            rows.append(row)
        return rows
    except:
        print("Error in scraping")
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

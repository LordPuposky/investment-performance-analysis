# This file is responsible for loading the S&P 500 dataset and cleaning it
# before any analysis is done. It is used by main.py.
#
# Dataset source: "S&P 500 stock data" by camnugent on Kaggle
# https://www.kaggle.com/datasets/camnugent/sandp500
# File used: all_stocks_5yr.csv

import pandas as pd

CSV_FILE = "all_stocks_5yr.csv"


def load_data():
    """
    Read the CSV file into a Pandas DataFrame, convert the date column
    to an actual date type, and remove rows that are missing price data.
    Returns the cleaned DataFrame, sorted by stock name and date.
    """
    df = pd.read_csv(CSV_FILE)

    # Convert the date column from text to a real datetime type,
    # so we can filter and group by year later.
    df["date"] = pd.to_datetime(df["date"])

    # A few rows are missing open/high/low values. Since we mainly need
    # the closing price for returns, we only drop rows where the close
    # price itself is missing (there are none), and otherwise fill small
    # gaps in open/high/low using the closing price of that same row.
    df["open"] = df["open"].fillna(df["close"])
    df["high"] = df["high"].fillna(df["close"])
    df["low"] = df["low"].fillna(df["close"])

    # Sort so that, for each stock, rows are in date order.
    # This matters for calculating daily returns correctly.
    df = df.sort_values(["Name", "date"]).reset_index(drop=True)

    return df


def add_daily_returns(df):
    """
    Add a 'daily_return' column: the percent change in closing price
    from one day to the next, calculated separately for each stock.
    """
    df = df.copy()
    df["daily_return"] = df.groupby("Name")["close"].pct_change()
    return df


if __name__ == "__main__":
    # Quick manual check: load the data and print some basic information.
    data = load_data()
    print(f"Rows: {len(data)}")
    print(f"Unique stocks: {data['Name'].nunique()}")
    print(f"Date range: {data['date'].min().date()} to {data['date'].max().date()}")

    data_with_returns = add_daily_returns(data)
    print("\nSample with daily returns:")
    print(data_with_returns[["date", "Name", "close", "daily_return"]].head())
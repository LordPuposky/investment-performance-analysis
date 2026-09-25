# analysis.py
# This file answers the three questions about the S&P 500 dataset.
# It works together with data_loader.py, which loads and cleans the data.

import pandas as pd
import data_loader


def calculate_stock_summary(df):
    """
    Build one summary row per stock, with the numbers needed to answer
    all three questions:
      - total_return_pct: overall percent change over the 5-year period.
      - volatility: standard deviation of daily returns (risk).
      - risk_adjusted_return: total_return_pct divided by volatility.

    This is shared logic, used by get_risk_adjusted_return() and
    get_top_growth_and_decline(), so the calculation is only written once.
    """
    df = data_loader.add_daily_returns(df)

    results = []
    for stock_name, stock_data in df.groupby("Name"):
        stock_data = stock_data.sort_values("date")

        first_close = stock_data["close"].iloc[0]
        last_close = stock_data["close"].iloc[-1]
        total_return = (last_close - first_close) / first_close * 100

        volatility = stock_data["daily_return"].std()

        if volatility and volatility > 0:
            risk_adjusted_return = total_return / volatility
        else:
            risk_adjusted_return = 0

        results.append({
            "Name": stock_name,
            "total_return_pct": round(total_return, 2),
            "volatility": round(volatility, 4) if volatility else 0,
            "risk_adjusted_return": round(risk_adjusted_return, 2),
        })

    return pd.DataFrame(results)


def get_risk_adjusted_return(summary_df, top_n=10):
    """
    Question 1: Which stocks had the best risk-adjusted return in the period?
    A higher risk_adjusted_return means more return for each unit of risk.
    Returns the top_n stocks, sorted from best to worst.
    """
    return summary_df.sort_values(
        "risk_adjusted_return", ascending=False
    ).reset_index(drop=True).head(top_n)


def get_top_growth_and_decline(summary_df, top_n=10):
    """
    Question 2: Which 10 stocks had the highest percentage growth over
    5 years, and which had the biggest drop?

    Returns two DataFrames: the top_n stocks with the highest total
    return, and the top_n stocks with the lowest (most negative) total
    return, both sorted so the most extreme value is first.
    """
    top_growth = summary_df.sort_values(
        "total_return_pct", ascending=False
    ).reset_index(drop=True).head(top_n)

    top_decline = summary_df.sort_values(
        "total_return_pct", ascending=True
    ).reset_index(drop=True).head(top_n)

    return top_growth, top_decline


def get_annual_volatility(df):
    """
    Question 3: How did average market volatility change year by year?

    For each year in the dataset, this pools together the daily returns
    of every stock and calculates the standard deviation, which gives a
    single "market volatility" number per year. A higher number means
    the market as a whole moved more sharply (more risk) that year.

    Returns a DataFrame with one row per year, sorted by year.
    """
    df = data_loader.add_daily_returns(df)
    df["year"] = df["date"].dt.year

    yearly = df.groupby("year")["daily_return"].std().reset_index()
    yearly.columns = ["year", "market_volatility"]
    yearly["market_volatility"] = yearly["market_volatility"].round(4)

    return yearly


if __name__ == "__main__":
    data = data_loader.load_data()
    summary = calculate_stock_summary(data)

    print("=== Question 1: Best risk-adjusted return (top 10) ===")
    top_stocks = get_risk_adjusted_return(summary, top_n=10)
    print(top_stocks.to_string(index=False))

    print("\n=== Question 2: Highest growth over 5 years (top 10) ===")
    growth, decline = get_top_growth_and_decline(summary, top_n=10)
    print(growth[["Name", "total_return_pct"]].to_string(index=False))

    print("\n=== Question 2: Biggest drop over 5 years (top 10) ===")
    print(decline[["Name", "total_return_pct"]].to_string(index=False))

    print("\n=== Question 3: Average market volatility by year ===")
    yearly_volatility = get_annual_volatility(data)
    print(yearly_volatility.to_string(index=False))
    most_volatile_year = yearly_volatility.loc[
        yearly_volatility["market_volatility"].idxmax(), "year"
    ]
    print(f"\nMost volatile year: {most_volatile_year}")
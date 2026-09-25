# This file answers the three questions about the S&P 500 dataset.
# It works together with data_loader.py, which loads and cleans the data.

import pandas as pd
import data_loader


def get_risk_adjusted_return(df, top_n=10):
    """
    Question 1: Which stocks had the best risk-adjusted return in the period?

    For each stock, calculate:
        - total_return: the overall percent change from the first to the
        last closing price in the dataset (5 years).
        - volatility: the standard deviation of daily returns, which is a
        common way to measure risk (how much the price jumps around).
        - risk_adjusted_return: total_return divided by volatility. This is
        a simplified version of the idea behind the Sharpe ratio: a
        higher number means more return for each unit of risk taken.

    Returns a DataFrame with the top_n stocks, sorted by risk-adjusted
    return, from best to worst.
    """
    df = data_loader.add_daily_returns(df)

    results = []
    # Group the data by stock, so we calculate one summary per company.
    for stock_name, stock_data in df.groupby("Name"):
        stock_data = stock_data.sort_values("date")

        first_close = stock_data["close"].iloc[0]
        last_close = stock_data["close"].iloc[-1]
        total_return = (last_close - first_close) / first_close * 100

        # Standard deviation of daily returns = volatility (risk).
        volatility = stock_data["daily_return"].std()

        # Avoid dividing by zero for stocks with almost no price movement.
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

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        "risk_adjusted_return", ascending=False
    ).reset_index(drop=True)

    return results_df.head(top_n)


if __name__ == "__main__":
    data = data_loader.load_data()

    print("=== Question 1: Best risk-adjusted return (top 10) ===")
    top_stocks = get_risk_adjusted_return(data, top_n=10)
    print(top_stocks.to_string(index=False))
from typing import Union
from datetime import datetime
from utils.helpers import to_scalar
import yfinance as yf
import pandas as pd

# Type aliases for clarity
DateType = Union[str, datetime]


def get_sp500_data(start_date: DateType, end_date: DateType) -> pd.DataFrame:
    """
    Download S&P 500 historical data.

    Args:
        start_date: Start date for data download
        end_date: End date for data download

    Returns:
        DataFrame with S&P 500 price data
    """
    sp500 = yf.download("^GSPC", start=start_date, end=end_date)
    return sp500


def calculate_moving_averages(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate 50-day and 200-day moving averages.

    Args:
        data: DataFrame with price data

    Returns:
        DataFrame with added moving average columns
    """
    data["MA50"] = data["Close"].rolling(window=50).mean()
    data["MA200"] = data["Close"].rolling(window=200).mean()
    return data


def generate_signals(data: pd.DataFrame) -> pd.DataFrame:
    """
    Generate buy/sell signals based on moving average crossovers.

    Args:
        data: DataFrame with price and moving average data

    Returns:
        DataFrame with added signal column
    """
    data["Signal"] = 0
    # Buy signal (1): MA50 crosses above MA200
    data.loc[
        (data["MA50"] > data["MA200"])
        & (data["MA50"].shift(1) <= data["MA200"].shift(1)),
        "Signal",
    ] = 1
    # Sell signal (-1): MA50 crosses below MA200
    data.loc[
        (data["MA50"] < data["MA200"])
        & (data["MA50"].shift(1) >= data["MA200"].shift(1)),
        "Signal",
    ] = -1
    return data


def prepare_strategy_data(sp500_data: pd.DataFrame, bh_shares: float) -> pd.DataFrame:
    """
    Calculate strategy values over time.

    Args:
        sp500_data: DataFrame with price and signal data
        bh_shares: Number of shares for buy and hold strategy

    Returns:
        DataFrame with strategy values
    """

    # Create buy and hold values
    bh_values = []
    for i in range(len(sp500_data)):
        if i < 200:  # No investment before day 200
            bh_values.append(None)
        else:
            price = to_scalar(sp500_data["Close"].iloc[i])
            bh_values.append(bh_shares * price)

    sp500_data["BH_Value"] = bh_values

    # Initialize MA values
    ma_values = [None] * len(sp500_data)
    sp500_data["MA_Value"] = ma_values

    # Set starting value
    sp500_data.loc[sp500_data.index[200], "MA_Value"] = 10000.0

    # Calculate MA strategy values over time
    current_value = 10000.0
    in_market = False
    shares = 0.0

    for i in range(201, len(sp500_data)):
        prev_idx = sp500_data.index[i - 1]
        curr_idx = sp500_data.index[i]

        prev_signal = to_scalar(sp500_data.loc[prev_idx, "Signal"])
        prev_close = to_scalar(sp500_data.loc[prev_idx, "Close"])
        curr_close = to_scalar(sp500_data.loc[curr_idx, "Close"])

        if prev_signal == 1 and not in_market:
            shares = current_value / prev_close
            in_market = True
        elif prev_signal == -1 and in_market:
            current_value = shares * prev_close
            shares = 0
            in_market = False

        if in_market:
            sp500_data.loc[curr_idx, "MA_Value"] = shares * curr_close
        else:
            sp500_data.loc[curr_idx, "MA_Value"] = current_value

    return sp500_data

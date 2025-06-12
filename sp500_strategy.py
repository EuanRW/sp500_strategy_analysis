import os
from datetime import datetime
from typing import Dict, List, Union, Tuple, Optional, Any
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

# Use non-interactive backend for WSL
plt.switch_backend("Agg")

# Type aliases for clarity
Scalar = Union[float, int]
DataFrameOrSeries = Union[pd.DataFrame, pd.Series]
DateType = Union[str, datetime]
SignalType = Dict[str, Any]
TransactionType = Dict[str, Any]


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


def to_scalar(value: Any) -> float:
    """
    Convert a pandas Series, DataFrame, or other value to a scalar float.

    Args:
        value: Value to convert

    Returns:
        Float value
    """
    if isinstance(value, (pd.Series, pd.DataFrame)):
        if value.empty:
            return 0.0
        return float(value.iloc[0])
    return float(value)


def buy_and_hold(data: pd.DataFrame) -> Dict[str, float]:
    """
    Implement buy and hold strategy.

    Args:
        data: DataFrame with price data

    Returns:
        Dict with strategy results
    """
    # Assume we invest $10,000 at the beginning
    initial_investment: float = 10000.0
    shares: float = initial_investment / to_scalar(
        data["Close"].iloc[200]
    )  # Start after we have enough data for MAs
    final_value: float = shares * to_scalar(data["Close"].iloc[-1])
    returns: float = (final_value - initial_investment) / initial_investment * 100

    return {
        "initial_investment": initial_investment,
        "final_value": final_value,
        "return_percentage": returns,
        "shares": shares,
    }


def ma_crossover_strategy(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Implement moving average crossover strategy.

    Args:
        data: DataFrame with price and signal data

    Returns:
        Dict with strategy results and transactions
    """
    # Initialize
    initial_investment: float = 10000.0
    cash: float = initial_investment
    shares: float = 0.0
    in_market: bool = False
    transactions: List[Dict[str, Any]] = []

    # Skip the first 200 days to ensure we have both MAs
    for i in range(200, len(data)):
        date = data.index[i]
        price = to_scalar(data["Close"].iloc[i])
        signal = to_scalar(data["Signal"].iloc[i])

        # Buy signal and not in market
        if signal == 1 and not in_market:
            shares = cash / price
            cash = 0.0
            in_market = True
            transactions.append(
                {
                    "date": date,
                    "action": "BUY",
                    "price": price,
                    "shares": shares,
                    "value": shares * price,
                }
            )

        # Sell signal and in market
        elif signal == -1 and in_market:
            cash = shares * price
            shares = 0.0
            in_market = False
            transactions.append(
                {
                    "date": date,
                    "action": "SELL",
                    "price": price,
                    "shares": 0,
                    "value": cash,
                }
            )

    # Calculate final value - ensure scalars
    final_cash = cash
    final_shares = shares
    final_price = to_scalar(data["Close"].iloc[-1])

    final_value = final_cash if final_cash > 0 else final_shares * final_price
    returns = (final_value - initial_investment) / initial_investment * 100

    return {
        "initial_investment": initial_investment,
        "final_value": final_value,
        "return_percentage": returns,
        "transactions": transactions,
    }


def plot_strategies(
    sp500_data: pd.DataFrame, bh_shares: float
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Create plots comparing the strategies.

    Args:
        sp500_data: DataFrame with price, MA, and signal data
        bh_shares: Number of shares for buy and hold strategy

    Returns:
        Matplotlib figure and axes
    """
    # Create figure and subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Top subplot: Price and Moving Averages
    ax1.plot(sp500_data.index, sp500_data["Close"], label="S&P 500")
    ax1.plot(sp500_data.index, sp500_data["MA50"], label="50-day MA")
    ax1.plot(sp500_data.index, sp500_data["MA200"], label="200-day MA")

    # Add buy/sell markers
    buy_signals = sp500_data[sp500_data["Signal"] == 1]
    sell_signals = sp500_data[sp500_data["Signal"] == -1]

    ax1.scatter(
        buy_signals.index,
        buy_signals["Close"],
        color="green",
        marker="^",
        s=100,
        label="Buy Signal",
    )
    ax1.scatter(
        sell_signals.index,
        sell_signals["Close"],
        color="red",
        marker="v",
        s=100,
        label="Sell Signal",
    )

    ax1.set_title("S&P 500 with Moving Averages and Signals")
    ax1.legend()

    # Bottom subplot: Strategy Comparison
    ax2.plot(
        sp500_data.index[200:], sp500_data["BH_Value"][200:], "b-", label="Buy and Hold"
    )
    ax2.plot(
        sp500_data.index[200:], sp500_data["MA_Value"][200:], "r-", label="MA Crossover"
    )

    ax2.legend(loc="best")
    ax2.set_title("Strategy Performance Comparison")

    plt.tight_layout()

    return fig, (ax1, ax2)


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
    bh_values: List[Optional[float]] = []
    for i in range(len(sp500_data)):
        if i < 200:  # No investment before day 200
            bh_values.append(None)
        else:
            price = to_scalar(sp500_data["Close"].iloc[i])
            bh_values.append(bh_shares * price)

    sp500_data["BH_Value"] = bh_values

    # Initialize MA values
    ma_values: List[Optional[float]] = [None] * len(sp500_data)
    sp500_data["MA_Value"] = ma_values

    # Set starting value
    sp500_data.loc[sp500_data.index[200], "MA_Value"] = 10000.0

    # Calculate MA strategy values over time
    current_value: float = 10000.0
    in_market: bool = False
    shares: float = 0.0

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


def create_results_dir() -> None:
    """Create directory for results if it doesn't exist."""
    if not os.path.exists("results"):
        os.makedirs("results")


def main() -> None:
    """Main function to run the analysis."""
    # Create results directory
    create_results_dir()

    # Define date range (e.g., last 10 years)
    end_date = datetime.now()
    start_date = datetime(end_date.year - 10, end_date.month, end_date.day)

    print(
        f"Downloading S&P 500 data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}..."
    )
    try:
        sp500_data = get_sp500_data(start_date, end_date)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return

    print("Calculating moving averages...")
    sp500_data = calculate_moving_averages(sp500_data)

    print("Generating buy/sell signals...")
    sp500_data = generate_signals(sp500_data)

    print("Running buy and hold strategy...")
    bh_results = buy_and_hold(sp500_data)

    print("Running moving average crossover strategy...")
    ma_results = ma_crossover_strategy(sp500_data)

    # Print results
    print("\n===== RESULTS =====")
    print("\nBuy and Hold Strategy:")
    print(f"Initial Investment: ${bh_results['initial_investment']:.2f}")
    print(f"Final Value: ${bh_results['final_value']:.2f}")
    print(f"Return: {bh_results['return_percentage']:.2f}%")

    print("\nMoving Average Crossover Strategy:")
    print(f"Initial Investment: ${ma_results['initial_investment']:.2f}")
    print(f"Final Value: ${ma_results['final_value']:.2f}")
    print(f"Return: {ma_results['return_percentage']:.2f}%")
    print(f"Number of Transactions: {len(ma_results['transactions'])}")

    # Prepare data for plotting
    sp500_data = prepare_strategy_data(sp500_data, bh_results["shares"])

    # Create plots
    fig, _ = plot_strategies(sp500_data, bh_results["shares"])

    # Save the plot
    fig.savefig("results/strategy_comparison.png")
    print(f"\nPlot saved as 'results/strategy_comparison.png'")

    # Save the data to CSV for further analysis
    sp500_data[["Close", "MA50", "MA200", "Signal", "BH_Value", "MA_Value"]].to_csv(
        "results/strategy_data.csv"
    )
    print(f"Data saved as 'results/strategy_data.csv'")


if __name__ == "__main__":
    main()

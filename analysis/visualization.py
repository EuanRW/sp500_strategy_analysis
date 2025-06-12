import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple


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
    # Use non-interactive backend for WSL
    plt.switch_backend("Agg")

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

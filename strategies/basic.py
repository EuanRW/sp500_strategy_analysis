import pandas as pd
from typing import Dict, List, Any
from utils.helpers import to_scalar


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

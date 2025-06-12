import os
from typing import Any
import pandas as pd


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


def create_results_dir() -> None:
    """Create directory for results if it doesn't exist."""
    if not os.path.exists("results"):
        os.makedirs("results")

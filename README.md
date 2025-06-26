# S&P 500 Strategy Analysis

This repository provides tools and scripts for analyzing and comparing investment strategies on the S&P 500 index. It includes data retrieval, strategy implementation, analysis, and visualization components.

## Project Structure

- `main.py`: Entry point for running analyses.
- `sp500_strategy.py`: Core logic for S&P 500 strategy analysis.
- `analysis/`: Analysis and visualization utilities.
- `data/`: Data retrieval and management modules.
- `results/`: Output files such as plots and CSVs.
- `strategies/`: Implementation of different investment strategies.
- `utils/`: Helper functions and utilities.

## Technologies used

- Python 3.10+: Main programming language for all scripts and analysis.
- pandas: Data manipulation and analysis, especially for time series and financial data.
- numpy: Numerical operations and efficient array handling.
- matplotlib: Visualization and plotting of strategy results.

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the main script:**
   ```bash
   python main.py
   ```
3. **Explore the notebook:**
   Open `sp500_analysis.ipynb` in Jupyter for interactive analysis.

## Requirements
- Python 3.10+
- See `requirements.txt` for Python dependencies

## Results
- Strategy comparison plots and data are saved in the `results/` directory.

## License
MIT License

## Strategies Analysed

### 1. Buy and Hold Strategy

This strategy invests a fixed amount (e.g., $10,000) in the S&P 500 at the start (after enough data is available for moving averages) and holds the position throughout the analysis period. No further trades are made. The final value is determined by the number of shares bought initially and the closing price at the end of the period.

- **Initial investment:** $10,000
- **Trading logic:** Buy once, hold until the end
- **Returns:** Calculated as the percentage gain/loss from initial investment to final value

### 2. Moving Average Crossover Strategy

This strategy uses a moving average (MA) crossover signal to determine when to enter and exit the market:

- **Buy signal:** When the short-term MA crosses above the long-term MA, invest all available cash into the S&P 500.
- **Sell signal:** When the short-term MA crosses below the long-term MA, sell all holdings and move to cash.
- **Initial investment:** $10,000
- **Trading logic:** Enter and exit the market based on MA crossover signals, tracking all transactions.
- **Returns:** Calculated as the percentage gain/loss from initial investment to final value, including the number of trades made.

Results and comparison plots for these strategies are saved in the `results/` directory.

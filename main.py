import os
from datetime import datetime

# Import modules from our project structure
from data.retrieval import (
    get_sp500_data,
    calculate_moving_averages,
    generate_signals,
    prepare_strategy_data,
)
from strategies.basic import buy_and_hold, ma_crossover_strategy
from analysis.visualization import plot_strategies
from utils.helpers import create_results_dir


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

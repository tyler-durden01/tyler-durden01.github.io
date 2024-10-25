import os
import datetime
from datetime import timedelta
import yfinance as yf
import pandas as pd

from GetAPIData import GetFinancialStatementData
from GetAPIData import GetMarketCapData
from GetAPIData import GetDailyData
from GetAPIData import GetHorizontalAndVertical



index_parameter = '^GSPC'
expected_market_return = 0.11
tax_rate = 0.21
terminal_growth_rate = 0.02


### DIRECT the attention to def wacc_calcualtion to get totalLiabilities/longTermDebt parameters

# Introduce parameters for years and timing standard outside the function
years_parameter = 5  # Can be 3 or 5 years
timing_standard_parameter = 'M'  # Can be 'D' (Daily), 'W' (Weekly), or 'M' (Monthly)
use_mean_or_median = 'Median'  # Can be 'Mean', 'Median', or 'None' to use specific beta values


# Function to get the U.S. 10-year yield
def get_us_10_year_yield():
    bond_ticker = yf.Ticker("^TNX")  # U.S. 10-year Treasury Yield
    bond_data = bond_ticker.history(period="5d")
    latest_yield = bond_data["Close"].iloc[-1]
    return latest_yield / 100  # Convert to decimal

risk_free_rate = get_us_10_year_yield()


market_risk_premium = expected_market_return - risk_free_rate




# Function to calculate beta and CAPM
def calculate_beta_and_capm(daily_df, index_parameter, start_date, end_date, timing_standard, risk_free_rate, market_risk_premium):
    asset_returns = daily_df['close'].resample(timing_standard).ffill().pct_change()
    
    # Filter the data by date
    asset_returns = asset_returns[(asset_returns.index >= start_date) & (asset_returns.index <= end_date)]

    # Fetch and process the market data for the specified period
    market_data = yf.Ticker(index_parameter).history(period=f"{years_parameter}y")['Close'].resample(timing_standard).ffill().pct_change()
    market_data = market_data[(market_data.index >= start_date) & (market_data.index <= end_date)]

    # Ensure both Series have tz-naive DatetimeIndex
    asset_returns.index = asset_returns.index.tz_localize(None)
    market_data.index = market_data.index.tz_localize(None)

    # Align indices for asset and market data to ensure they match
    asset_returns, market_data = asset_returns.align(market_data, join='inner', axis=0)

    # Calculate variance and covariance
    variance = market_data.var()
    covariance = asset_returns.cov(market_data)
    beta = covariance / variance

    # CAPM calculation
    capm = risk_free_rate + beta * market_risk_premium

    return beta, capm


# Function to calculate WACC
def wacc_calculation(merged_data, ttm_data, risk_free_rate, capm):
    liabilities = merged_data.iloc[0]['totalLiabilities']
    long_term_debt = merged_data.iloc[0]['longTermDebt']
    equity = merged_data.iloc[0]['totalEquity']
    interest_expense = ttm_data.iloc[0]['interestExpense']

    cost_of_debt = interest_expense / long_term_debt if long_term_debt != 0 else 0
    # cost_of_debt = 0.0425

    # wacc = (liabilities / (liabilities + equity) * cost_of_debt * (1 - tax_rate)) + \
    #        (equity / (liabilities + equity) * capm)


    wacc = (long_term_debt / (long_term_debt + equity) * cost_of_debt * (1 - tax_rate)) + \
        (equity / (long_term_debt + equity) * capm)

    return liabilities, long_term_debt, equity, cost_of_debt, wacc


# Main function
def main(ticker):
    # Fetch and process daily data
    daily_prices_df = GetDailyData.collect_daily_price_data(ticker)
    daily_prices_df.index = pd.to_datetime(daily_prices_df.index)

    # Calculate beta and CAPM for different scenarios
    beta_results = []
    for years in [3, 5]:
        start_date = (datetime.date.today() - timedelta(days=365 * years)).strftime('%Y-%m-%d')
        end_date = datetime.date.today().strftime('%Y-%m-%d')

        for timing_standard in ['M', 'W', 'D']:
            beta, capm = calculate_beta_and_capm(
                daily_prices_df, index_parameter, start_date, end_date, timing_standard, risk_free_rate, market_risk_premium
            )
            beta_results.append({
                'Years': years,
                'Timing Standard': timing_standard,
                'Beta': beta,
                'CAPM': capm,
            })

    # Convert the results to a DataFrame
    beta_df = pd.DataFrame(beta_results)

    # Calculate mean and median for beta and CAPM
    beta_df_mean = beta_df[['Beta', 'CAPM']].mean()
    beta_df_median = beta_df[['Beta', 'CAPM']].median()

    # Append mean and median rows to the beta DataFrame
    mean_row = pd.DataFrame([{
        'Years': 'Mean',
        'Timing Standard': '',
        'Beta': beta_df_mean['Beta'],
        'CAPM': beta_df_mean['CAPM'],
    }])
    median_row = pd.DataFrame([{
        'Years': 'Median',
        'Timing Standard': '',
        'Beta': beta_df_median['Beta'],
        'CAPM': beta_df_median['CAPM'],
    }])
    beta_df = pd.concat([beta_df, mean_row, median_row], ignore_index=True)

    # Select beta based on the parameters
    if use_mean_or_median == 'Mean':
        selected_beta = beta_df_mean['Beta']
        selected_capm = beta_df_mean['CAPM']
        # print(f"Selected Beta: Mean = {selected_beta}, CAPM: {selected_capm}")
    elif use_mean_or_median == 'Median':
        selected_beta = beta_df_median['Beta']
        selected_capm = beta_df_median['CAPM']
        # print(f"Selected Beta: Median = {selected_beta}, CAPM: {selected_capm}")
    else:
        # Select beta based on the years and timing_standard parameters
        selected_beta_row = beta_df[(beta_df['Years'] == years_parameter) & 
                                    (beta_df['Timing Standard'] == timing_standard_parameter)]
        
        if selected_beta_row.empty:
            # print(f"No beta found for {years_parameter} years and {timing_standard_parameter} timing.")
            return
        else:
            selected_beta = selected_beta_row['Beta'].values[0]
            selected_capm = selected_beta_row['CAPM'].values[0]
            # print(f"Selected Beta: {selected_beta}, Selected CAPM: {selected_capm}")

    # Proceed with WACC calculation using the selected beta and CAPM
    financial_statements_df = GetFinancialStatementData.collect_financial_statement_data(ticker)
    horizontal_results = GetHorizontalAndVertical.collect_horizontal_and_vertical(financial_statements_df)

    ttm_data = horizontal_results['ttm_df']

    liabilities, long_term_debt, equity, cost_of_debt, wacc = wacc_calculation(
        financial_statements_df, ttm_data, risk_free_rate, selected_capm
    )

    # Create a result dataframe
    result_df = pd.DataFrame({
        'Total Liabilities': [liabilities],
        'Long-Term Debt': [long_term_debt],
        '% Debt': [long_term_debt / (equity + long_term_debt)],
        'Cost of Debt': [cost_of_debt],
        'Tax Rate': 0.21,
        'Total Equity': [equity],
        '% Equity': [equity / (equity + long_term_debt)],
        'CAPM': [selected_capm],
        'Risk-Free Rate': [risk_free_rate],
        'Beta': [selected_beta],
        'Market Risk Premium': [market_risk_premium],
        'Terminal Growth Rate': [terminal_growth_rate],
        'WACC': [wacc]
    }, index=[ticker])

    result_df = result_df.T

    return result_df, beta_df


if __name__ == "__main__":
    # ticker = 'ASML'  # Replace with the desired ticker or make it dynamic based on user input
    main(ticker)





# Raname the functinos
# correct the calcualtions / account for parameters to set for each function
# implement and fix the parameters' variables
# need to also consider the multiple benchmarks
import os
import datetime
from datetime import timedelta
import yfinance as yf
import pandas as pd

from GetAPIData import GetFinancialStatementData
from GetAPIData import GetMarketCapData
from GetAPIData import GetDailyData
from GetAPIData import GetHorizontalAndVertical
# from GetHorizontalAndVertical import collect_horizontal_and_vertical


# Function to get the U.S. 10-year yield
def get_us_10_year_yield():
    bond_ticker = yf.Ticker("^TNX")  # U.S. 10-year Treasury Yield
    bond_data = bond_ticker.history(period="5d")
    latest_yield = bond_data["Close"].iloc[-1]
    return latest_yield / 100  # Convert to decimal

# Function to calculate the market risk premium
def calculate_market_risk_premium(expected_market_return, risk_free_rate):
    return expected_market_return - risk_free_rate

'''
def calculate_beta_and_capm(daily_df, market_ticker, start_date, end_date, timing_standard, risk_free_rate, market_risk_premium):
    # Resample and calculate returns for the ticker
    asset_df = daily_df.resample(timing_standard).ffill().pct_change()
    asset_df = asset_df[(asset_df.index >= start_date) & (asset_df.index <= end_date)]

    # Fetch and process the market data for S&P 500 (^GSPC)
    market_data = yf.Ticker(market_ticker).history(period="5y")['Close'].resample(timing_standard).ffill().pct_change()
    market_data = market_data[(market_data.index >= start_date) & (market_data.index <= end_date)]

    # Ensure both DataFrames have tz-naive DatetimeIndex
    asset_df.index = asset_df.index.tz_localize(None)
    market_data.index = market_data.index.tz_localize(None)

    # Calculate variance and covariance
    variance = market_data.var()
    covariance = asset_df.cov(market_data)
    beta = covariance / variance

    # CAPM calculation
    capm = risk_free_rate + beta * market_risk_premium

    return beta, capm
'''


'''
def calculate_beta_and_capm(daily_df, market_ticker, start_date, end_date, timing_standard, risk_free_rate, market_risk_premium):
    # Resample and calculate returns for the ticker
    asset_df = daily_df.resample(timing_standard).ffill().pct_change()
    asset_df = asset_df[(asset_df.index >= start_date) & (asset_df.index <= end_date)]

    # Fetch and process the market data for S&P 500 (^GSPC)
    market_data = yf.Ticker(market_ticker).history(period="5y")['Close'].resample(timing_standard).ffill().pct_change()
    market_data = market_data[(market_data.index >= start_date) & (market_data.index <= end_date)]

    # Ensure both DataFrames have tz-naive DatetimeIndex
    asset_df.index = asset_df.index.tz_localize(None)
    market_data.index = market_data.index.tz_localize(None)

    # Ensure that both Series have data before calculating covariance
    if asset_df.empty or market_data.empty:
        raise ValueError("One or both of the dataframes are empty. Please check the input data.")

    # Align indices for asset and market data to ensure they match
    asset_df, market_data = asset_df.align(market_data, join='inner', axis=0)

    # Calculate variance and covariance
    variance = market_data.var()
    covariance = asset_df['Close'].cov(market_data)
    beta = covariance / variance

    # CAPM calculation
    capm = risk_free_rate + beta * market_risk_premium

    return beta, capm
'''

# Function to calculate beta and CAPM
def calculate_beta_and_capm(daily_df, market_ticker, start_date, end_date, timing_standard, risk_free_rate, market_risk_premium):
    # Check the columns of the daily_df
    print("Columns in daily_prices_df:", daily_df.columns)

    # Select the correct column for calculating returns
    if 'close' in daily_df.columns:
        asset_returns = daily_df['close'].resample(timing_standard).ffill().pct_change()
    elif 'Adj Close' in daily_df.columns:
        asset_returns = daily_df['Adj Close'].resample(timing_standard).ffill().pct_change()
    else:
        raise ValueError("Neither 'Close' nor 'Adj Close' column found in daily prices data.")
    
    # Filter the data by date
    asset_returns = asset_returns[(asset_returns.index >= start_date) & (asset_returns.index <= end_date)]

    # Fetch and process the market data for S&P 500 (^GSPC)
    market_data = yf.Ticker(market_ticker).history(period="5y")['Close'].resample(timing_standard).ffill().pct_change()
    market_data = market_data[(market_data.index >= start_date) & (market_data.index <= end_date)]

    # Ensure both Series have tz-naive DatetimeIndex
    asset_returns.index = asset_returns.index.tz_localize(None)
    market_data.index = market_data.index.tz_localize(None)

    # Ensure that both Series have data before calculating covariance
    if asset_returns.empty or market_data.empty:
        raise ValueError("One or both of the dataframes are empty. Please check the input data.")

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

    cost_of_debt = interest_expense / long_term_debt
    tax_rate = 0.21

    wacc = (liabilities / (liabilities + equity) * cost_of_debt * (1 - tax_rate)) + \
           (equity / (liabilities + equity) * capm)

    return liabilities, long_term_debt, equity, cost_of_debt, wacc

# Main function
def main(ticker):
    # Market risk premium calculation
    expected_market_return = 0.11
    risk_free_rate = get_us_10_year_yield()
    market_risk_premium = calculate_market_risk_premium(expected_market_return, risk_free_rate)

    # Define the period and timing
    years = 3  # Adjust as needed
    timing_standard = 'W'  # 'W' for weekly or 'M' for monthly

    # Set the date range
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    start_date = (datetime.date.today() - timedelta(days=365 * years)).strftime('%Y-%m-%d')

    # Fetch and process daily data
    daily_prices_df = GetDailyData.collect_daily_price_data(ticker)
    daily_prices_df.index = pd.to_datetime(daily_prices_df.index)

    # Calculate beta and CAPM for different scenarios
    beta_results = []
    for years in [3, 5]:
        for timing_standard in ['M', 'W', 'D']:
            beta, capm = calculate_beta_and_capm(
                daily_prices_df, '^GSPC', start_date, end_date, timing_standard, risk_free_rate, market_risk_premium
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

    print(beta_df)

    # WACC calculation
    financial_statements_df = GetFinancialStatementData.collect_financial_statement_data(ticker)
    horizontal_results = GetHorizontalAndVertical.collect_horizontal_and_vertical(financial_statements_df)

    ttm_data = horizontal_results['ttm_df']

    liabilities, long_term_debt, equity, cost_of_debt, wacc = wacc_calculation(
        financial_statements_df, ttm_data, risk_free_rate, beta
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
        'CAPM': [capm],
        'Risk-Free Rate': [risk_free_rate],
        'Beta': [beta],
        'Market Risk Premium': [market_risk_premium],
        'WACC': [wacc]
    }, index=[ticker])

    result_df = result_df.T
    
    # Round and format the DataFrame
    # result_df = result_df.T.applymap(lambda x: f'{x:.4f}' if isinstance(x, (int, float)) else x)
    # result_df.loc['Total Liabilities'] = result_df.loc['Total Liabilities'].astype(float).map('{:.0f}'.format)
    # result_df.loc['Long-Term Debt'] = result_df.loc['Long-Term Debt'].astype(float).map('{:.0f}'.format)
    # result_df.loc['Total Equity'] = result_df.loc['Total Equity'].astype(float).map('{:.0f}'.format)

    print(result_df)

    return(result_df, beta_df)

if __name__ == "__main__":
    # Replace 'ASML' with any desired ticker or make it dynamic based on user input
    main()



# Raname the functinos
# get rid of prints, excess code, excess returns
# correct the calcualtions
# implement and fix the parameters' variables
# Make the CAPM df numeric
import requests
import pandas as pd
from yahoo_fin.stock_info import *
from GetAPIData.GetMarketCapData import collect_market_cap_data
from config import api_key, base_url, start_date, end_date  # Import from config.py


def collect_daily_price_data(ticker):
    # Placeholder for getting daily market data (for illustration)
    daily_prices_yahoo_df = pd.DataFrame(get_data(ticker, start_date=start_date, end_date=end_date))  # Assuming get_data() is defined elsewhere
    daily_prices_yahoo_df.drop(['adjclose', 'ticker'], axis=1, inplace=True)

    # Get the historical market cap data
    df2 = collect_market_cap_data(ticker)


    # Concatenate the DataFrames
    daily_prices_df = pd.concat([daily_prices_yahoo_df, df2], axis=1)

    # Drop the last row (incomplete data) if needed
    daily_prices_df.drop(daily_prices_df.index[-1], inplace=True)

    # Calculate Implied Shares
    daily_prices_df['Implied Shares'] = ((daily_prices_df['marketCap'] / daily_prices_df['close']) / 1000).round(0) * 1000

    # Add 1-year, 3-year, and 5-year prior dates
    daily_prices_df['1YearPriorDate'] = daily_prices_df.index - pd.DateOffset(years=1)
    daily_prices_df['3YearPriorDate'] = daily_prices_df.index - pd.DateOffset(years=3)
    daily_prices_df['5YearPriorDate'] = daily_prices_df.index - pd.DateOffset(years=5)

    # Sort data to ensure proper asof merging
    daily_prices_df.sort_index(inplace=True)

    # Use pd.merge_asof to merge on the nearest trading date (1 year prior)
    daily_prices_df = pd.merge_asof(
        daily_prices_df,
        daily_prices_df[['close', 'marketCap']].rename(columns={'close': 'close_1YearPrior', 'marketCap': 'marketCap_1YearPrior'}),
        left_on='1YearPriorDate', right_index=True, direction='backward'
    )

    # Use pd.merge_asof to merge on the nearest trading date (3 years prior)
    daily_prices_df = pd.merge_asof(
        daily_prices_df,
        daily_prices_df[['close', 'marketCap']].rename(columns={'close': 'close_3YearPrior', 'marketCap': 'marketCap_3YearPrior'}),
        left_on='3YearPriorDate', right_index=True, direction='backward'
    )

    # Use pd.merge_asof to merge on the nearest trading date (5 years prior)
    daily_prices_df = pd.merge_asof(
        daily_prices_df,
        daily_prices_df[['close', 'marketCap']].rename(columns={'close': 'close_5YearPrior', 'marketCap': 'marketCap_5YearPrior'}),
        left_on='5YearPriorDate', right_index=True, direction='backward'
    )

    # Calculate 1-year, 3-year, and 5-year returns for close and market cap.
    daily_prices_df['Return_Close_1Y'] = (daily_prices_df['close'] - daily_prices_df['close_1YearPrior']) / daily_prices_df['close_1YearPrior']
    daily_prices_df['Return_MC_1Y'] = (daily_prices_df['marketCap'] - daily_prices_df['marketCap_1YearPrior']) / daily_prices_df['marketCap_1YearPrior']

    # Calculate 3-year returns
    daily_prices_df['Return_Close_3Y'] = (daily_prices_df['close'] - daily_prices_df['close_3YearPrior']) / daily_prices_df['close_3YearPrior']
    daily_prices_df['Return_MC_3Y'] = (daily_prices_df['marketCap'] - daily_prices_df['marketCap_3YearPrior']) / daily_prices_df['marketCap_3YearPrior']

    # Calculate 5-year returns
    daily_prices_df['Return_Close_5Y'] = (daily_prices_df['close'] - daily_prices_df['close_5YearPrior']) / daily_prices_df['close_5YearPrior']
    daily_prices_df['Return_MC_5Y'] = (daily_prices_df['marketCap'] - daily_prices_df['marketCap_5YearPrior']) / daily_prices_df['marketCap_5YearPrior']

    # Drop intermediate columns if they are not needed
    daily_prices_df.drop(['1YearPriorDate', '3YearPriorDate', '5YearPriorDate', 'close_1YearPrior', 'marketCap_1YearPrior', 
                            'close_3YearPrior', 'marketCap_3YearPrior', 'close_5YearPrior', 'marketCap_5YearPrior'], axis=1, inplace=True)

    '''
    # Generate the moving average periods: start at 15, increment by 15, add 365 and 730 as full years
    moving_average_days = list(range(15, 750, 15)) # + [365, 730]

    # Prepare a dictionary for moving averages
    moving_averages = {}

    # Calculate moving averages for both 'close' and 'marketCap'
    for days in sorted(moving_average_days):
        moving_averages[f'MA_Close_{days}'] = daily_prices_df['close'].rolling(window=days).mean()
        moving_averages[f'MA_MarketCap_{days}'] = daily_prices_df['marketCap'].rolling(window=days).mean()

    # Concatenate all the moving averages into the DataFrame at once
    daily_prices_df = pd.concat([daily_prices_df, pd.DataFrame(moving_averages)], axis=1)
    '''

    return daily_prices_df



'''

Now, I want you to add columns for % change in price and market cap (daily). 
From there, I want you to do similar to the beginning of this conversation, with returns. 
Only, I want you to do it for the averages and the medians, not just the returns.
By the way, I want the data to be in descending order, such that the most recent date is at the top and the oldest date is at the bottom. 
Perhaps you can make this change earlier in the program, before you move and shift around in order to get 1, 3, and 5 years figures. 
That should make the program cleaner and easier for you to write.

'''
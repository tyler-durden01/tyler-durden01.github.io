import requests
import pandas as pd
from datetime import timedelta
from config import api_key, base_url, end_date  # start_date # Import from config.py

def collect_market_cap_data(ticker, years_step=5, iterations=10):
    url = f"{base_url}/historical-market-capitalization/{ticker}"

    # Initialize the DataFrame to store all data
    market_cap_data_df = pd.DataFrame()

    current_end_date = end_date

    # Iterate through the specified number of iterations
    for _ in range(iterations):
        # Calculate the start date by subtracting the step years from the end date
        current_start_date = current_end_date - timedelta(days=years_step * 365)

        # Format dates to the required string format
        params = {
            "from": current_start_date.strftime("%Y-%m-%d"),
            "to": current_end_date.strftime("%Y-%m-%d"),
            "apikey": api_key
        }

        # Send the request
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Convert the JSON response to DataFrame
            data = response.json()
            df = pd.DataFrame(data)

            # Append the data to the full DataFrame
            market_cap_data_df = pd.concat([market_cap_data_df, df])
        else:
            print(f"Failed to fetch data for period {current_start_date} to {current_end_date}")
        
        # Update the end date to the start date for the next iteration, minus one day to avoid overlap
        current_end_date = current_start_date - timedelta(days=1)

    # Reset the index of the final DataFrame
    # market_cap_data_df.reset_index(drop=True, inplace=True)

    #### market_cap_data_df['date'] = pd.to_datetime(market_cap_data_df['date']).dt.strftime('%Y-%m-%d')  # Format dates as 'yyyy-mm-dd'
    # Convert back to datetime format (if needed)
    # print(market_cap_data_df)
    market_cap_data_df['date'] = pd.to_datetime(market_cap_data_df['date'])
    # Set 'date' as the index (in place)
    market_cap_data_df.set_index('date', inplace=True)
    # Drop the 'symbol' column (in place)
    market_cap_data_df.drop('symbol', axis=1, inplace=True)
    # market_cap_data_df.drop('symbol') # , axis=1, inplace=True)


    return market_cap_data_df
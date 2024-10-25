import requests
import pandas as pd
from datetime import datetime, timedelta

# Replace 'YOUR_API_KEY' with your actual API key
API_KEY = '6fe8c4680cf2609b34c3674e0a32720b'

# Define the endpoint URL for upcoming earnings
base_url = 'https://financialmodelingprep.com/api/v3/earning_calendar'
today = datetime.now()
next_week = today + timedelta(days=7)

# Convert dates to string format 'YYYY-MM-DD'
start_date = today.strftime('%Y-%m-%d')
end_date = next_week.strftime('%Y-%m-%d')

# Define query parameters
params = {
    'apikey': API_KEY,
    'from': start_date,
    'to': end_date,
}

# Send GET request to the API
response = requests.get(base_url, params=params)
earnings_data = response.json()

# if len(earnings_data) == 0:
    # print("No earnings releases scheduled for the upcoming week.")

df = pd.DataFrame(earnings_data)
# Select relevant columns
df = df[['symbol', 'date', 'time', 'fiscalDateEnding', 'revenueEstimated', 'revenue', 'epsEstimated', 'eps', 'date', 'epsEstimated', 'fiscalDateEnding']]

# Display the DataFrame
print(df)
export_file = 'Earnings_2024-10-24.xlsx' 
df.to_excel(export_file, index=False)



'''
# additional_info = []
additional_info_dfs = []
ticker_errors = []

for symbol in df['symbol'] :
   # print(symbol)
    
    try: 
        symbol_info_url = f'https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}'
        symbol_info_response = requests.get(symbol_info_url)
        symbol_info = symbol_info_response.json()

        # print(symbol_info)
        additional_info_df = pd.DataFrame(symbol_info)
        additional_info_df = additional_info_df[['symbol', 'mktCap', 'sector', 'industry']]
        additional_info_dfs.append(additional_info_df)
        # print(additional_info_df)
    except:
        ticker_errors.append(symbol)
        print(f'error for {symbol}')

    # print(df2)
    # df2 = df2[['symbol', 'mktCap', 'sector', 'industry']]
    # df2.set_index('symbol', inplace=True)
                

# Merge the two DataFrames based on the 'symbol' column
# df_final = pd.merge(df, df2, on='symbol', right_index=True, how='left')
# df_final = pd.concat([df, df2], axis=1)
# print(df_final)

additional_info_dfs = pd.concat(additional_info_dfs, axis=1)
# additional_info_dfs.columns = df['symbol']
print(additional_info_dfs)
additional_info_dfs.to_excel('Earnings_2024-10-24.xlsx')
'''
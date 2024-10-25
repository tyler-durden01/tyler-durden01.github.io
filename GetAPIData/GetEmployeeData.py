import requests
import pandas as pd
from config import api_key  # Import from config.py
from .GetHorizontalAndVertical import collect_horizontal_and_vertical  # Import the function to use ttm_df; use a relative import


def collect_employee_data(ticker, financial_statements_df):
    # Get the ttm_df from GetHorizontalAndVertical.py
    horizontal_and_vertical_results = collect_horizontal_and_vertical(financial_statements_df)
    ttm_df_invoked = horizontal_and_vertical_results['ttm_df']

    # Construct the URL using the base_url from config.py
    url = f'https://financialmodelingprep.com/api/v4/historical/employee_count?symbol={ticker}&apikey={api_key}'

    # Send the request
    response = requests.get(url)
    data = response.json()

    # Convert the data to a DataFrame
    employee_df = pd.DataFrame(data)

    # Drop unnecessary columns
    # NOTICE: might need these below columns (one day)
    employee_df = employee_df.drop(['companyName', 'source', 'symbol'], axis=1)

    # Keep only the needed columns and set 'periodOfReport' as the index
    employee_df = employee_df[['periodOfReport', 'filingDate', 'acceptanceTime', 'formType', 'cik', 'employeeCount']]
    
    # Convert 'periodOfReport' to datetime format for merging
    employee_df['periodOfReport'] = pd.to_datetime(employee_df['periodOfReport'])

    # Ensure 'date' column in ttm_df is in datetime format
    ttm_df_invoked = ttm_df_invoked.reset_index()
    ttm_df_invoked['date'] = pd.to_datetime(ttm_df_invoked['date'])


    # Merge employee_df with ttm_df_invoked on 'periodOfReport' and 'date'
    employee_df1 = pd.merge(employee_df, ttm_df_invoked[['date', 'revenue']], left_on='periodOfReport', right_on='date', how='inner')


    # Calculate revenue per employee
    employee_df1['revenuePerEmployee'] = employee_df1['revenue'] / employee_df1['employeeCount']

    # Calculate the percentage change in revenue per employee
    # Reverse the order of the DataFrame to apply pct_change correctly
    employee_df1 = employee_df1.iloc[::-1]
    employee_df1['employeeCountPctChange'] = employee_df1['employeeCount'].pct_change() 
    employee_df1['revenuePerEmployeePctChange'] = employee_df1['revenuePerEmployee'].pct_change()
    employee_df1 = employee_df1.iloc[::-1]

    # Drop the 'date' column after merging if not needed
    employee_df1 = employee_df1.drop(['date', 'revenue'], axis=1)
    employee_df1['periodOfReport'] = employee_df1['periodOfReport'].dt.strftime('%Y-%m-%d')
    employee_df1 = employee_df1.set_index('periodOfReport')
    employee_df = employee_df1

    return employee_df
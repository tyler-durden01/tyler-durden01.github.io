# from flask import Blueprint, render_template, request, redirect, url_for
import requests
from datetime import date, timedelta
from yahoo_fin.stock_info import *
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Add routes for HTML pages
@app.route('/get_company_data.html')


# Add a new route to handle the form submission
@app.route('/get_company_data', methods=['GET', 'POST'])
def get_company_data():
    if request.method == 'POST':
    # Get the user input for the ticker symbol
        ticker = request.form['ticker']
    
    
        api_key = '6fe8c4680cf2609b34c3674e0a32720b'

        base_url = 'https://financialmodelingprep.com/api/v3/'

        # Define the endpoints for both income statement and cash flow statement
        income_statement_endpoint = f'income-statement/{ticker}'
        balance_sheet_endpoint = f'balance-sheet-statement/{ticker}'
        cash_flow_statement_endpoint = f'cash-flow-statement/{ticker}'
        earnings_endpoint = f'historical/earning_calendar/{ticker}'

        # Define the parameters for the requests
        params = {
            'apikey': api_key,
            'period': 'quarter'
        }

        # Send a GET request to fetch the finanical statement data
        income_response = requests.get(base_url + income_statement_endpoint, params=params)
        cash_flow_response = requests.get(base_url + cash_flow_statement_endpoint, params=params)
        balance_sheet_response = requests.get(base_url + balance_sheet_endpoint, params=params)
        earnings_response = requests.get(base_url + earnings_endpoint, params=params)

        # Check if both requests were successful (status code 200); can change this to a try and except; not a big fan of this loop
        if income_response.status_code == 200 and cash_flow_response.status_code == 200:
            # Parse the JSON responses for both statements
            income_data = income_response.json()
            cash_flow_data = cash_flow_response.json()
            balance_sheet_data = balance_sheet_response.json()
            earnings_data = earnings_response.json()
            
            # Create Pandas DataFrames from the data
            income_df = pd.DataFrame(income_data)
            cash_flow_df = pd.DataFrame(cash_flow_data)
            balance_sheet_df = pd.DataFrame(balance_sheet_data)
            earnings_df = pd.DataFrame(earnings_data)

            # Filter and select the relevant columns for income statement
            income_df = income_df[[
                'date',
                'revenue',
                'grossProfit',
                'sellingGeneralAndAdministrativeExpenses',
                'operatingIncome',
                'interestExpense',
                'interestIncome',
                'incomeTaxExpense',
                'netIncome'
                ]]

            # Filter and select the relevant columns for cash flow statement
            cash_flow_df = cash_flow_df[[
                'date', 
                'freeCashFlow',
                'depreciationAndAmortization',
                'stockBasedCompensation',
                'deferredIncomeTax',
                'netCashProvidedByOperatingActivities',
                'changeInWorkingCapital',
                'capitalExpenditure',
                'investmentsInPropertyPlantAndEquipment',
                'acquisitionsNet',
                'purchasesOfInvestments',
                'netCashUsedForInvestingActivites',
                'debtRepayment',
                'commonStockIssued',
                'commonStockRepurchased',
                'dividendsPaid',
                'netCashUsedProvidedByFinancingActivities',
                'effectOfForexChangesOnCash',
                'netChangeInCash',
                ]]
            
            balance_sheet_df = balance_sheet_df[[
                'date',
                'cashAndCashEquivalents',
                'shortTermInvestments',
                'cashAndShortTermInvestments',
                'netReceivables',
                'inventory',
                'otherCurrentAssets',
                'totalCurrentAssets',
                'propertyPlantEquipmentNet',
                'goodwill',
                'intangibleAssets',
                'longTermInvestments',
                'otherNonCurrentAssets',
                'totalNonCurrentAssets',
                'totalAssets',
                'accountPayables',
                'shortTermDebt',
                'taxPayables',
                'deferredRevenue',
                'otherCurrentLiabilities',
                'totalCurrentLiabilities',
                'longTermDebt',
                'deferredRevenueNonCurrent',
                'deferredTaxLiabilitiesNonCurrent',
                'otherNonCurrentLiabilities',
                'totalNonCurrentLiabilities',
                'otherLiabilities',
                'capitalLeaseObligations',
                'totalLiabilities',
                'preferredStock',
                'commonStock',
                'retainedEarnings',
                'accumulatedOtherComprehensiveIncomeLoss',
                'othertotalStockholdersEquity',
                'totalStockholdersEquity',
                'totalEquity',
                'totalLiabilitiesAndStockholdersEquity',
                'minorityInterest',
                'totalLiabilitiesAndTotalEquity',
                'totalInvestments',
                'totalDebt',
                'netDebt',
            ]]

            earnings_df = earnings_df.drop(columns=['symbol'])

        else:
            print("Failed to retrieve data.")


        # Merge the two DataFrames on the 'date' column to align the data
        merged_df = pd.merge(income_df, cash_flow_df, on='date', how='inner')
        merged_df = pd.merge(merged_df, balance_sheet_df, on='date', how='inner')


        # Convert numerical columns to numeric data types
        numeric_columns = merged_df.columns.drop('date')
        merged_df[numeric_columns] = merged_df[numeric_columns].apply(pd.to_numeric, errors='coerce')
        merged_df.set_index('date', inplace=True)
        merged_df = merged_df / 1000000
        merged_df = merged_df.round(0)
        # .applymap('{:,.0f}'.format)
        # Convert 'date' column to datetime
        # merged_df['date'] = pd.to_datetime(merged_df['date'])
        # Print the final merged DataFrame
        print(merged_df)

        horizontal_df = merged_df.div(merged_df['revenue'], axis=0)
        horizontal_df = horizontal_df.round(3)
        print(horizontal_df)

        # Calculate the % changes from the next period (descending order)
        # quarterly_pct_change_df = merged_df[::-1].set_index('date').pct_change()
        quarterly_pct_change_df = merged_df[::-1].pct_change()
        quarterly_pct_change_df = (quarterly_pct_change_df[::-1]).round(3) # Reverse the result back to ascending order
        print(quarterly_pct_change_df)

        # yearly_pct_change_df = merged_df[::-1].set_index('date').pct_change(periods=4)
        yearly_pct_change_df = merged_df[::-1].pct_change(periods=4)
        yearly_pct_change_df = yearly_pct_change_df[::-1].round(3) # Reverse the result back to ascending order
        print(yearly_pct_change_df)  

        annual_df = merged_df.copy()
        annual_df['year'] = pd.to_datetime(annual_df.index)
        annual_df['year'] = annual_df['year'].dt.year
        annual_df = annual_df.groupby('year').sum()
        annual_df = annual_df[::-1]
        annual_df.index.name = 'date'
        print(annual_df)

        annual_pct_change_df = annual_df[::-1].pct_change()
        annual_pct_change_df = annual_pct_change_df[::-1].round(3)
        print(annual_pct_change_df)

        # Create a new DataFrame for cumulative sums
        ttm_df = merged_df.copy()
        # Calculate cumulative sums for each row in reverse order
        for i in range(len(merged_df) - 4, -1, -1):
            ttm_df.iloc[i] = merged_df.iloc[i:i + 4].sum()
        # Set NaN values for the last three rows
        ttm_df.iloc[-3:] = None
        # Print the cumulative sum DataFrame
        print(ttm_df)

        # yearly_pct_change_df = merged_df[::-1].set_index('date').pct_change(periods=4)
        ttm_df_quarterly_pct_change = ttm_df[::-1].pct_change()
        ttm_df_quarterly_pct_change = ttm_df_quarterly_pct_change[::-1].round(3) # Reverse the result back to ascending order
        print(ttm_df_quarterly_pct_change)

        # yearly_pct_change_df = merged_df[::-1].set_index('date').pct_change(periods=4)
        ttm_df_yearly_pct_change = ttm_df[::-1].pct_change(periods=4)
        ttm_df_yearly_pct_change = ttm_df_yearly_pct_change[::-1].round(3) # Reverse the result back to ascending order
        print(ttm_df_yearly_pct_change)

        # earnings_df.set_index('date', inplace=True)
        print(earnings_df)
        # need to format this df so that date is the index

        tickers = [ticker.strip() for ticker in ticker.split(',')]
        end_date = date.today()
        start_date = end_date - timedelta(days=100 * 365)

        def get_historical_market_caps(tickers, start_date, end_date):
            combined_dfs = []  # Initialize an empty list to store DataFrames

            for ticker in tickers:
                df1 = pd.DataFrame(get_data(ticker, start_date, end_date))
                df1.drop(['adjclose', 'ticker'], axis=1, inplace=True)
                print(df1)

                # Define the API URL with the chosen ticker and date range for market capitalization
                url = f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{ticker}?from={start_date}&to={end_date}&apikey=6fe8c4680cf2609b34c3674e0a32720b"
                # url2 = f"https://financialmodelingprep.com/api/v4/shares_float?symbol={ticker}?from={start_date}&to={end_date}&apikey=6fe8c4680cf2609b34c3674e0a32720b"

                try:
                    response = requests.get(url)
                    response.raise_for_status()  # Raise an exception if the request fails
                    historical_market_caps = response.json()

                    # response2 = requests.get(url2)
                    # response2.raise_for_status()
                    # shares_outstanding = response2.json()

                    if historical_market_caps:
                        df2 = pd.DataFrame(historical_market_caps)                               
                        df2['date'] = pd.to_datetime(df2['date'])  # Convert 'date' column to datetime
                        df2.set_index('date', inplace=True)
                        df2.drop(columns='symbol', inplace=True)

                        print(df2)

                        combined_df = pd.concat([df1, df2], axis=1)  # Concatenate the DataFrames
                        combined_dfs.append(combined_df)  # Append to the list

                except requests.exceptions.RequestException as e:
                    print(f"Error fetching data for {ticker}: {e}")
                    continue  # Continue to the next ticker in case of an error

            return combined_dfs  # Return the list of DataFrames

        # Call the function and store the result in combined_dfs
        combined_dfs = get_historical_market_caps(tickers, start_date, end_date)

        # Concatenate all DataFrames in the list into one DataFrame
        if combined_dfs:
            combined_df = pd.concat(combined_dfs, ignore_index=False)
            combined_df.drop(combined_df.index[-1], inplace=True)
            combined_df['Implied Shares'] = (combined_df['marketCap'] / combined_df['close']).round(0)
            print(combined_df)
            # combined_df.to_excel(excel_writer, sheet_name='Daily Data', index=True)


            # data_table = pa.Table.from_pandas(combined_df)
            # fileName = f'{ticker}_daily_data.parquet'
            # filePath = os.path.join(folder_path, fileName)
            # pq.write_table(data_table, filePath)

        
        else:
            print("No historical market capitalization data available for the specified tickers.")




        
        # Save the Excel file.
        # excel_writer.close()
        # os.system(f'start excel "{excel_file_path}"')
        # print("Complete")
        

        # Replace NaN with None in DataFrames
        # merged_df = merged_df.fillna(value='0', inplace=True)
        # horizontal_df = horizontal_df.fillna(value='0', inplace=True)
        # quarterly_pct_change_df = quarterly_pct_change_df.fillna(value='0', inplace=True)
        # yearly_pct_change_df = yearly_pct_change_df.fillna(value='0', inplace=True)
        # annual_df = annual_df.fillna(value='0', inplace=True)
        # annual_pct_change_df = annual_pct_change_df.fillna(value='0', inplace=True)
        # ttm_df = ttm_df.fillna(value='0', inplace=True)
        # ttm_quarterly_pct_change = ttm_quarterly_pct_change.fillna(value='0', inplace=True)
        # ttm_yearly_pct_change = ttm_yearly_pct_change.fillna(value='0', inplace=True)
        # earnings_df = earnings_df.fillna(value='0', inplace=True)



        



        # Convert DataFrames to dictionaries
        merged_dict = merged_df.reset_index().to_dict(orient='records')
        horizontal_dict = horizontal_df.reset_index().to_dict(orient='records')
        quarterly_pct_change_dict = quarterly_pct_change_df.reset_index().to_dict(orient='records')
        yearly_pct_change_dict = yearly_pct_change_df.reset_index().to_dict(orient='records')
        annual_dict = annual_df.reset_index().to_dict(orient='records')
        annual_pct_change_dict = annual_pct_change_df.reset_index().to_dict(orient='records')
        ttm_dict = ttm_df.reset_index().to_dict(orient='records')
        ttm_quarterly_pct_change_dict = ttm_df_quarterly_pct_change.reset_index().to_dict(orient='records')
        ttm_yearly_pct_change_dict = ttm_df_yearly_pct_change.reset_index().to_dict(orient='records')
        earnings_dict = earnings_df.reset_index().to_dict(orient='records')



        
        # Assuming you have processed data in dictionaries
        data = {
            'merged_df': merged_dict,
            'horizontal_df': horizontal_dict,
            'quarterly_pct_change_df': quarterly_pct_change_dict,
            'yearly_pct_change_df': yearly_pct_change_dict,
            'annual_df': annual_dict,
            'annual_pct_change_df': annual_pct_change_dict,
            'ttm_df': ttm_dict,
            'ttm_df_quarterly_pct_change': ttm_quarterly_pct_change_dict,
            'ttm_df_yearly_pct_change': ttm_yearly_pct_change_dict,
            'earnings_df': earnings_dict,
        }

        return render_template('get_company_data.html', data=data)

    return render_template('get_company_data.html', data=None)


if __name__ == '__main__':
    app.run(debug=True)
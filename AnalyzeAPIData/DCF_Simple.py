import os
import openpyxl
import pandas as pd
from GetAPIData import GetHorizontalAndVertical  # for the ttm_df
from GetAPIData import GetFinancialStatementData
from GetAPIData import GetEarningsReportData
from AnalyzeAPIData import CAPM


def duplicate_excel_file(original_file, duplicate_file):
    # Open the original Excel file
    wb = openpyxl.load_workbook(original_file)

    # Get the current script's directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Create the path for the 'TickerData' folder, which is one directory above the current directory
    ticker_data_directory = os.path.join(current_directory, '..', 'TickerData')

    # Ensure the 'TickerData' folder exists (create it if it doesn't)
    os.makedirs(ticker_data_directory, exist_ok=True)

    # Define the full path for the duplicate file in the 'TickerData' folder
    duplicate_file_path = os.path.join(ticker_data_directory, duplicate_file)

    # Save a copy of the original Excel file with the new name in the 'TickerData' folder
    wb.save(duplicate_file_path)

    # print(f"Excel file duplicated successfully as '{duplicate_file_path}'.")

    return duplicate_file_path  # Return the file path to use later



def run_dcf_simple(ticker):
    # Get the current script's directory and locate the template in 'AnalyzeAPIData' folder
    current_directory = os.path.dirname(os.path.abspath(__file__))
    analyze_api_data_directory = current_directory if 'AnalyzeAPIData' in current_directory else os.path.join(current_directory, 'AnalyzeAPIData')

    original_file = os.path.join(analyze_api_data_directory, 'DCF_Simple_Template.xlsx')

    # Define the duplicate file name
    duplicate_file = f'{ticker}_DCF.xlsx'

    # Duplicate the Excel file
    duplicate_file_path = duplicate_excel_file(original_file, duplicate_file)

    # Retrieve the CAPM dataframe, unpacking the tuple
    capm_df, beta_df = CAPM.main(ticker)  # Unpack the returned tuple

    # Load the dataframes
    financial_statements_df = GetFinancialStatementData.collect_financial_statement_data(ticker)
    
    # Get the dictionary of dataframes from collect_horizontal_and_vertical
    horizontal_and_vertical_data = GetHorizontalAndVertical.collect_horizontal_and_vertical(financial_statements_df)

    # Access only the 'ttm_df' from the returned dictionary
    ttm_df = horizontal_and_vertical_data['ttm_df']
    # print(ttm_df)
    
    earnings_df = GetEarningsReportData.collect_earnings_data(ticker)
    earnings_df.set_index('fiscalDateEnding', inplace=True)
    # print(earnings_df)

    # Filter the necessary columns from ttm_df
    ttm_df_filtered = ttm_df[['revenue', 'freeCashFlow']].copy()
    # print(ttm_df_filtered)

    # Filter the necessary columns from financial_statements_df and earnings_df
    financial_statements_df_filtered = financial_statements_df[['weightedAverageShsOutDil', 'cashAndShortTermInvestments']].copy()
    earnings_df_filtered = earnings_df[['estimatedRevGrowth_yearly']].copy()
    # print(financial_statements_df_filtered)
    # print(earnings_df_filtered)

    # Merge the dataframes on the index (date)
    python_df = ttm_df_filtered.merge(financial_statements_df_filtered, on='date', how='inner')
    python_df = python_df.merge(earnings_df_filtered, left_on='date', right_index=True, how='outer')
    # print(python_df)

    # Reverse the order of the rows, moving bottom-most row to the top
    python_df = python_df.iloc[::-1]

    # Drop rows where all 5 columns (not index or 'date') are blank
    python_df.dropna(how='all', subset=['revenue', 'freeCashFlow', 'weightedAverageShsOutDil', 'cashAndShortTermInvestments', 'estimatedRevGrowth_yearly'], inplace=True)

    # Set 'date' as the index, rename it to 'fiscalDateEnding', and drop the old index column
    python_df.set_index('date', inplace=True)
    python_df.index.name = 'fiscalDateEnding'
    python_df.sort_index(ascending=False, inplace=True)

    # Manually rename columns
    python_df.rename(columns={
        'revenue': 'Revenue',
        'freeCashFlow': 'Free Cash Flow (FCF)',
        'weightedAverageShsOutDil': 'Shares Outstanding, Diluted',
        'cashAndShortTermInvestments': 'Cash and Equivalents',
        'estimatedRevGrowth_yearly': 'estimatedRevGrowth_yearly'
    }, inplace=True)
    
    # Export the merged dataframe to the duplicated Excel file in a sheet called 'Python'
    with pd.ExcelWriter(duplicate_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        python_df.to_excel(writer, sheet_name='Python', index=True)
        capm_df.to_excel(writer, sheet_name='WACC', index=True)
        beta_df.to_excel(writer, sheet_name='Beta', index=True)  # Optionally export the beta_df


    print(f"Merged dataframe exported successfully to '{duplicate_file_path}' in the 'Python' sheet.")
    os.startfile(duplicate_file_path)
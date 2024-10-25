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
    # print(python_df)
    # python_df = python_df.merge(earnings_df_filtered, left_on='date', right_index=True, how='left')
    python_df = python_df.merge(earnings_df_filtered, left_on='date', right_index=True, how='outer')
    # print(python_df)

    # Format the column names to be capitalized with spaces where appropriate
    # python_df.columns = python_df.columns.str.replace('_', ' ').str.title()
    # python_df = python_df.reset_index()
    # python_df = python_df.set_index('date')
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





# keep the 'fiscalDateEnding' data column, and then just rename it? set it as that, and rename what is currenty the index to 'reportedDateEnding'? 
# Becuase I want this to be in deliverable form, but with as little information as possible
# would be nice to better format the date columns (currently there are duplicates) that then get exported to the 'Python' sheet in the Excel file
# Still need to figure out how to set the parameter dates within the excel file, and format them, for row 1 of the template's sheet 
# And then, of course, need to get the derivative rates of change
# Good to keep the betas_df so as to keep an option that would be easy to change
# daily data: do % changes, and see where the disp. are (wihtin rounding errors) for price and market cap 











# I'll need earnings report data as well
# might need relativevaluations and horizontal/vertical analysis =
# read the result in python. have one for static, and one for dynamic inputs and assumptions
# calcualte the first derivatives/second of the growth rates? 

# get the earnings_df estimated revenue growth rate
# estimatedRevGrowth_yearly in earnings report df; get the most recent date after the fiscalDateEnding column 
# ttm_df for revenue, change name of row to 'Revenue'

# set parameter to be to determine what the current ttm quarter will be 





# get the most recent date for the ttm_df
# consider doing it on the earnings report date basis

# Let'start with 'Fiscal Year Ended'...take the most recent date in ttm_df. look in the earnings_df. get the next date that comes after that date in time, so
# that we get the next earnings report date. for the projection years, it will just be the year added + 1. for companies with peculiar quarter ended dates on 
# a bizare date like 27 or 28, can just format it down the line

# in the CAPM.py, add a row for terminal growth rate. add a parameter to toggle it on and off for display. or just add the row for terminal growth rate in this program.
# different year options. start with just 7 years. 

# from earnings report df, get the estimated value for the next quarter
# get the ttm_df yearly % change 
# estimatedRevGrowth_yearly 
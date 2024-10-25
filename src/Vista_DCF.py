# python src/Vista_DCF.py

import sys
import os
import time
import pandas as pd

program_start_time = time.time()

# Add the Vista_v0.03 directory to sys.path to ensure all submodules are accessible
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from AnalyzeAPIData import DCF_Simple
# import DCF_Simple

'''
from GetAPIData import GetFinancialStatementData
from GetAPIData import GetHorizontalAndVertical
from GetAPIData import GetEarningsReportData
from GetAPIData import GetEmployeeData
from GetAPIData import GetRevenueSegmentationData
from GetAPIData import GetMarketCapData
from GetAPIData import GetDailyData
from AnalyzeAPIData import BalanceSheetMetrics
from AnalyzeAPIData import RelativeValuations
from AnalyzeAPIData import FinancialStatementAnalysis
from AnalyzeAPIData import CAPM
'''

ticker = input("Enter the ticker symbol: ").upper()
# ticker = 'CURI'

def main():

    DCF_Simple.run_dcf_simple(ticker)
    # the next one shall be a parameter that allows for either flexible or static, based on what the parameter set in the CAPM calculation methodology
    # probably will want a prompt that asks if they even want to see the menu options to set the parameters, like for CAPM liabilities or just long term debt

    '''
    # Collect financial statement data
    financial_statements_df = GetFinancialStatementData.collect_financial_statement_data(ticker)

    # Perform horizontal and vertical analysis
    GetHorizontalAndVertical_results = GetHorizontalAndVertical.collect_horizontal_and_vertical(financial_statements_df)

    # Collect all dataframes to be saved into Excel sheets
    dataframes = {
        'Financial Statements': financial_statements_df,
        'Margins': GetHorizontalAndVertical_results['margins_df'],
        'Quarterly % Change': GetHorizontalAndVertical_results['quarterly_pct_change_df'],
        'Yearly % Change': GetHorizontalAndVertical_results['yearly_pct_change_df'],
        'Annual Aggregated': GetHorizontalAndVertical_results['annual_df'],
        'Annual % Change': GetHorizontalAndVertical_results['annual_pct_change_df'],
        'Trailing Twelve Months (TTM)': GetHorizontalAndVertical_results['ttm_df'],
        'TTM Margins': GetHorizontalAndVertical_results['ttm_margins'],
        'TTM Quarterly % Change': GetHorizontalAndVertical_results['ttm_df_quarterly_pct_change'],
        'TTM Yearly % Change': GetHorizontalAndVertical_results['ttm_df_yearly_pct_change'],
    }

    # Collect earnings report data
    earnings_df = GetEarningsReportData.collect_earnings_data(ticker)
    dataframes['Earnings Reports'] = earnings_df

    # Collect employee data
    employee_df = GetEmployeeData.collect_employee_data(ticker, financial_statements_df)
    dataframes['Employees'] = employee_df

    # Collect revenue segmentation data
    # these naming conventions need to be cleaned up 
    revenue_product_segmentation = GetRevenueSegmentationData.collect_revenue_product_segmentation(ticker)
    dataframes['Revenue Product Seg.'] = revenue_product_segmentation['revenue_product_segmentation_df']
    dataframes['Revenue Product % Total'] = revenue_product_segmentation['revenue_product_segmentation_pct_total']
    dataframes['Revenue Product % YoY'] = revenue_product_segmentation['revenue_product_segmentation_yoy']
    dataframes['Revenue Product % QoQ'] = revenue_product_segmentation['revenue_product_segmentation_qoq']

    revenue_geographic_segmentation = GetRevenueSegmentationData.collect_revenue_geographic_segmentation(ticker)
    dataframes['Revenue Geographic Seg.'] = revenue_geographic_segmentation['revenue_geographic_segmentation_df']
    dataframes['Revenue Geographic % Total'] = revenue_geographic_segmentation['revenue_geographic_segmentation_pct_total']
    dataframes['Revenue Geographic % YoY'] = revenue_geographic_segmentation['revenue_geographic_segmentation_yoy']
    dataframes['Revenue Geographic % QoQ'] = revenue_geographic_segmentation['revenue_geographic_segmentation_qoq']

    # Collect market cap data
    market_cap_data_df = GetMarketCapData.collect_market_cap_data(ticker)
    dataframes['Market Caps'] = market_cap_data_df

    # Collect daily price data
    daily_prices_df = GetDailyData.collect_daily_price_data(ticker)
    dataframes['Daily Prices'] = daily_prices_df
    


    balance_sheet_metrics_df = BalanceSheetMetrics.calculate_balance_sheet_metrics(
        market_cap_data_df,
        earnings_df,
        financial_statements_df
    )
    dataframes['Balance Sheet Metrics'] = balance_sheet_metrics_df

    # Perform relative valuations
    valuations_TTM_df = RelativeValuations.calculate_relative_valuations(
        market_cap_data_df=market_cap_data_df,
        earnings_df=earnings_df,
        ttm_df=GetHorizontalAndVertical_results['ttm_df'],
        balance_sheet_metrics_df=balance_sheet_metrics_df
    )
    dataframes['Relative Valuations'] = valuations_TTM_df


    financial_statement_analysis_df = FinancialStatementAnalysis.calculate_financial_statement_analysis(
        financial_statements_df=financial_statements_df,
        ttm_df=GetHorizontalAndVertical_results['ttm_df']
    )
    dataframes['Financial Analysis'] = financial_statement_analysis_df


    # Collect CAPM data
    CAPM_results, beta_results = CAPM.main(ticker)
    dataframes['CAPM'] = CAPM_results
    dataframes['Beta Analysis'] = beta_results
    


    # Define the output directory and ensure it exists
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'TickerData'))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define the output Excel file path
    output_file_path = os.path.join(output_dir, f"{ticker}_data.xlsx")

    # Write all collected DataFrames to the Excel file
    with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            df.to_excel(writer, sheet_name=sheet_name, index=True)


    # Automatically open the Excel file after saving
    os.startfile(output_file_path)
    
    print(f"Data collection and processing for {ticker} is complete.")
    print(f"Data has been saved to '{output_file_path}'.")



    # Display total runtime

    '''

    program_end_time = time.time()
    program_run_time = program_end_time - program_start_time 
    print(f"Total runtime: {program_run_time:.2f} seconds.")

if __name__ == "__main__":
    main()
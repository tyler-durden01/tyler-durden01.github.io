import pandas as pd
from GetAPIData import GetFinancialStatementData
from GetAPIData import GetEarningsReportData
from GetAPIData import GetMarketCapData

def calculate_balance_sheet_metrics(market_cap_data_df, earnings_df, financial_statements_df):
    # Convert the 'date' column in full_df and earnings_df to datetime for proper comparison
    market_cap_data_df = market_cap_data_df.reset_index()
    market_cap_data_df['date'] = pd.to_datetime(market_cap_data_df['date'])
    earnings_df = earnings_df.reset_index()
    earnings_df['date'] = pd.to_datetime(earnings_df['date'])

    # Sort both DataFrames by date
    market_cap_data_df = market_cap_data_df.sort_values('date')
    earnings_df = earnings_df.sort_values('date')

    # Create a list of dates from earnings_df for which "after market close" earnings are reported
    amc_dates = earnings_df.loc[earnings_df['time'] == 'amc', 'date'].tolist()

    # Merge full_df with earnings_df to find the closest earnings date
    market_cap_data_df = pd.merge_asof(
        market_cap_data_df,
        earnings_df[['date', 'fiscalDateEnding', 'time']],
        left_on='date',
        right_on='date',
        direction='backward',
        suffixes=('', '_closest')
    )

    # Ensure fiscalDateEnding in full_df is datetime
    market_cap_data_df['fiscalDateEnding'] = pd.to_datetime(market_cap_data_df['fiscalDateEnding'], errors='coerce')

    # Create a duplicate of full_df for adjusted earnings
    market_cap_data_df_adjustedEarnings = market_cap_data_df.copy()

    # Iterate over full_df_adjustedEarnings and apply the shift to fiscalDateEnding only for rows where the date is in amc_dates
    for i in range(1, len(market_cap_data_df_adjustedEarnings)):
        if market_cap_data_df_adjustedEarnings.loc[i, 'date'] in amc_dates:
            # Update the 'fiscalDateEnding' column with the value from the previous row
            market_cap_data_df_adjustedEarnings.loc[i, 'fiscalDateEnding'] = market_cap_data_df_adjustedEarnings.loc[i - 1, 'fiscalDateEnding']
            market_cap_data_df_adjustedEarnings.loc[i, 'time'] = market_cap_data_df_adjustedEarnings.loc[i - 1, 'time']

    # Convert 'date' in ttm_df to datetime just in case it wasn't done earlier
    financial_statements_df = financial_statements_df.reset_index()
    financial_statements_df['date'] = pd.to_datetime(financial_statements_df['date'], errors='coerce')

    # Merge full_df with ttm_df based on the fiscalDateEnding
    market_cap_data_df_unadjustedEarnings = pd.merge(
        market_cap_data_df,
        financial_statements_df[[
            'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 
            'totalCurrentAssets', 'otherCurrentAssets', 'shortTermDebt', 'longTermDebt', 'totalCurrentLiabilities', 
            'totalLiabilities', 'preferredStock', 'minorityInterest', 'totalEquity'
            ]],
        # payables and receivables? for quick ratio, etc? 
        left_on='fiscalDateEnding',
        right_on='date',
        how='left'
    )


    # Merge full_df_adjustedEarnings with ttm_df based on the fiscalDateEnding
    market_cap_data_df_adjustedEarnings = pd.merge(
        market_cap_data_df_adjustedEarnings,
        financial_statements_df[[
            'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 
            'totalCurrentAssets', 'otherCurrentAssets', 'shortTermDebt', 'longTermDebt', 'totalCurrentLiabilities', 
            'totalLiabilities', 'preferredStock', 'minorityInterest', 'totalEquity'
            ]],
        left_on='fiscalDateEnding',
        right_on='date',
        how='left'
    )

    # Set a parameter for which DataFrame the algorithm uses to calculate the ratios
    ratio_calculation_parameter = market_cap_data_df_adjustedEarnings  # Options are _adjustedEarnings or _unadjustedEarnings

    balance_sheet_metrics_df = ratio_calculation_parameter


    # valuations_TTM_df.rename(columns={'revenue': 'revenue_TTM'}, inplace=True)
    balance_sheet_metrics_df.drop(columns=['date_y'], inplace=True)
    balance_sheet_metrics_df.rename(columns={'date_x': 'date'}, inplace=True)
    # The below lines are more for formatting for presentation. Might need to put these further down the line
    balance_sheet_metrics_df['date'] = balance_sheet_metrics_df['date'].dt.strftime('%Y-%m-%d')
    balance_sheet_metrics_df['fiscalDateEnding'] = balance_sheet_metrics_df['fiscalDateEnding'].dt.strftime('%Y-%m-%d')
    balance_sheet_metrics_df = balance_sheet_metrics_df.set_index('date')


    # Calculate valuation ratios
    # no longer need 1000000
    balance_sheet_metrics_df['enterpriseValue_simple'] = balance_sheet_metrics_df['marketCap'] + (balance_sheet_metrics_df['shortTermDebt'] + balance_sheet_metrics_df['longTermDebt']) - balance_sheet_metrics_df['cashAndShortTermInvestments'] 
    balance_sheet_metrics_df['enterpriseValue'] = balance_sheet_metrics_df['enterpriseValue_simple'] + (balance_sheet_metrics_df['preferredStock'] + balance_sheet_metrics_df['minorityInterest'])
    
    # balance_sheet_metrics_df['equityValue'] = balance_sheet_metrics_df['']
    # cash and cash equivalents for enterprise value, but balance sheet figure for equity value

    # EV/EBITDA, EV/EBIT, EV/FCF, or EV/Sales for
        # market value of debt is needed
    # EV is market value; equity value is financial statement value?
    # fully diluted market cap? 

    return balance_sheet_metrics_df


# Need to add the duplicate of this one, and make the sheet_NTM (realized and estimated)

# Enterprise value

# from here, ttm/merged_df analysis for current ratio, d/e, quick ratio, see financial stattement analysis course for inpir, along with FMP docs

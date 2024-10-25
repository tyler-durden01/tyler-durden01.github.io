import pandas as pd
from GetAPIData import GetFinancialStatementData
from GetAPIData import GetEarningsReportData
from GetAPIData import GetMarketCapData
from AnalyzeAPIData import BalanceSheetMetrics

def calculate_relative_valuations(market_cap_data_df, earnings_df, ttm_df, balance_sheet_metrics_df):
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
    ttm_df = ttm_df.reset_index()
    ttm_df['date'] = pd.to_datetime(ttm_df['date'], errors='coerce')

    balance_sheet_metrics_df = balance_sheet_metrics_df.reset_index()
    balance_sheet_metrics_df['date'] = pd.to_datetime(balance_sheet_metrics_df['date'], errors='coerce')

    
    # Merge full_df with ttm_df based on the fiscalDateEnding
    market_cap_data_df_unadjustedEarnings = pd.merge(
        market_cap_data_df,
        ttm_df[['date', 'revenue', 'EBITDA', 'freeCashFlow', 'FCFsimple', 'operatingIncome', 'netIncome']],
        left_on='fiscalDateEnding',
        right_on='date',
        how='left'
    ).merge(
        balance_sheet_metrics_df[[
            'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 
            'totalCurrentAssets', 'otherCurrentAssets', 'shortTermDebt', 'longTermDebt', 'totalCurrentLiabilities', 
            'totalLiabilities', 'preferredStock', 'minorityInterest', 'totalEquity',
            'enterpriseValue_simple', 'enterpriseValue'
            ]],
        left_on='date_x',
        right_on='date', 
        how='left'
    )
    

    # Merge full_df_adjustedEarnings with ttm_df based on the fiscalDateEnding
    market_cap_data_df_adjustedEarnings = pd.merge(
        market_cap_data_df_adjustedEarnings,
        ttm_df[['date', 'revenue', 'EBITDA', 'freeCashFlow', 'FCFsimple', 'operatingIncome','netIncome']],
        left_on='fiscalDateEnding',
        right_on='date',
        how='left'
    ).merge(
        balance_sheet_metrics_df[[
            'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 
            'totalCurrentAssets', 'otherCurrentAssets', 'shortTermDebt', 'longTermDebt', 'totalCurrentLiabilities', 
            'totalLiabilities', 'preferredStock', 'minorityInterest', 'totalEquity',
            'enterpriseValue_simple', 'enterpriseValue'
            ]],
        left_on='date_x',
        right_on='date', 
        how='left'
    )
    
    
    # Set a parameter for which DataFrame the algorithm uses to calculate the ratios
    ratio_calculation_parameter = market_cap_data_df_adjustedEarnings  # Options are _adjustedEarnings or _unadjustedEarnings

    valuations_TTM_df = ratio_calculation_parameter


    valuations_TTM_df.drop(columns=['date_y'], inplace=True)
    valuations_TTM_df.drop(columns=['date_x'], inplace=True)
    valuations_TTM_df['date'] = valuations_TTM_df['date'].dt.strftime('%Y-%m-%d')
    valuations_TTM_df['fiscalDateEnding'] = valuations_TTM_df['fiscalDateEnding'].dt.strftime('%Y-%m-%d')
    valuations_TTM_df = valuations_TTM_df.set_index('date')


    # valuations_TTM_df.rename(columns={'revenue': 'revenue_TTM'}, inplace=True)


    


    # Calculate valuation ratios
    # no longer need 1000000
    valuations_TTM_df['P/S'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['revenue']
    valuations_TTM_df['P/EBITDA'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['EBITDA']
    valuations_TTM_df['P/FCF'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['freeCashFlow']
    valuations_TTM_df['P/FCFsimple'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['FCFsimple']
    valuations_TTM_df['P/OpIncome'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['operatingIncome']
    valuations_TTM_df['P/E'] = valuations_TTM_df['marketCap'] / valuations_TTM_df['netIncome']
    valuations_TTM_df['EnV/EBITDA'] = valuations_TTM_df['enterpriseValue'] / valuations_TTM_df['EBITDA']
    valuations_TTM_df['EnV_simple/EBITDA'] = valuations_TTM_df['enterpriseValue_simple'] / valuations_TTM_df['EBITDA']
    valuations_TTM_df['EnV/OpIncome'] = valuations_TTM_df['enterpriseValue'] / valuations_TTM_df['operatingIncome']
    valuations_TTM_df['EnV_simple/OpIncome'] = valuations_TTM_df['enterpriseValue_simple'] / valuations_TTM_df['operatingIncome']
    valuations_TTM_df['EnV/FCF'] = valuations_TTM_df['enterpriseValue'] / valuations_TTM_df['freeCashFlow']
    valuations_TTM_df['EnV/FCFsimple'] = valuations_TTM_df['enterpriseValue'] / valuations_TTM_df['FCFsimple']
    valuations_TTM_df['EnV_simple/FCF'] = valuations_TTM_df['enterpriseValue_simple'] / valuations_TTM_df['freeCashFlow']
    valuations_TTM_df['EnV_simple/FCFsimple'] = valuations_TTM_df['enterpriseValue_simple'] / valuations_TTM_df['FCFsimple']
    valuations_TTM_df['EnV/Sales'] = valuations_TTM_df['enterpriseValue'] / valuations_TTM_df['revenue']
    valuations_TTM_df['EnV_simple/Sales'] = valuations_TTM_df['enterpriseValue_simple'] / valuations_TTM_df['revenue']
    


    return valuations_TTM_df


# Need to add the duplicate of this one, and make the sheet_NTM (realized and estimated)

# Enterprise value

# from here, ttm/merged_df analysis for current ratio, d/e, quick ratio, see financial stattement analysis course for inpir, along with FMP docs
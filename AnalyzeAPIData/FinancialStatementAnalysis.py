import pandas as pd
from GetAPIData import GetFinancialStatementData
from GetAPIData import GetHorizontalAndVertical

financial_statement_analysis_df = pd.DataFrame()

def calculate_financial_statement_analysis(financial_statements_df, ttm_df):

    financial_statement_analysis_df['ROE'] = ttm_df['netIncome'] / financial_statements_df['totalEquity']
    financial_statement_analysis_df['ROE_EBITDA'] = ttm_df['EBITDA'] / financial_statements_df['totalEquity']
    financial_statement_analysis_df['ROE_EBIT'] = ttm_df['operatingIncome'] / financial_statements_df['totalEquity']
    financial_statement_analysis_df['ROE_FCF'] = ttm_df['freeCashFlow'] / financial_statements_df['totalEquity']
    financial_statement_analysis_df['ROE_FCFsimple'] = ttm_df['FCFsimple'] / financial_statements_df['totalEquity']
    
    financial_statement_analysis_df['ROA'] = ttm_df['netIncome'] / financial_statements_df['totalAssets']
    financial_statement_analysis_df['ROA_EBITDA'] = ttm_df['EBITDA'] / financial_statements_df['totalAssets']
    financial_statement_analysis_df['ROA_EBIT'] = ttm_df['operatingIncome'] / financial_statements_df['totalAssets']
    financial_statement_analysis_df['ROA_FCF'] = ttm_df['freeCashFlow'] / financial_statements_df['totalAssets']
    financial_statement_analysis_df['ROA_FCFsimple'] = ttm_df['FCFsimple'] / financial_statements_df['totalAssets']

    financial_statement_analysis_df['ROC'] = ttm_df['netIncome'] / ((financial_statements_df['totalCurrentAssets'] - financial_statements_df['otherCurrentAssets']) + financial_statements_df['propertyPlantEquipmentNet'])
    financial_statement_analysis_df['ROIC'] = ttm_df['NOPAT'] / (financial_statements_df['propertyPlantEquipmentNet'] + financial_statements_df['NWC_simple'] + financial_statements_df['goodwill'])
    

    financial_statement_analysis_df['CurrentRatio_simple'] = financial_statements_df['totalCurrentAssets'] / financial_statements_df['totalCurrentLiabilities']
    financial_statement_analysis_df['CL/TL'] = financial_statements_df['totalCurrentLiabilities'] / financial_statements_df['totalLiabilities']
    financial_statement_analysis_df['LTL/TL'] = 1 - financial_statement_analysis_df['CL/TL']
    financial_statement_analysis_df['L/E'] = financial_statements_df['totalLiabilities'] / financial_statements_df['totalEquity']
    financial_statement_analysis_df['LTD/E'] = financial_statements_df['longTermDebt'] / financial_statements_df['totalEquity']

    # simple quick ratio
    # MISSING acquired intangibles; will need the change row over row to compute that
    # (average) invested capital 
    # ROCE
    # cash per share? mcap to cash?
    # see balance sheet metrics to get more ideas of the inputted variables, at least
    # invested capital; breakdown of how the invested capital comes about
    # NWC (the other methods)
    # should maybe do my own current asset calculations
    # how is depreciation netted against PP&E?
    # print(financial_statements_df)
    # EV to revenue
    # price to book
    # peg 
    # [
            # 'date', 'cashAndCashEquivalents', 'shortTermInvestments', 'cashAndShortTermInvestments', 
            # 'totalCurrentAssets', 'otherCurrentAssets', 'shortTermDebt', 'longTermDebt', 'totalCurrentLiabilities', 
            # 'totalLiabilities', 'preferredStock', 'minorityInterest', 'totalEquity'
            # ]

    return financial_statement_analysis_df
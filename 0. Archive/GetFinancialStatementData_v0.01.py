import requests
import pandas as pd
from config import api_key, base_url, api_params

def collect_financial_statement_data(ticker):
    # Define the endpoints for financial statements
    income_statement_endpoint = f'income-statement/{ticker}'
    balance_sheet_endpoint = f'balance-sheet-statement/{ticker}'
    cash_flow_statement_endpoint = f'cash-flow-statement/{ticker}'

    # Make API requests
    income_data = fetch_data(income_statement_endpoint, api_params)
    balance_sheet_data = fetch_data(balance_sheet_endpoint, api_params)
    cash_flow_data = fetch_data(cash_flow_statement_endpoint, api_params)

    # Process the data into DataFrames
    income_df = process_income_statement(income_data)
    print(income_df)
    balance_sheet_df = process_balance_sheet(balance_sheet_data)
    print(balance_sheet_df)
    # problem: there is no balance sheet for july 2018, which is pre-IPO
    cash_flow_df = process_cash_flow_statement(cash_flow_data)
    print(cash_flow_df)
    

    # Merge DataFrames on the 'date' column
    financial_statements_df = merge_data(income_df, balance_sheet_df, cash_flow_df)

    # Add additional calculated columns
    financial_statements_df['EBITDA'] = financial_statements_df['operatingIncome'] + financial_statements_df['depreciationAndAmortization']
    financial_statements_df['FCFsimple'] = financial_statements_df['EBITDA'] + financial_statements_df['capitalExpenditure']
    print(financial_statements_df)

    # Convert columns to numeric and adjust scale    
    numeric_columns = financial_statements_df.columns.drop('date')

    # Fill missing values in numeric columns before applying conversion
    # ## financial_statements_df[numeric_columns] = financial_statements_df[numeric_columns].fillna(0).apply(pd.to_numeric, errors='coerce')
    # Apply numeric conversion to the selected columns
    ## financial_statements_df.fillna(0, inplace=True)

    # ## financial_statements_df[numeric_columns] = financial_statements_df[numeric_columns].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    ## for col in numeric_columns:
        ## financial_statements_df[col] = pd.to_numeric(financial_statements_df[col], errors='coerce')

    
    #### numeric_columns = numeric_columns.apply(pd.to_numeric, errors='coerce')
    #### financial_statements_df[numeric_columns] = financial_statements_df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    financial_statements_df.set_index('date', inplace=True)
    # financial_statements_df = financial_statements_df / 1000000  # Convert to millions
    # financial_statements_df = financial_statements_df.round(0)

    return financial_statements_df


def fetch_data(endpoint, params):
    response = requests.get(base_url + endpoint, params=api_params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data from {endpoint}")
        return []


def process_income_statement(data):
    return pd.DataFrame(data)[[
        'date', 'revenue', 'grossProfit', 'generalAndAdministrativeExpenses', 
        'sellingAndMarketingExpenses', 'sellingGeneralAndAdministrativeExpenses',
        'researchAndDevelopmentExpenses', 'otherExpenses', 'operatingIncome',
        'interestExpense', 'interestIncome', 'incomeTaxExpense', 'netIncome',
        'weightedAverageShsOut', 'weightedAverageShsOutDil'
    ]]


def process_balance_sheet(data):
    return pd.DataFrame(data)[[
        'date', 'cashAndCashEquivalents', 'shortTermInvestments', 
        'cashAndShortTermInvestments', 'netReceivables', 'inventory', 
        'otherCurrentAssets', 'totalCurrentAssets', 'propertyPlantEquipmentNet',
        'goodwill', 'intangibleAssets', 'longTermInvestments', 
        'totalNonCurrentAssets', 'totalAssets', 'accountPayables', 
        'shortTermDebt', 'totalCurrentLiabilities', 'longTermDebt', 
        'totalNonCurrentLiabilities', 'totalLiabilities', 'capitalLeaseObligations', 
        'preferredStock', 'commonStock', 'minorityInterest', 'retainedEarnings', 'totalEquity'
    ]]


def process_cash_flow_statement(data):
    return pd.DataFrame(data)[[
        'date', 'freeCashFlow', 'accountsReceivables', 'accountsPayables', 
        'inventory', 'depreciationAndAmortization', 'stockBasedCompensation',
        'deferredIncomeTax', 'changeInWorkingCapital', 'otherWorkingCapital', 
        'netChangeInCash', 'netCashProvidedByOperatingActivities', 
        'capitalExpenditure', 'investmentsInPropertyPlantAndEquipment', 
        'acquisitionsNet', 'purchasesOfInvestments', 'netCashUsedForInvestingActivites', 
        'debtRepayment', 'commonStockIssued', 'commonStockRepurchased', 
        'dividendsPaid', 'netCashUsedProvidedByFinancingActivities', 
        'effectOfForexChangesOnCash', 'netChangeInCash', 'cashAtEndOfPeriod',
        'cashAtBeginningOfPeriod'
    ]]


def merge_data(income_df, balance_sheet_df, cash_flow_df):
    financial_statements_df = pd.merge(income_df, balance_sheet_df, on='date', how='outer')
    financial_statements_df = pd.merge(financial_statements_df, cash_flow_df, on='date', how='outer')
    return financial_statements_df
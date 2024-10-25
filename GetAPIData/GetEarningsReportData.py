import requests
import pandas as pd
from config import api_key, base_url, api_params


def collect_earnings_data(ticker):
    # Define the endpoints for financial statements
    earnings_endpoint = f'historical/earning_calendar/{ticker}'
    earnings_data = fetch_data(earnings_endpoint, params=api_params)
    earnings_df = pd.DataFrame(earnings_data)

    # Rev calculations
    earnings_df['RevPctBeat'] = earnings_df['revenue'] / earnings_df['revenueEstimated'] - 1

    earnings_df['estimatedRevGrowth_yearly'] = earnings_df['revenueEstimated'] / earnings_df['revenue'].shift(-4) - 1
    earnings_df['estimatedRevGrowth_quarterly'] = earnings_df['revenueEstimated'] / earnings_df['revenue'].shift(-1) - 1

    earnings_df['estimatedRev_PctChange_y/y'] =  earnings_df['revenueEstimated'] / earnings_df['revenueEstimated'].shift(-4) - 1
    earnings_df['estimatedRev_PctChange_q/q'] =  earnings_df['revenueEstimated'] / earnings_df['revenueEstimated'].shift(-1) - 1

    earnings_df['actualRev_PctChange_y/y'] = earnings_df['revenue'] / earnings_df['revenue'].shift(-4) - 1
    earnings_df['actualRev_PctChange_q/q'] = earnings_df['revenue'] / earnings_df['revenue'].shift(-1) - 1


    # EPS calculations
    earnings_df['EPSPctBeat'] = earnings_df['eps'] / earnings_df['epsEstimated'] - 1 
    earnings_df['estimatedEPSGrowth_yearly'] = earnings_df['epsEstimated'] / earnings_df['eps'].shift(-4) - 1
    earnings_df['estimatedEPSGrowth_quarterly'] = earnings_df['epsEstimated'] / earnings_df['eps'].shift(-1) - 1

    earnings_df['estimatedEPS_PctChange_y/y'] =  earnings_df['epsEstimated'] / earnings_df['epsEstimated'].shift(-4) - 1
    earnings_df['estimatedEPS_PctChange_q/q'] =  earnings_df['epsEstimated'] / earnings_df['epsEstimated'].shift(-1) - 1

    earnings_df['actualEPS_PctChange_y/y'] = earnings_df['eps'] / earnings_df['eps'].shift(-4) - 1
    earnings_df['actualEPS_PctChange_q/q'] = earnings_df['eps'] / earnings_df['eps'].shift(-1) - 1



    earnings_df = earnings_df.drop(columns=['symbol'])
    earnings_df = earnings_df.set_index('date')  # Set 'date' column as the index
    # missing notes on guidance and forward-looking estimated revisions. might not really need that data, actually
    # notice that the EPS and EPSestimated figures are completely off. No idea where they come from.
    # oh wait. Adj EPS???? non0GAAP??? What is this now???
    # CAN DO THE SAME % CHANGES FOR EPS NOW?????
    # Better way to code this? With 14 individual calculations? 
    # re-order the columns, too
    
    return earnings_df

def fetch_data(endpoint, params):
    response = requests.get(base_url + endpoint, params=api_params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data from {endpoint}")
        return []


# Only reason det fetch_data stays for now is because it might be needed to put into the config file
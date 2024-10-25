import requests
import pandas as pd
### from config import api_key
### the below will be commented out, and the above will be enacted
api_key = '6fe8c4680cf2609b34c3674e0a32720b'

def collect_mergers_and_acquisitions_data():
    # Initialize an empty list to store data for all pages
    all_data = []

    # Loop through pages 0 to 10
    for page in range(0, 11):
        # Construct the URL for the current page
        url = f'https://financialmodelingprep.com/api/v4/mergers-acquisitions-rss-feed?page={page}&apikey={api_key}'

        # Send the request
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # print(f"Data from page {page}: {data}")

            # Add the data from the current page to the list
            all_data.extend(data)
        else:
            print(f"Failed to fetch data on page {page}. Status code: {response.status_code}")
            break  # Optionally break the loop if a page fails

    # Convert the combined data to a DataFrame
    MandA_df = pd.DataFrame(all_data)

    # Drop the columns that are not currently needed (example code, you can adjust as needed)
    ## MandA_df = MandA_df.drop(['companyName', 'source', 'symbol'], axis=1)
    ## MandA_df = MandA_df[['periodOfReport', 'filingDate', 'acceptanceTime', 'formType', 'cik', 'employeeCount']]
    ## MandA_df = MandA_df.set_index('periodOfReport')
    
    ### outputFileName = f'mergers_acquis_df.xlsx'
    ### MandA_df.to_excel(outputFileName, index=True, sheet_name='Mergers_Acquisitions')


    ### print(MandA_df)
    return MandA_df


### This below will also be commented out
collect_mergers_and_acquisitions_data()



# This seems lacking and incomplete data. Also, the valuations, they are nowhere
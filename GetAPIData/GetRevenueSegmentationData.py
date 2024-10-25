import requests
import pandas as pd
from config import api_key, base_url, api_params

def collect_revenue_product_segmentation(ticker):
    url_product = f'https://financialmodelingprep.com/api/v4/revenue-product-segmentation?symbol={ticker}&structure=flat'

    response = requests.get(url_product, params=api_params)
    if response.status_code == 200:
        data = response.json()

        # Extract data from the list of dictionaries and restructure it
        flattened_data = []
        for item in data:
            date = list(item.keys())[0]
            values = list(item.values())[0]
            values['date'] = date  # Add the date as a new key 'date'
            flattened_data.append(values)

        # Create a Pandas DataFrame from the flattened data
        revenue_product_segmentation_df = pd.DataFrame(flattened_data)
        revenue_product_segmentation_df.index = revenue_product_segmentation_df['date']
        revenue_product_segmentation_df = revenue_product_segmentation_df.drop(columns=['date'])

        # Calculate % of total
        revenue_product_segmentation_pct_total = revenue_product_segmentation_df.div(revenue_product_segmentation_df.sum(axis=1), axis=0)

        # Reverse the dataframe so the oldest date is at the top for proper % change calculations
        reversed_df = revenue_product_segmentation_df.iloc[::-1]

        # Calculate % change year over year
        revenue_product_segmentation_yoy = reversed_df.pct_change(periods=4)  # Calculating YoY % change

        # Calculate % change quarter over quarter
        revenue_product_segmentation_qoq = reversed_df.pct_change(periods=1)  # Calculating QoQ % change

        # Reverse the % change dataframes back to match the original date order (most recent first)
        revenue_product_segmentation_yoy = revenue_product_segmentation_yoy.iloc[::-1]
        revenue_product_segmentation_qoq = revenue_product_segmentation_qoq.iloc[::-1]

        return {
            'revenue_product_segmentation_df': revenue_product_segmentation_df,
            'revenue_product_segmentation_pct_total': revenue_product_segmentation_pct_total,
            'revenue_product_segmentation_yoy': revenue_product_segmentation_yoy,
            'revenue_product_segmentation_qoq': revenue_product_segmentation_qoq
        }

    else:
        print(f"Failed to retrieve product segmentation data. Status code: {response.status_code}")
        return None



def collect_revenue_geographic_segmentation(ticker):
    url_geographic = f'https://financialmodelingprep.com/api/v4/revenue-geographic-segmentation?symbol={ticker}&structure=flat'

    response = requests.get(url_geographic, params=api_params)
    if response.status_code == 200:
        data = response.json()

        # Extract data from the list of dictionaries and restructure it
        flattened_data = []
        for item in data:
            date = list(item.keys())[0]
            values = list(item.values())[0]
            values['date'] = date  # Add the date as a new key 'date'
            flattened_data.append(values)

        # Create a Pandas DataFrame from the flattened data
        revenue_geographic_segmentation_df = pd.DataFrame(flattened_data)
        revenue_geographic_segmentation_df.index = revenue_geographic_segmentation_df['date']
        revenue_geographic_segmentation_df = revenue_geographic_segmentation_df.drop(columns=['date'])

        # Calculate % of total
        revenue_geographic_segmentation_pct_total = revenue_geographic_segmentation_df.div(revenue_geographic_segmentation_df.sum(axis=1), axis=0)

        # Reverse the dataframe so the oldest date is at the top for proper % change calculations
        reversed_df = revenue_geographic_segmentation_df.iloc[::-1]

        # Calculate % change year over year
        revenue_geographic_segmentation_yoy = reversed_df.pct_change(periods=4)  # Calculating YoY % change

        # Calculate % change quarter over quarter
        revenue_geographic_segmentation_qoq = reversed_df.pct_change(periods=1)  # Calculating QoQ % change

        # Reverse the % change dataframes back to match the original date order (most recent first)
        revenue_geographic_segmentation_yoy = revenue_geographic_segmentation_yoy.iloc[::-1]
        revenue_geographic_segmentation_qoq = revenue_geographic_segmentation_qoq.iloc[::-1]

        return {
            'revenue_geographic_segmentation_df': revenue_geographic_segmentation_df,
            'revenue_geographic_segmentation_pct_total': revenue_geographic_segmentation_pct_total,
            'revenue_geographic_segmentation_yoy': revenue_geographic_segmentation_yoy,
            'revenue_geographic_segmentation_qoq': revenue_geographic_segmentation_qoq
        }

    else:
        print(f"Failed to retrieve geographic segmentation data. Status code: {response.status_code}")
        return None








# def get_sales_by_product_line():
    # Define the product line you want to get sales data for
    # product_line = 'electronics'  # Replace with your desired product line

    # Make a GET request to the API
    # url = f'{base_url}/income-statement/{product_line}?apikey={api_key}'    


# if __name__ == "__main__":
    # get_sales_by_product_line()
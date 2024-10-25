from datetime import timedelta
from datetime import date
import pandas as pd

# tickers = [ticker.strip() for ticker in ticker.split(',')]


api_key = '6fe8c4680cf2609b34c3674e0a32720b'


# Base URL for financial modeling prep API
base_url = 'https://financialmodelingprep.com/api/v3/'


api_params = {
        'apikey': api_key,
        'period': 'quarter'
    }


# Function to append summary statistics to each dataframe
def config_append_summary_statistics(dataframe):
    # Calculate statistics
    # Drop NaN values for cleaner analysis
    # col_data = df[column].dropna()

    dataframe = dataframe.select_dtypes(include='number')

    stats = pd.DataFrame({
        'mean': dataframe.mean(),
        'mean_values_>0': dataframe[dataframe > 0].mean(),
        'median': dataframe.median(),
        'median_values_>0': dataframe[dataframe > 0].median(),
        'stdev_pop': dataframe.std(ddof=0),
        'stdev_sample': dataframe.std(),
        'std_values_>0': dataframe[dataframe > 0].std(ddof=1),
        # 'CHECK_std_values_>0': dataframe[dataframe > 0].std(),
        'max': dataframe.max(),
        'min': dataframe.min(),
        'min_values_>0': dataframe[dataframe > 0].min(),
    }).T

    # Append statistics to the dataframe
    # stats.index = ['Mean', 'Median', 'Max', 'Min', 'St_Dev']
    # stats = stats.set_index(stats.columns[0], inplace=True)
    return pd.concat([dataframe, stats])


end_date = date.today()
# end_date = date(year=2024, month=8, day=30)
start_date = end_date - timedelta(days=100 * 365) 
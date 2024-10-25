import os
import pandas as pd
import pyarrow.parquet as pq

# ticker = input('Enter ticker symbol: ')
ticker = 'ASML'

path = r'C:\Users\Kyle Jennings\OneDrive - Arcadian Holdings LLC\3.  Arcadian Financial\4.  Investment Management\Software Programs\Financial_Data'
# path = r'C:\Users\ktjje\OneDrive - Arcadian Holdings LLC\3.  Arcadian Financial\4.  Investment Management\Software Programs\Financial_Data'
path = os.path.join(path, f'{ticker}_Financial_Data')


date = '2017-01-01'

yearly_pct_change_data_file = f'{ticker}_yearly_pct_change_data.parquet'
yearly_pct_change_data_path = os.path.join(path, yearly_pct_change_data_file)
yearly_pct_change_data_table = pq.read_table(yearly_pct_change_data_path)
yearly_pct_change_data_df = yearly_pct_change_data_table.to_pandas()
# Filter rows where the index (axis) is on or after January 1, 2017
yearly_pct_change_data_filtered_df = yearly_pct_change_data_df[yearly_pct_change_data_df.index >= date]
yearly_pct_change_data_filtered_df = yearly_pct_change_data_filtered_df[['revenue', 'grossProfit']]
print(yearly_pct_change_data_filtered_df)


margins_data_file = f'{ticker}_margins_data.parquet'
margins_data_path = os.path.join(path, margins_data_file)
margins_data_table = pq.read_table(margins_data_path)
margins_data_df = margins_data_table.to_pandas()
# Filter rows where the index (axis) is on or after January 1, 2017
margins_data_filtered_df = margins_data_df[margins_data_df.index >= date]
margins_data_filtered_df = margins_data_filtered_df[['grossProfit', 'sellingGeneralAndAdministrativeExpenses', 'operatingIncome', 'netIncome', 'depreciationAndAmortization', 'stockBasedCompensation', 'capitalExpenditure', 'acquisitionsNet', ]]
# consider others like stocked based comp, capex, etc.
print(margins_data_filtered_df)



# correlation between rev, o/i, and CFFO? Do a study? Or how the fuck can I map it out?


# avg of rev growth and avg of margins
# Use os.listdir to get all files in the directory with .parquet extension
# input_files = [os.path.join(path, filename) for filename in os.listdir(path) if filename.endswith('.parquet')]


# for file in input_files:
    # table = pq.read_table(file)
    # df = table.to_pandas()

    # Extract the sheet name from the file name (remove ".parquet" extension)
    # sheet_name = os.path.splitext(os.path.basename(file))[0]
    # print(f'File: {file}')
    # print(f'Data for {sheet_name}:')
    # print(df)









    # row_avg = df.mean(axis=1)
    # print('All Time Mean:')
    # print(row_avg)

    # row_avg_recent = df.iloc[:, -5:].mean(axis=1)
    # print('Past 5 Years Mean')
    # print(row_avg_recent)

    # You can iterate through each row and calculate the mean for each row
    # for index, row in df.iterrows():
    #     mean_value = row.mean()
    #     print(f'Mean for Row {index}: {mean_value}')

    # Calculate and print the mean and median for each row using Pandas
    # mean_values = df.mean(axis=1)
    # median_values = df.median(axis=1)

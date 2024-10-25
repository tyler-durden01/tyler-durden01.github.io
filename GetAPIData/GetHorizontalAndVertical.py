import pandas as pd

# need to adjust horizontal and vertical for the balance sheet figures.
# need to add % changes for the margins, and CAGRs for the growth rates

# Function to append summary statistics to each dataframe
def append_summary_statistics(df):
    # Calculate statistics
    stats = pd.DataFrame({
        'mean': df.mean(),
        'median': df.median(),
        'max': df.max(),
        'min': df.min(),
        'std': df.std()
    }).T

    # Append statistics to the dataframe
    stats.index = ['Mean', 'Median', 'Max', 'Min', 'St_Dev']
    return pd.concat([df, stats])


def collect_horizontal_and_vertical(financial_statements_df):
    # Perform the operations after financial_statements_df = financial_statements_df.round(0)

    # Margins analysis: Divide by revenue to standardize
    margins_df = financial_statements_df.div(financial_statements_df['revenue'], axis=0)
    margins_df = margins_df.round(3)

    # Quarterly % changes (in descending order)
    quarterly_pct_change_df = financial_statements_df[::-1].pct_change()
    quarterly_pct_change_df = quarterly_pct_change_df[::-1].round(3)

    # Yearly % changes (with 4 quarters difference)
    yearly_pct_change_df = financial_statements_df[::-1].pct_change(periods=4)
    yearly_pct_change_df = yearly_pct_change_df[::-1].round(3)

    # Annual aggregation
    annual_df = financial_statements_df.copy()
    annual_df['year'] = pd.to_datetime(annual_df.index)
    annual_df['year'] = annual_df['year'].dt.year
    annual_df = annual_df.groupby('year').sum()
    annual_df = annual_df[::-1]
    annual_df.index.name = 'date'

    # Annual % changes
    annual_pct_change_df = annual_df[::-1].pct_change()
    annual_pct_change_df = annual_pct_change_df[::-1].round(3)

    # Trailing twelve months (TTM) calculations
    ttm_df = financial_statements_df.copy()
    for i in range(len(financial_statements_df) - 4, -1, -1):
        ttm_df.iloc[i] = financial_statements_df.iloc[i:i + 4].sum()
    ttm_df.iloc[-3:] = None

    # Margins analysis for TTM
    ttm_margins = ttm_df.div(ttm_df['revenue'], axis=0)
    ttm_margins = ttm_margins.round(3)

    # TTM Quarterly % changes
    ttm_df_quarterly_pct_change = ttm_df[::-1].pct_change()
    ttm_df_quarterly_pct_change = ttm_df_quarterly_pct_change[::-1].round(3)

    # TTM Yearly % changes
    ttm_df_yearly_pct_change = ttm_df[::-1].pct_change(periods=4)
    ttm_df_yearly_pct_change = ttm_df_yearly_pct_change[::-1].round(3)

    # Append summary statistics to each dataframe
    # margins_df = append_summary_statistics(margins_df)
    quarterly_pct_change_df = append_summary_statistics(quarterly_pct_change_df)
    yearly_pct_change_df = append_summary_statistics(yearly_pct_change_df)
    # annual_df = append_summary_statistics(annual_df)
    annual_pct_change_df = append_summary_statistics(annual_pct_change_df)
    # ttm_df = append_summary_statistics(ttm_df)
    ttm_margins = append_summary_statistics(ttm_margins)
    ttm_df_quarterly_pct_change = append_summary_statistics(ttm_df_quarterly_pct_change)
    ttm_df_yearly_pct_change = append_summary_statistics(ttm_df_yearly_pct_change)
    

    return {
        'margins_df': margins_df,
        'quarterly_pct_change_df': quarterly_pct_change_df,
        'yearly_pct_change_df': yearly_pct_change_df,
        'annual_df': annual_df,
        'annual_pct_change_df': annual_pct_change_df,
        'ttm_df': ttm_df,
        'ttm_margins': ttm_margins,
        'ttm_df_quarterly_pct_change': ttm_df_quarterly_pct_change,
        'ttm_df_yearly_pct_change': ttm_df_yearly_pct_change,
    }

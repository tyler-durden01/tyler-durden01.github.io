# flask_app.py
from flask import Flask, request, render_template, jsonify
import pandas as pd
import os
import time

# Import modules from the Vista project
from GetAPIData import GetFinancialStatementData, GetHorizontalAndVertical, GetEarningsReportData
from GetAPIData import GetEmployeeData, GetRevenueSegmentationData, GetMarketCapData, GetDailyData
from AnalyzeAPIData import BalanceSheetMetrics, RelativeValuations, FinancialStatementAnalysis, CAPM

app = Flask(__name__)

# Define Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_company_data', methods=['GET', 'POST'])
def get_company_data():
    dataframes = {}
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        try:
            # Collect financial statement data
            financial_statements_df = GetFinancialStatementData.collect_financial_statement_data(ticker)
            dataframes['Financial Statements'] = financial_statements_df

            # Collect horizontal and vertical analysis
            GetHorizontalAndVertical_results = GetHorizontalAndVertical.collect_horizontal_and_vertical(financial_statements_df)
            dataframes.update({
                'Margins': GetHorizontalAndVertical_results['margins_df'],
                'Quarterly % Change': GetHorizontalAndVertical_results['quarterly_pct_change_df'],
                'Yearly % Change': GetHorizontalAndVertical_results['yearly_pct_change_df'],
                'Annual Aggregated': GetHorizontalAndVertical_results['annual_df'],
                'Annual % Change': GetHorizontalAndVertical_results['annual_pct_change_df'],
                'Trailing Twelve Months (TTM)': GetHorizontalAndVertical_results['ttm_df'],
                'TTM Margins': GetHorizontalAndVertical_results['ttm_margins'],
                'TTM Quarterly % Change': GetHorizontalAndVertical_results['ttm_df_quarterly_pct_change'],
                'TTM Yearly % Change': GetHorizontalAndVertical_results['ttm_df_yearly_pct_change'],
            })

            # Add other data collection steps
            earnings_df = GetEarningsReportData.collect_earnings_data(ticker)
            dataframes['Earnings Reports'] = earnings_df

            employee_df = GetEmployeeData.collect_employee_data(ticker, financial_statements_df)
            dataframes['Employees'] = employee_df

            revenue_product_segmentation = GetRevenueSegmentationData.collect_revenue_product_segmentation(ticker)
            dataframes.update({
                'Revenue Product Seg.': revenue_product_segmentation['revenue_product_segmentation_df'],
                'Revenue Product % Total': revenue_product_segmentation['revenue_product_segmentation_pct_total'],
                'Revenue Product % YoY': revenue_product_segmentation['revenue_product_segmentation_yoy'],
                'Revenue Product % QoQ': revenue_product_segmentation['revenue_product_segmentation_qoq'],
            })

            market_cap_data_df = GetMarketCapData.collect_market_cap_data(ticker)
            dataframes['Market Caps'] = market_cap_data_df

            daily_prices_df = GetDailyData.collect_daily_price_data(ticker)
            dataframes['Daily Prices'] = daily_prices_df

            balance_sheet_metrics_df = BalanceSheetMetrics.calculate_balance_sheet_metrics(
                market_cap_data_df, earnings_df, financial_statements_df
            )
            dataframes['Balance Sheet Metrics'] = balance_sheet_metrics_df

            valuations_TTM_df = RelativeValuations.calculate_relative_valuations(
                market_cap_data_df=market_cap_data_df,
                earnings_df=earnings_df,
                ttm_df=GetHorizontalAndVertical_results['ttm_df'],
                balance_sheet_metrics_df=balance_sheet_metrics_df
            )
            dataframes['Relative Valuations'] = valuations_TTM_df

            financial_statement_analysis_df = FinancialStatementAnalysis.calculate_financial_statement_analysis(
                financial_statements_df=financial_statements_df,
                ttm_df=GetHorizontalAndVertical_results['ttm_df']
            )
            dataframes['Financial Analysis'] = financial_statement_analysis_df

            CAPM_results, beta_results = CAPM.main(ticker)
            dataframes['CAPM'] = CAPM_results
            dataframes['Beta Analysis'] = beta_results

        except Exception as e:
            return jsonify({'error': str(e)})

        # Convert dataframes to JSON for easy rendering in the web interface
        data_json = {name: df.to_dict(orient='records') for name, df in dataframes.items()}

        return render_template('get_company_data.html', data=data_json, ticker=ticker)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
    
import pandas as pd
from jinja2 import Template
import time

while True:
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv('C:\\Users\\paulp\\OneDrive - Taiga Group Holdings, LLC\\Shared - Taiga Group Holdings\\Apex Executable\\Polygon\\stablePools\\Supporting Executables\\CurrentDepegLevels.csv')

    # Get the last 7 data points under the "depegLevel" column
    last_7_depeg_levels = df['depegLevel'].tail(7).tolist()

    # Define the HTML table template
    html_table_template = Template('''
        <table>
            <thead>
                <tr>
                    <th>Pool Name</th>
                    <th>Depeg Level</th>
                    <th>Current Tick</th>
                    <th>Base Tick</th>
                </tr>
            </thead>
            <tbody>
                {% for index, row in df.tail(7).iterrows() %}
                <tr>
                    <td>{{ row['poolName'] }}</td>
                    <td>{{ row['depegLevel'] }}</td>
                    <td>{{ row['CurrentTick'] }}</td>
                    <td>{{ row['BaseTick'] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    ''')

    # Render the HTML table with the last 7 data points under the "depegLevel" column
    html_table = html_table_template.render(df=df, last_7_depeg_levels=last_7_depeg_levels)

    # Define the HTML code for the web page
    html_code = f'''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <title>Depeg Status</title>
      </head>
      <body>
        <h1>Depeg Status</h1>
        <p>Updates every 5 minutes</p>
        {html_table}
      </body>
    </html>
    '''

    # Write the HTML code to a file
    with open('DepegStatus.html', 'w') as f:
        f.write(html_code)
    
    # Sleep for 5 minutes before running the loop again
    time.sleep(300)

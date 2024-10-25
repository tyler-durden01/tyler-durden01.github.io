import requests
import pandas as pd
### from config import api_key
api_key = '6fe8c4680cf2609b34c3674e0a32720b'

lehman = '0001124610'

url = f'https://financialmodelingprep.com/api/v3/income-statement/{lehman}?period=annual&apikey={api_key}'

response = requests.get(url)
print(response)
data = response.json()
print(data)

df = pd.DataFrame(data)

print(df)




'''
# userInput = input("Enter Search for CIK: ")
# userInput = 'Lehman'
lehman = '0001568495'

url = f'https://financialmodelingprep.com/api/v3/cik/{lehman}?apikey={api_key}'

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data)

print(data)

# can go off cik numbers!!
# need tickers and cik numbers matched. 
# enter a ticker, use a CIK to get the data. 
# enter a CIK, roll with it
# if CIK numbers always start with 0, then the program should know to roll with that.
# https://financialmodelingprep.com/api/v3/profile/AAPL
# When I come back, try getting the financial statements based on the cik numbers
'''
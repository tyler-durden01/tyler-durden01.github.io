import requests
import pandas as pd
### from config import api_key
### the below will be commented out, and the above will be enacted
api_key = '6fe8c4680cf2609b34c3674e0a32720b'

# userInput = input("Enter Search for CIK: ")
userInput = 'Lehman'

url = f'https://financialmodelingprep.com/api/v3/cik-search/{userInput}?apikey={api_key}'

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data)

print(df)

# can go off cik numbers!!
# need tickers and cik numbers matched. 
# enter a ticker, use a CIK to get the data. 
# enter a CIK, roll with it
# if CIK numbers always start with 0, then the program should know to roll with that.
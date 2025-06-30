import requests
import pandas as pd
import time

# Display all rows
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

API_KEY = "UV9QUT1VSQA2EU17"
symbol = "IBM"
function = "TIME_SERIES_DAILY_ADJUSTED"
url = "https://www.alphavantage.co/query"

params = {
    "function": function,
    "symbol": symbol,
    "apikey": API_KEY,
    "outputsize": "full",
    "datatype": "json"
}

response = requests.get(url, params=params)
time.sleep(12)
data = response.json()
print(data)


ts = data["Time Series (Daily) Adjusted"]
df = pd.DataFrame.from_dict(ts, orient="index")
df.columns = [col.split(". ")[1] for col in df.columns]
df.index = pd.to_datetime(df.index)
df = df.sort_index()

start_date = '2023-03-23'
end_date = '2025-06-24'
print(df.loc[start_date:end_date])


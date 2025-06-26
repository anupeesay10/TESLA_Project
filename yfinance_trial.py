import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

# Display all rows and columns
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

tsla = yf.Ticker("TSLA")


df = yf.download("TSLA", start="2010-06-29", end="2025-06-24", auto_adjust=False)
df.columns = df.columns.droplevel(1)
df = df.reset_index()

df.to_csv('new_tsla.csv')
#print(df.columns)
#print(df.head())

#connection string
engine = create_engine('postgresql://postgres:anirudh9@localhost:5432/postgres')

# SQL query
query = """
SELECT * FROM new_tsla;
"""

# Run the query
df2 = pd.read_sql_query(query, engine)
df2 = df2.drop(index=0).reset_index(drop=True) # Dropping the first row (as it is the same as the headers)
print(df2.head()) # Display the first five rows




import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import yfinance as yf


#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Display all rows
pd.set_option("display.max_rows", None)

# Optional: to display all columns too
pd.set_option("display.max_columns", None)

# Load the data using pandas
#connection string
engine = create_engine('postgresql://postgres:anirudh9@localhost:5432/postgres')

# SQL query
query = """
SELECT * FROM tsla;
"""

# Run the query
df1 = pd.read_sql_query(query, engine)
df1 = df1.drop(index=0).reset_index(drop=True) # Dropping the first row (as it is the same as the headers)
#print(df1) # Display the first five rows

df1['date']  = pd.to_datetime(df1['date'])
df1.set_index('date', inplace=True)


tsla = yf.Ticker("TSLA")


df2 = yf.download("TSLA", start="2022-03-24", end="2025-06-24", auto_adjust=False)
df2.columns = df2.columns.droplevel(1)


df2.reset_index(inplace=True)
df2.rename(columns={'Date': 'date'}, inplace=True)
df2.rename(columns={'Adj Close': 'adj_close'}, inplace=True)
df2.rename(columns={'Close': 'close_'}, inplace=True)
df2.rename(columns={'High': 'high'}, inplace=True)
df2.rename(columns={'Low': 'low'}, inplace=True)
df2.rename(columns={'Open': 'open_'}, inplace=True)
df2.rename(columns={'Volume': 'volume'}, inplace=True)
df2['date'] = pd.to_datetime(df2['date'])
df2.set_index('date', inplace=True)
#print(df2.head())


# Combine the DataFrames
combined_df = pd.concat([df1, df2])

# Sort by date
combined_df = combined_df.sort_index()

# Optional: reset index if you want 'Date' back as a column
# combined_df = combined_df.reset_index()

print(combined_df)

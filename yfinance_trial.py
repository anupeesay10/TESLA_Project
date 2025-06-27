import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

from datetime import datetime


import ssl
import certifi
import urllib.request

# Display all rows and columns
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

tsla = yf.Ticker("TSLA")


df = yf.download("TSLA", start="2010-06-29", end="2025-06-24", auto_adjust=False)
df.columns = df.columns.droplevel(1)
df = df.reset_index()
df['Date'] = pd.to_datetime(df['Date'])

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
#print(df2.head()) # Display the first five rows

#print(df2[['date','volume']])



# Initialize the Dash app
app = dash.Dash(__name__)

# Create the dropdown menu options
# FIXED dropdown values
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'All Years Statistics', 'value': 'All Years Statistics'}  # fixed
]


# List of years
year_list = [i for i in range(2010, 2026)]


# Create the layout of the app
app.layout = html.Div([
    html.H1("Tesla Stocks Dashboard", style={'textAlign': 'center', 'color': '#003366', 'fontSize': 30}),

    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='stat-select',
            options=dropdown_options,
            value='Yearly Statistics',
            placeholder='Select a statistic type'
        )
    ]),

    html.Div([
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value=year_list[-1]
        )
    ]),

    html.Div(id='output-container', className='chart-grid', style={'padding': '20px'})
])


# Disable year dropdown when All Years Statistics is selected
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='stat-select', component_property='value')
)
def update_input_container(selected_statistics):
    return selected_statistics == 'All Year Statistics'

@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='stat-select', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'All Years Statistics':
        all_years_data = df2[['date', 'volume']].copy()
        all_years_data['Year'] = all_years_data['date'].dt.year

        # Group by Year and get average volume
        yearly_volume = all_years_data.groupby('Year')['volume'].mean().reset_index()

        # Plot using 'Year' and 'volume'
        all_chart = dcc.Graph(
            figure=px.area(
                yearly_volume,
                x='Year',
                y='volume',
                title='Average Tesla Trading Volume Per Year (2010–2025)',
                markers=True
            )
        )

        return [html.Div(className='chart-item', children=[all_chart])]

    elif input_year and selected_statistics == 'Yearly Statistics':
        yearly_data = data[data['Year'] == input_year]

# Run the Dash app
if __name__ == '__main__':
    # Change the port number here
    app.run(debug=True, port=8060)  # <-- Specify your desired port here

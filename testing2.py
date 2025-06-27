import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import plotly.graph_objects as go

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Display all rows and columns
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Download Tesla stock data
df = yf.download("TSLA", start="2010-06-29", end="2025-06-24", auto_adjust=False)
df.columns = df.columns.droplevel(1) if isinstance(df.columns, pd.MultiIndex) else df.columns
df = df.reset_index()
df['Date'] = pd.to_datetime(df['Date'])

# Save to CSV
df.to_csv('new_tsla.csv', index=False)

# Save to SQL
engine = create_engine('postgresql://postgres:anirudh9@localhost:5432/postgres')
df.to_sql('new_tsla', engine, if_exists='replace', index=False)

query = "SELECT * FROM new_tsla;"

# Read from SQL
df2 = pd.read_sql_query(query, engine)
df2['date'] = pd.to_datetime(df2['Date'])  # Align with SQL column
df2.drop(columns=['Date'], inplace=True)
print(df2.columns)
# Dash app
app = dash.Dash(__name__)

# Dropdown options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'All Years Statistics', 'value': 'All Years Statistics'}
]

year_list = [i for i in range(2010, 2026)]

app.layout = html.Div([
    html.H1("Tesla Stocks Dashboard", style={'textAlign': 'center', 'color': '#003366'}),

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
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value=year_list[-1]
        )
    ]),

    html.Div(id='output-container', className='chart-grid', style={'padding': '20px'})
])

# Disable Year dropdown when All Years Statistics is selected
@app.callback(
    Output('select-year', 'disabled'),
    Input('stat-select', 'value')
)
def toggle_year_dropdown(stat_type):
    return stat_type == 'All Years Statistics'

# Chart output callback
@app.callback(
    Output('output-container', 'children'),
    [Input('stat-select', 'value'),
     Input('select-year', 'value')]
)
def update_output(stat_type, year):
    if stat_type == 'All Years Statistics':
        # Column Names: Index(['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume', 'date'], dtype='object')
        # Candlestick Chart
        fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                                             open=df['Open'],
                                             high=df['High'],
                                             low=df['Low'],
                                             close=df['Adj Close'], )])

        fig1.update_layout(
            title='Tesla Stock Candlestick Chart',
            yaxis_title='Price',
            xaxis_title='Date',
            xaxis_rangeslider_visible=True,
            width=1000,  # Set the desired width in pixels
            height=700  # Set the desired height in pixels
        )

        # Volume Chart
        df2['Year'] = df2['date'].dt.year
        yearly_volume = df2.groupby('Year')['Volume'].mean().reset_index()

        fig2 = px.area(yearly_volume, x='Year', y='Volume',
                      title='Average Tesla Trading Volume Per Year (2010–2025)', width=800,
              height=500,
                      markers=True)

        return [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2)]

    elif stat_type == 'Yearly Statistics' and year:
        year_data = df2[df2['date'].dt.year == year]

        fig = px.line(year_data, x='date', y='Volume',
                      title=f'Daily Trading Volume for {year}',width=600,
              height=400)


        return [dcc.Graph(figure=fig)]

    return []


if __name__ == '__main__':
    app.run(debug=True, port=8070)

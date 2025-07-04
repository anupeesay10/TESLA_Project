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
            title='Tesla Stock Candlestick Chart (2010-2025)',
            yaxis_title='Price',
            xaxis_title='Date',
            xaxis_rangeslider_visible=True,
            width=1900,
            height=700
        )

        # Volume Chart
        df2['Year'] = df2['date'].dt.year
        yearly_volume = df2.groupby('Year')['Volume'].mean().reset_index()
        fig2 = px.area(yearly_volume, x='Year', y='Volume',
                      title='Average Tesla Trading Volume Per Year (2010–2025)', width=1900,
              height=700,
                      markers=True)


        # Daily Return Chart
        df2['year'] = df2['date'].dt.year
        df2['daily_return'] = (df2['Adj Close'].pct_change()) * 100
        yearly_return = df2.groupby('year')['daily_return'].mean().reset_index()
        yearly_return['return_category'] = yearly_return['daily_return'].apply(
            lambda x: 'Positive' if x > 0 else 'Negative'
        )

        fig3 = px.bar(
            yearly_return,
            x='year',
            y='daily_return',
            color='return_category',
            color_discrete_map={'Positive': 'green', 'Negative': 'red'}
        ).update_layout(
            title="Average Daily Returns Per Year",
            yaxis_title='Percent Daily Return (%)',
            xaxis_title='Year',
            legend_title_text="Return Category",
            width=1900,
            height=700
            #yaxis = dict(tickformat=".2f")
        )


        # Drawdown Chart
        df2['Cumulative Max'] = df2['Adj Close'].cummax()
        df2['Drawdown'] = (df2['Adj Close'] / df2['Cumulative Max'] - 1) * 100
        fig4 = px.area(df2, x='date', y='Drawdown',
        title='Tesla Drawdowns Over All Years')
        fig4.update_layout(
        yaxis_title = 'Percent Drawdown (%)',
        xaxis_title = 'Date',
        width=1900,
        height=700
        )



        return [dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), dcc.Graph(figure=fig3), dcc.Graph(figure=fig4)]

    elif stat_type == 'Yearly Statistics' and year:
        year_data = df2[df2['date'].dt.year == year]

        # Candlestick Chart
        fig1_year = go.Figure(data=[go.Candlestick(x=year_data['date'],
                                              open=year_data['Open'],
                                              high=year_data['High'],
                                              low=year_data['Low'],
                                              close=year_data['Adj Close'], )])

        fig1_year.update_layout(
            title=f'Tesla Stock Candlestick Chart for {year}',
            yaxis_title='Price',
            xaxis_title='Date',
            xaxis_rangeslider_visible=True,
            width=1900,
            height=700
        )

        # Volume Chart
        fig2_year = px.area(year_data, x='date', y='Volume',
                      title=f'Daily Trading Volume for {year}',width=1900,
              height=700)


        # Daily Return Per Year
        year_data['daily_return'] = (year_data['Adj Close'].pct_change()) * 100
        yearly_return2 = year_data.groupby('date')['daily_return'].mean().reset_index()
        yearly_return2['return_category'] = yearly_return2['daily_return'].apply(
            lambda x: 'Positive' if x > 0 else 'Negative'
        )

        fig3_year = px.bar(
            yearly_return2,
            x='date',
            y='daily_return',
            color='return_category',
            color_discrete_map={'Positive': 'green', 'Negative': 'red'}
        ).update_layout(
            title=f"Average Daily Returns for {year}",
            yaxis_title='Percent Daily Return (%)',
            xaxis_title='Year',
            legend_title_text="Return Category",
            width=1900,
            height=700
        )

        # Drawdown Chart
        year_data['Cumulative Max'] = year_data['Adj Close'].cummax()
        year_data['Drawdown'] = (year_data['Adj Close'] / year_data['Cumulative Max'] - 1) * 100
        fig4_year = px.area(year_data, x='date', y='Drawdown',
                       title=f'Tesla Drawdowns for {year}')

        fig4_year.update_layout(
            yaxis_title='Percent Drawdown (%)',
            xaxis_title='Date',
            width=1900,
            height=700
        )

        return [dcc.Graph(figure=fig1_year), dcc.Graph(figure=fig2_year), dcc.Graph(figure=fig3_year), dcc.Graph(figure=fig4_year)]

    return []


if __name__ == '__main__':
    app.run(debug=True, port=8070)

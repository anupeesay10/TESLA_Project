#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


import ssl
import certifi
import urllib.request

url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv'

# Create an SSL context using certifi's trusted CA bundle
context = ssl.create_default_context(cafile=certifi.where())

# Open the URL using the context
with urllib.request.urlopen(url, context=context) as response:
    data = pd.read_csv(response)


# Initialize the Dash app
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# List of years
year_list = [i for i in range(1980, 2024)]

# Create the layout of the app
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center', 'color': '#003366', 'fontSize': 24}),

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


# Disable year dropdown when Recession is selected
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='stat-select', component_property='value')
)
def update_input_container(selected_statistics):
    return selected_statistics == 'Recession Period Statistics'


# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='stat-select', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Chart 1 for Recession Statistics
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec,
                           x='Year',
                           y='Automobile_Sales').update_layout(
                           title="Average Automobile Sales Fluctuation Over Recession Period")
        )

        # Chart 2 for Recession Statistics
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                          x='Vehicle_Type',
                          y='Automobile_Sales').update_layout(
                          title="Average Vehicles Sold by Vehicle Type During Recession")
        )

        # Chart 3 for Recession Statistics
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec,
                          names='Vehicle_Type',
                          values='Advertising_Expenditure').update_layout(
                          title='Advertisement Expenditure Share by Vehicle Type During Recession')
        )

        # Chart 4 for Recession Statistics
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])[
            'Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                          x='unemployment_rate',
                          y='Automobile_Sales',
                          color='Vehicle_Type',
                          labels={'unemployment_rate': 'Unemployment Rate',
                                  'Automobile_Sales': 'Average Automobile Sales'}).update_layout(
                          title='Effect of Unemployment Rate on Vehicle Type and Sales')
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)],
                     style={'display': 'flex'})
        ]

    elif input_year and selected_statistics == 'Yearly Statistics':
        yearly_data = data[data['Year'] == input_year]

        # Chart 1 for Yearly Statistics
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas,
                           x='Year',
                           y='Automobile_Sales').update_layout(
                           title='Average Yearly Automobile Sales')
        )

        # Chart 2 for Yearly Statistics
        mas = data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas,
                           x='Month',
                           y='Automobile_Sales').update_layout(
                           title='Total Monthly Automobile Sales')
        )

        # Chart 3 for Yearly Statistics
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata,
                          x='Vehicle_Type',
                          y='Automobile_Sales').update_layout(
                          title='Average Vehicles Sold by Vehicle Type in the year {}'.format(input_year))
        )

        # Chart 4 for Yearly Statistics
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data,
                          names='Vehicle_Type',
                          values='Advertising_Expenditure').update_layout(
                          title='Advertisement Expenditure Share by Vehicle Type in the Year {}'.format(input_year))
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)],
                     style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)],
                     style={'display': 'flex'})
        ]
    else:
        return None


# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)
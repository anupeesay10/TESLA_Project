import pandas as pd

table = input('Please enter your table name (include .csv extension): ')
while not table.endswith('.csv'):
    print('Must include .csv extension!')
    table = input('Please enter your table name (include .csv extension): ')

try:
    df = pd.read_csv(table)
    cols = df.columns

    index = table.find('.csv')

    create_stmt = f" CREATE TABLE {table[:index]} (\n"
    create_stmt += ",\n".join([f"    {col} TEXT" for col in cols])
    create_stmt += "\n);"

    print(create_stmt)

except:
    print('Table not found')

##########################################
# Name: Matthew Oke
# Project: CMPT450EndProject
# Filename: main.py
##########################################

import dash as ds
import plotly as pl
import numpy as np
import pandas as pn
import dataPrep

app = ds.Dash(__name__)

# Set up a color dictionary for use within dash components. FFFFFF is pure white, 111111 is pure black
colors = {'background': '#FFFFFF',
          'text': '#111111'}




layout1 = ds.html.Div(style={'backgroundColor': colors['background']}, children=[ds.html.H1(style={'textAlign': 'center',
                                'color': colors['text']}, children='RealEdmonton: Housing Made Easy'),
                                "Input: ", ds.dcc.Input(id='searchInput', value='Neighborhood Name...', type='text'),
                                ds.html.Br(), ds.html.Div(id='myOutput')
                                                                                 ])


# This callback connected to the function below it connects the input value with the table.
@app.callback(
    ds.Output(component_id='myOutput', component_property='children'),
    ds.Input(component_id='searchInput', component_property='value')
)
def update_table(input_value):
    return f'Output: {input_value}'


app.layout = layout1

print(dataPrep.generateSpecificData("Rutherford"))
if __name__ == '__main__':
    app.run_server(debug=True)

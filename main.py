
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

######################
#imports added by Ian#
######################
import geojson
import plotly.graph_objects as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = ds.Dash(__name__, external_stylesheets=external_stylesheets)

# Set up a color dictionary for use within dash components. FFFFFF is pure white, 111111 is pure black
colors = {'background': '#FFFFFF',
          'text': '#111111'}



####################
#files added by Ian#
####################
cdf = pn.read_csv("nav2.csv", low_memory=False)
crimedf = pn.read_csv("finalcrimestats.csv", low_memory=False)

with open('Neighbourhoods.geojson') as f:
    gj = geojson.load(f)

nbs = pn.read_csv("coenb.csv", low_memory=False)
nbcodes = nbs['Neighbourhood Number']
nbnames = nbs['Descriptive Name']


fig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=cdf['nnum'],featureidkey="properties.neighbourhood_number",z=cdf['Assessed Value'],colorscale='Blues',colorbar=dict(title='Assessed Value'),marker_opacity=0.5),            
    layout=dict(mapbox_style='carto-positron', width=1200, height=850, mapbox_zoom=9.7,mapbox_center = {"lat": 53.54551, "lon": -113.49408}))

crimefig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=crimedf['nnum'],featureidkey="properties.neighbourhood_number",z=crimedf['normpermil'],colorscale='Reds',colorbar=dict(title='Crimes per 1000 Residents'),marker_opacity=0.5),            
    layout=dict(mapbox_style='carto-positron', width=1200, height=850, mapbox_zoom=9.7,mapbox_center = {"lat": 53.54551, "lon": -113.49408}))







app.layout = ds.html.Div(style={'backgroundColor': colors['background']}, children=[ds.html.H1(style={'textAlign': 'center',
                                'color': colors['text']}, children='RealEdmonton: Housing Made Easy'),
                                ds.dcc.Tabs(id='Tabs', value= 'Specific View', children=[
                                    ds.dcc.Tab(label='Specific View', value='Specific View'),
                                    ds.dcc.Tab(label='Assessment View', value='Assessment View'),
                                    ds.dcc.Tab(label='Crime View', value='Crime View'),
                                    ds.dcc.Tab(label='Recommend View', value='Recommend View')
                                ]),
                                ds.html.Div(id='Tab Content')
                                                                                  ])

# The renderContent function is connected to a callback, making it update any time the Tab
# value changes. Any time a user switches tabs, it will generate the required tab's info.
# This is where any Dash HTML code is placed that is specific to a tab.

@app.callback(
    ds.Output(component_id='Tab Content', component_property='children'),
    ds.Input(component_id='Tabs', component_property='value')
)
def renderContent(tab):
    if tab == 'Specific View':
        return ds.html.Div([
                            ds.html.Br(),
                            ds.html.Br(),
                            "Input: ", ds.dcc.Input(id='searchInput', value='Neighborhood Name...', type='text'),
                            ds.html.Button(id='search-state', n_clicks=0, children='Search'),
                            ds.html.Br(), ds.html.Table([ds.html.Tr([ds.html.Td('Neighbourhood Name:'), ds.html.Td(id='nName')]),
                                                        ds.html.Tr([ds.html.Td('# of Properties:'), ds.html.Td(id='count')]),
                                                        ds.html.Tr([ds.html.Td('Smallest Assessment Value:'), ds.html.Td(id='min')]),
                                                        ds.html.Tr([ds.html.Td('Largest Assessment Value:'), ds.html.Td(id='max')]),
                                                        ds.html.Tr([ds.html.Td('Average Mean Value:'), ds.html.Td(id='mean')]),
                                                        ds.html.Tr([ds.html.Td('Average Median Value:'), ds.html.Td(id='median')]),
                                                        ds.html.Tr([ds.html.Td('Mode Income:'), ds.html.Td(id='mode')])
                                                        ])
                            ])
    # HTML code for the assessment view here
    elif tab == 'Assessment View':
        return ds.html.Div(children=[
            ds.dcc.Graph(id='choropleth',figure=fig)

        ], style={'padding-left': '16vw', 'height': '80vh'})

    # HTML code for the crime view here
    elif tab == 'Crime View':
        return ds.html.Div(children=[
            ds.dcc.Graph(id='crimechoropleth',figure=crimefig)

        ], style={'padding-left': '16vw', 'height': '80vh'})
        

    # HTML code for the recommend view here
    elif tab == 'Recommend View':
        return ds.html.Div([


        ])

# Specific View updater function. This function will run any time the 'Search' button on the
# Specific View is pressed. It will call the dataPrep.py generateSpecificData function with
# the input parameter as the search bar value.
# This callback connected to the function below it connects the input value with the table.



@app.callback(
    ds.Output('choropleth', 'figure'),
    [ds.Input('choropleth', 'clickData')])
def update_figure(clickData):    
    if clickData is not None:            
        location = clickData['points'][0]['location']

        for i in range(len(nbcodes)):
            if location == nbcodes[i]:
                res = nbnames[i]

                app.logger.info(res)

    return res

@app.callback(
    ds.Output('crimechoropleth', 'figure'),
    [ds.Input('crimechoropleth', 'clickData')])
def update_figure(clickData):    
    if clickData is not None:            
        location = clickData['points'][0]['location']

        for i in range(len(nbcodes)):
            if location == nbcodes[i]:
                res = nbnames[i]

                app.logger.info(res)

    return res



@app.callback(
    ds.Output(component_id='nName', component_property='children'),
    ds.Output(component_id='count', component_property='children'),
    ds.Output(component_id='min', component_property='children'),
    ds.Output(component_id='max', component_property='children'),
    ds.Output(component_id='mean', component_property='children'),
    ds.Output(component_id='median', component_property='children'),
    ds.Output(component_id='mode', component_property='children'),
    ds.Input(component_id='search-state', component_property='n_clicks'),
    ds.State('searchInput', 'value')
)
def update_table(n_clicks, input_value):
    callbackList = dataPrep.generateSpecificData(input_value)
    return callbackList


if __name__ == '__main__':
    app.run_server(debug=True)

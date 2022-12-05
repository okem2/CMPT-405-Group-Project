
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
import dash_bootstrap_components as dbc
import plotly_express as px

######################
# imports added by Ian#
######################
import geojson
import plotly.graph_objects as go

app = ds.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
# app.config.suppress_callback_exceptions=True

# Set up a color dictionary for use within dash components. FFFFFF is pure white, 111111 is pure black
colors = {'background': '#FFFFFF',
          'text': '#111111'}


####################
# files added by Ian#
####################
cdf = pn.read_csv("nav2.csv", low_memory=False)
crimedf = pn.read_csv("finalcrimestats.csv", low_memory=False)

with open('Neighbourhoods.geojson') as f:
    gj = geojson.load(f)

nbs = pn.read_csv("coenb.csv", low_memory=False)
nbcodes = nbs['Neighbourhood Number']
nbnames = nbs['Descriptive Name']

crimeGraph = pn.DataFrame({'Neighbourhood': ['Neighbourhood', 'Average'], 'Crime Occurences': [0, 67.069091]})

crimeSpecificFig = px.bar(data_frame=crimeGraph, x='Neighbourhood', y='Crime Occurences', text_auto=True, width=600, height=400,title="Crime occurences in specified neighbourhood")

fig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=cdf['nnum'], featureidkey="properties.neighbourhood_number", z=cdf['Assessed Value'], colorscale='Blues', colorbar=dict(title='Average Assessed Value'), marker_opacity=0.5, hovertext='Neighbourhood: ' + cdf['descname']),
    layout=dict(mapbox_style='carto-positron', width=600, height=525, mapbox_zoom=8.9, mapbox_center = {"lat": 53.54551, "lon": -113.49408}))

crimefig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=crimedf['nnum'],featureidkey="properties.neighbourhood_number",z=crimedf['normpermil'],colorscale='Reds',colorbar=dict(title='Crimes per 1000 Residents'),marker_opacity=0.5, hovertext='Neighbourhood: ' + cdf['descname']),
    layout=dict(mapbox_style='carto-positron', width=600, height=525, mapbox_zoom=8.9, mapbox_center = {"lat": 53.54551, "lon": -113.49408}))


app.layout = ds.html.Div(children=[ds.html.H1(style={'textAlign': 'center',
                                'color': colors['text']}, children='RealEdmonton: Housing Made Easy'),
                                ds.html.Br(),
                                ds.html.Br(),
                                ds.html.Div([
                                ds.html.Div([
                                "Input: ", ds.dcc.Input(id='searchInput', value='Neighbourhood Name...', type='text'),
                                ds.html.Button(id='search-state', n_clicks=0, children='Search'),
                                ds.html.Br(), ds.html.Table([ds.html.Tr([ds.html.Td('Neighbourhood Name:'), ds.html.Td(id='nName')]),
                                                        ds.html.Tr([ds.html.Td('# of Properties:'), ds.html.Td(id='count')]),
                                                        ds.html.Tr([ds.html.Td('Smallest Assessment Value:'), ds.html.Td(id='min')]),
                                                        ds.html.Tr([ds.html.Td('Largest Assessment Value:'), ds.html.Td(id='max')]),
                                                        ds.html.Tr([ds.html.Td('Average Mean Value:'), ds.html.Td(id='mean')]),
                                                        ds.html.Tr([ds.html.Td('Average Median Value:'), ds.html.Td(id='median')]),
                                                        ds.html.Tr([ds.html.Td('Mode Income:'), ds.html.Td(id='mode')])
                                                        ],style={'padding':'200px'})]),
                                ds.dcc.Graph(id='crimeGraph', figure=crimeSpecificFig, style={'justify-content':'right'})
                                ], style={'display':'flex'}),
                                ds.html.Div([ds.dcc.Graph(id='choropleth', figure=fig, clickData=None),
                                ds.dcc.Graph(id='crimechoropleth', figure=crimefig)], style={'display':'flex', 'padding-left:':'0px', 'margin':'0px'})
                                                                                  ])


@app.callback(
    ds.Output(component_id='crimeGraph', component_property='figure'),
    ds.Input(component_id='nName', component_property='children'),
    prevent_initial_call=True
)
def updateGraph(name):
    newCount = crimedf[crimedf['nname'] == name].iloc[0, 2]

    print(newCount)
    fig = pn.DataFrame({'Neighbourhood': [name, 'Average'], 'Crime Occurrences': [newCount, 67.069091]})
    newFigure = px.bar(data_frame=fig, x='Neighbourhood', y='Crime Occurrences', text_auto=True, width=600, height=400,
             title="Crime occurrences in specified neighbourhood")

    return newFigure



@app.callback(
    ds.Output(component_id='searchInput', component_property='value'),
    ds.Input('choropleth', 'clickData'),
    ds.Input('crimechoropleth', 'clickData'))
def update_figure(clickData, secondClickData):
    graphTrigger = ds.ctx.triggered_id
    if graphTrigger == 'choropleth':
        if clickData is not None:
            location = clickData['points'][0]['location']

            for i in range(len(nbcodes)):
                if location == nbcodes[i]:
                    res = nbnames[i]

                    app.logger.info(res)
                    return res
        else:
            return None

    elif graphTrigger == 'crimechoropleth':
        if secondClickData is not None:
            location = secondClickData['points'][0]['location']

            for i in range(len(nbcodes)):
                if location == nbcodes[i]:
                    res = nbnames[i]

                    app.logger.info(res)
                    return res
        else:
            return None


@app.callback(
    ds.Output(component_id='nName', component_property='children'),
    ds.Output(component_id='count', component_property='children'),
    ds.Output(component_id='min', component_property='children'),
    ds.Output(component_id='max', component_property='children'),
    ds.Output(component_id='mean', component_property='children'),
    ds.Output(component_id='median', component_property='children'),
    ds.Output(component_id='mode', component_property='children'),
    ds.Input(component_id='search-state', component_property='n_clicks'),
    ds.State('searchInput', 'value'),
    prevent_initial_call=True
)
def update_table(n_clicks, input_value):
    callbackList = dataPrep.generateSpecificData(input_value)
    return callbackList


if __name__ == '__main__':
    app.run_server(debug=True)

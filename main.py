
##########################################
# Name: Matthew Oke, Keyanna Levie, Ian Leblanc, Wamiq Hussain
# Project: CMPT450EndProject
# Filename: main.py
##########################################

# To run this program correctly, make sure all relevant data files submitted along with this main are present,
# and then run the program. After loading, you will be given a server address to go to.

import dash as ds
import plotly as pl
import numpy as np
import pandas as pn
import dataPrep
import dash_bootstrap_components as dbc
import plotly.express as px
import geojson
import plotly.graph_objects as go

# Set up the app object that will house the application
app = ds.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

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

crimeGraph = pn.DataFrame({'Neighbourhood': ['Neighbourhood', 'Average'], 'Crime Occurences': [0, 67]})

# Set up the adjacent bar graph to the specific data to show the relative amount of crime in that neighbourhood
crimeSpecificFig = px.bar(data_frame=crimeGraph, x='Neighbourhood', y='Crime Occurences', text_auto=True, width=600, height=400,title="Crime occurences in specified neighbourhood")

# Set up the choropleth maps
fig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=cdf['nnum'], featureidkey="properties.neighbourhood_number", z=cdf['Assessed Value'], colorscale='Blues', colorbar=dict(title='Average Assessed Value'), marker_opacity=0.5, hovertext='Neighbourhood: ' + cdf['descname']),
    layout=dict(mapbox_style='carto-positron', width=600, height=525, mapbox_zoom=8.9, mapbox_center = {"lat": 53.54551, "lon": -113.49408}))

crimefig = go.Figure(go.Choroplethmapbox(geojson=gj, locations=crimedf['nnum'],featureidkey="properties.neighbourhood_number",z=crimedf['normpermil'],colorscale='Reds',colorbar=dict(title='Crimes per 1000 Residents'),marker_opacity=0.5, hovertext='Neighbourhood: ' + cdf['descname']),
    layout=dict(mapbox_style='carto-positron', width=600, height=525, mapbox_zoom=8.9, mapbox_center = {"lat": 53.54551, "lon": -113.49408}))

########
# Files added by Keyanna
########

grad_sal = pn.read_csv("grad-data-trim.csv")
drop_sal = grad_sal.groupby(["Field of Study (2-digit CIP code)"])["Median Income"].mean().reset_index()
app.title = 'RealEdmonton'

# Set up the layout object using all of the HTML components for the page
app.layout = ds.html.Div(children=[ds.html.H1(style={'textAlign': 'center',
                                'color': colors['text']}, children='RealEdmonton: Housing Made Easy'),
                                ds.html.Br(),
                                ds.html.Br(),
                                ds.html.H2("Specifics"),
                                ds.html.Div([
                                ds.html.Div([
                                "Input: ", ds.dcc.Input(id='searchInput', placeholder='Neighbourhood Name...', type='text'),
                                ds.html.Button(id='search-state', n_clicks=0, children='Search'),
                                ds.html.Br(),ds.html.Br(), ds.html.Table([ds.html.Tr([ds.html.Td('Neighbourhood Name:'), ds.html.Td(id='nName')]),
                                                        ds.html.Tr([ds.html.Td('# of Properties:'), ds.html.Td(id='count')]),
                                                        ds.html.Tr([ds.html.Td('Smallest Assessment Value:'), ds.html.Td(id='min')]),
                                                        ds.html.Tr([ds.html.Td('Largest Assessment Value:'), ds.html.Td(id='max')]),
                                                        ds.html.Tr([ds.html.Td('Average Mean Value:'), ds.html.Td(id='mean')]),
                                                        ds.html.Tr([ds.html.Td('Average Median Value:'), ds.html.Td(id='median')]),
                                                        ds.html.Tr([ds.html.Td('Mode Income:'), ds.html.Td(id='mode')])
                                                        ],style={'padding':'200px'})]),
                                ds.dcc.Graph(id='crimeGraph', figure=crimeSpecificFig, style={'justify-content':'right'})
                                ], style={'display':'flex'}),
                                ds.html.Div([
                                    ds.html.H2("Assessment Data"),
                                    ds.dcc.Graph(id='choropleth', figure=fig, clickData=None, style={'display': 'inline-block'}),
                                    ds.html.H2("Crime Data"),
                                    ds.dcc.Graph(id='crimechoropleth', figure=crimefig)], 
                                    style={'display':'flex','padding-left:':'0px', 'margin':'0px'}
                                    ),
                                ds.html.H2("Recommendations"),
                                ds.html.Div([
                                    ds.dcc.Dropdown(
                                        id='dropdown',
                                        options=[{'label': r, 'value': r} for r in list(drop_sal.loc[:,"Field of Study (2-digit CIP code)"].unique())],
                                        value='a',
                                        placeholder='Occupation',
                                        style={'width': '60%', 'marginRight':'10px'}
                                    ), 
                                    "    or    ",
                                    ds.dcc.Input(id='salInput', placeholder='Salary Amount', type='number', style={'width': '35%', 'marginRight':'10px'}),
                                    ds.html.Button(id='searchSal', n_clicks=0, children='Submit'),
                                    ds.html.Br(),ds.html.Br(),
                                    ds.dash_table.DataTable(
                                        id='salTable'
                                    ),
                                    ds.html.Br(),ds.html.Br()
                                ])
                                                                                  ])

# The affordability function takes a salary as a parameter and then calculates an appropriate
# mortgage amount, and then returns float that makrs the maximum recommended price of a house.

def affordability(salary):
    top_mortgage = salary * 2.25
    top_house = (top_mortgage*25)/0.8
    return top_house

# The get_salary fuction takes a name (The name of an occupation) as a parameter and returns a
# salary.

def get_salary(name):
    occupation = drop_sal[drop_sal['Field of Study (2-digit CIP code)'] == str(name)]
    salary = occupation["Median Income"]
    print('Salary:',salary)
    return int(salary)


# The update_salary function uses callbacks to update the recommendation graph of properties.
# It takes inputs from the search button, and the dropdown menu and manual salary input field.

@app.callback(
    ds.Output('salTable', 'data'),
    ds.Output('salTable', 'columns'),
    ds.Input('searchSal', 'n_clicks'),
    ds.State("dropdown", 'value'),
    ds.State('salInput', 'value'),
    prevent_initial_call=True
)
def update_salary(n_clicks, value, value2):
    if value is not None:
        sal = get_salary(value)
        maxhouse = affordability(int(sal))
        df = cdf.loc[(cdf['Assessed Value']< maxhouse), ['Neighbourhood', 'Assessed Value']]
        return df.to_dict('records'), [{'name': i, 'id':i} for i in df.columns]
    elif value2 is not None:
        maxhouse = affordability(int(value2))
        df = cdf.loc[(cdf['Assessed Value']< maxhouse), ['Neighbourhood', 'Assessed Value']]
        return df.to_dict('records'), [{'name': i, 'id':i} for i in df.columns]
    return [{}], []


# The updateGraph function updates the crime bar chart next to the specific neighbourhood
# information whenever a new neighbourhood's information is brought up.

@app.callback(
    ds.Output(component_id='crimeGraph', component_property='figure'),
    ds.Input(component_id='nName', component_property='children'),
    prevent_initial_call=True
)
def updateGraph(name): # Updates crime bar chart
    newCount = crimedf[crimedf['nname'] == name].iloc[0, 2]

    print(newCount)
    fig = pn.DataFrame({'Neighbourhood': [name, 'Average'], 'Crime Occurrences': [newCount, 67]})
    newFigure = px.bar(data_frame=fig, x='Neighbourhood', y='Crime Occurrences', text_auto=True, width=600, height=400,
             title="Crime occurrences in specified neighbourhood")

    return newFigure


# The update_figure function uses callbacks to send click information to the specific information
# area. It uses context information to figure out which choropleth was clicked, and sends that
# respective info to the specific area.

@app.callback(
    ds.Output(component_id='searchInput', component_property='value'),
    ds.Input('choropleth', 'clickData'),
    ds.Input('crimechoropleth', 'clickData'))
def update_figure(clickData, secondClickData): #Populates search bar when neighbourhood map clicked
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
                    ds.dcc.Store(res)
                    return res
        else:
            return None


# The update_table function uses callbacks and a function from dataPrep.py to update the
# specific information on a neighbourhood and present it to the user. Whenever the search
# button is pressed, it triggers the callback.

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
def update_table(n_clicks, input_value): #Updates the assessment data table
    callbackList = dataPrep.generateSpecificData(input_value)
    return callbackList


if __name__ == '__main__':
    app.run_server(debug=True)

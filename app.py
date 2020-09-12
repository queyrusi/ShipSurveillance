# Import required libraries
import os
import pickle
import copy
import datetime as dt
import math
import pandas as pd
from flask import Flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, date
from config import LAYOUT as layout
from config import DATAPATH, DATERANGE
from utils import Utils
from filter import Filter as fi
import time

colors = ["royalblue", "crimson", "lightseagreen", "orange", "lightgrey"]

app = dash.Dash(__name__)
server = app.server

# ships data
ship_df = pd.read_json(DATAPATH)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        html.Div(
            id="header",
            className='row flex-display',
            style={"margin-bottom": "25px"},
            children=[
                html.Div(
                    children=[
                        html.Img(src=app.get_asset_url('ensta.png'),
                                 style={
                                     'height': '120px',
                                     'width': 'auto',
                                 })
                    ],
                    className='one-third column',
                ),
                html.Div([
                    html.H3('Suivi de Navires Militaires',
                            style={'margin-bottom': '0px'}),
                    html.H5('Dashboard', style={'margin-top': '0px'})
                ],
                         id="title",
                         className='one-half column'),
                html.
                A(html.Button("Learn More", id="learn-more-button"),
                  href=
                  "https://etudes.ensta.fr/pluginfile.php/299/mod_book/chapter/250/Projet%20DGA%20navire.pdf",
                  target="_blank",
                  className="one-third column",
                  id="button")
            ]),
        html.Div(
            id="buttons",
            className='row flex-display',
            style={"margin-bottom": "25px"},
            children=[
                html.
                A(html.Button("Run", id="run_button")),
                html.P(id='button-clicks'),
            ]),
        html.Div(
            id="add-account",
            className='row flex-display',
            style={"margin-bottom": "25px"},
            children=[
                dcc.Input(placeholder='Enter a new account...',
                          id='input-box', type='text'),
                html.
                A(html.Button("Add Account", id="add-account-button"),
                  target="_blank",
                  className="one-third column",
                  id="button_add_account"),
                html.P(id='button-added'),
            ]),
        html.Div(
            [
                html.Div(
                    [
                        html.P('Date Selector:',
                               className="control_label",
                               id='date_range'),
                        dcc.RangeSlider(id='date_selector',
                                        min=-365,
                                        max=0,
                                        value=[-DATERANGE, 0],
                                        className="dcc_control"),
                        html.P('Filter by Country:',
                               className="control_label"),
                        dcc.RadioItems(id='country_selector_status',
                                       options=[{
                                           'label': 'All ',
                                           'value': 'all'
                                       }, {
                                           'label': 'Customize ',
                                           'value': 'custom'
                                       }],
                                       value='all',
                                       labelStyle={'display': 'inline-block'},
                                       className="dcc_control"),
                        dcc.Dropdown(id='country_selector',
                                     options=[{
                                         'label': pays,
                                         'value': pays
                                     } for pays in ship_df.pays.unique()],
                                     multi=True,
                                     value='France',
                                     className="dcc_control"),
                        html.P('Filter by Ship:', className="control_label"),
                        dcc.RadioItems(id='ship_selector_status',
                                       options=[{
                                           'label': 'All ',
                                           'value': 'all'
                                       }, {
                                           'label': 'Customize ',
                                           'value': 'custom'
                                       }],
                                       value='all',
                                       labelStyle={'display': 'inline-block'},
                                       className="dcc_control"),
                        dcc.Dropdown(
                            id='ship_selector',
                            options=[],
                            #  options=[{'label': ship, 'value': i} for i, ship in enumerate(ship_df.nom.unique())],
                            multi=True,
                            style={
                                'overflowY': 'scroll',
                                'height': 180
                            },
                            className="dcc_control"),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options"),
                html.Div([
                    html.Div([
                        html.Div([
                            html.P("No. of Ships"),
                            html.H6(id="nbShip", className="info_text")
                        ],
                                 className="mini_container left_mini"),
                        html.Div([
                            html.P("No. of Country"),
                            html.H6(id="nbCountry", className="info_text")
                        ],
                                 className="mini_container"),
                        html.Div([
                            html.P("No. of Point"),
                            html.H6(id="nbPoint", className="info_text")
                        ],
                                 className="mini_container"),
                        html.Div([
                            html.P("No. of Port"),
                            html.H6(id="nbPort", className="info_text")
                        ],
                                 className="mini_container right_mini"),
                    ],
                             id="info-container",
                             className="row container-display"),
                    html.Div([
                        html.P("No. of ships spotted by day"),
                        dcc.Graph(id='count_graph',
                                  style={
                                      'overflowY': 'scroll',
                                      'height': 275
                                  })
                    ],
                             id="countGraphContainer",
                             className="pretty_container")
                ],
                         id="right-column",
                         className="eight columns")
            ],
            # style={'overflowY': 'scroll', 'height': 300},
            className="row flex-display"),
        html.Div(
            [
                html.Div(
                    # visualize ship trace
                    # relative function: showShipTrace
                    [
                        html.P("Ship Trace Visualization"),
                        dcc.Graph(id='main_graph',
                                  figure={
                                      'data': [],
                                      'layout': layout
                                  },
                                  style={'height': '860px'})
                    ],
                    className='mini_container',
                    style={
                        'height': '900px',
                        'flex': 3
                    }),
            ],
            className='row flex-display'),
        html.Div(
            # visualize ship trace
            # relative function: showShipTrace
            [
                html.P("Ship List at Position: All", id='position_info'),
                dash_table.DataTable(id='ship_list',
                    columns=[{"name": "Nom", "id": "nom"},
                             {"name": "Date", "id": "date"},
                             {"name": "Tweet", "id": "tweet"}],
                    data=pd.DataFrame({"nom": []}).to_dict('records')
                )
            ],
            className='mini_container',
            style={
                'height': '900px',
                'overflowY': 'scroll',
                'flex': 1
            }),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column"
    })


# Run Button
@app.callback(
    Output('button-clicks', 'children'),
    [Input('run_button', 'n_clicks')])
def clicks(n_clicks):
    if n_clicks:
        os.system('./run.sh')
        return ''


# Add account Button
@app.callback(Output('input-box', 'value'),
              [Input('add-account-button', 'n_clicks')],
              [State('input-box', 'value')])
def add_Account(n_clicks, input_value):
    if n_clicks:
        os.system('cd scripts; ./add_account.sh ' + input_value + '; cd ..')
        return ''

# date range
@app.callback(Output('date_range', 'children'),
              [Input('date_selector', 'value')])
def display_date_range(value):
    return 'Date Selectore: From: {} to : {}'.format(
        *Utils.dateTransform(datetime.now(), value))


@app.callback(Output('country_selector', 'value'),
              [Input('country_selector_status', 'value')])
def update_country_list(selector):

    if selector == 'all':
        return list(ship_df.pays.unique())
    else:
        return []


@app.callback(Output('ship_selector', 'options'),
              [Input('country_selector', 'value')])
def update_ship_option(countries):
    ship_list = ship_df[ship_df.pays.isin(countries if countries else [])]
    options = [{
        'label': ship,
        'value': ship
    } for ship in ship_list.nom.unique()]

    return options


@app.callback(Output('ship_selector', 'value'), [
    Input('ship_selector_status', 'value'),
    Input('ship_selector', 'options')
])
def update_ship_list(selector, options):

    if selector == 'all':
        return [option['value'] for option in options]
    else:
        return []


@app.callback(Output('aggregate_data', 'data'), [
    Input('date_selector', 'value'),
    Input('country_selector', 'value'),
    Input('ship_selector', 'value'),
    Input('main_graph', 'selectedData')
])
def update_aggregate_data(date, countries, ships, selectedDataMain):
    funcs = ['by_date', 'by_country', 'by_name', 'by_longitude', 'by_latitude']
    columns = ['date', 'pays', 'nom', 'longitude', 'latitude']
    date = Utils.value_to_date(datetime.now(), date)
    index = fi.by_value(ship_df, [date, countries, ships], funcs, columns)
    df1 = ship_df[index]
    if not (selectedDataMain is None) and not (len(selectedDataMain['points']) == 0):
        min_longitude = min([selectedDataMain['points'][i]['lon'] for i
         in range(len(selectedDataMain['points']))])
        max_longitude = max([selectedDataMain['points'][i]['lon'] for i
         in range(len(selectedDataMain['points']))])
        min_latitude = min([selectedDataMain['points'][i]['lat'] for i
         in range(len(selectedDataMain['points']))])
        max_latitude = max([selectedDataMain['points'][i]['lat'] for i
         in range(len(selectedDataMain['points']))])
        df2 = df1[(df1['longitude'] <= max_longitude)
                & (df1['longitude'] >= min_longitude)
                & (df1['latitude'] <= max_latitude)
                & (df1['latitude'] >= min_latitude)]
        ships = list(df2['nom'])
        longitudes = df2["longitude"]
        latitudes = df2["latitude"]
        longitudes_span = [min(longitudes), max(longitudes)]
        latitudes_span = [min(latitudes), max(latitudes)]
        index = fi.by_value(ship_df, [date, countries, ships, longitudes_span, latitudes_span], funcs, columns)
    return index


# Indicator: No. of ships
@app.callback(Output('nbShip', 'children'), [Input('aggregate_data', 'data')])
def updateNbShip(index):

    return len(ship_df[index].nom.unique())


# Indicator: No. of Country
@app.callback(Output('nbCountry', 'children'),
              [Input('aggregate_data', 'data')])
def updateNbCountry(index):

    return len(ship_df[index].pays.unique())


# Indicator: No. of Points
@app.callback(Output('nbPoint', 'children'), [Input('aggregate_data', 'data')])
def updateNbPoint(index):

    return len(ship_df[index])


# Indicator: No. of Ports
@app.callback(Output('nbPort', 'children'), [Input('aggregate_data', 'data')])
def updateNbPort(index):

    return len(
        set(ship_df[index].port.unique())
        & set(ship_df[index].port_base.unique()))


@app.callback(Output('main_graph',
                     'figure'), [Input('aggregate_data', 'data')],
              [State('main_graph', 'relayoutData')])
def showShipTrace(index, main_graph_layout):

    traces = [dict(type='scattermapbox')]
    df = ship_df[index]
    for id_ in df.nom.unique():
        subdf = df[df['nom'] == id_]
        subdf = subdf.sort_values(by='date')
        trace = dict(
            type='scattermapbox',
            mode="markers+lines",
            #  showlegend=True,
            #  legendgroup=str(subdf.iloc[0]['classe']),
            name='Name: {}'.format(str(subdf.iloc[0]['nom'])),
            text=subdf['nom'] + '\n' + subdf['date'].dt.strftime('%Y-%m-%d'),
            # ids=list(subdf['date']),
            lon=subdf['longitude'],
            lat=subdf['latitude'],
            line={
                'opacity': 0.6,
            },
            marker={
                'size': 15,
                'opacity': 0.6,
            })
        traces.append(trace)
    layoutShip = copy.deepcopy(layout)
    layoutShip['title'] = 'Ship Trace Visualization'
    layoutShip['mapbox']['center'] = dict(lon=df.longitude.mean(),
                                          lat=df.latitude.mean())
    figure = dict(data=traces, layout=layoutShip)
    return figure


# Selectors -> count graph
@app.callback(Output('count_graph', 'figure'), [
    Input('date_selector', 'value'),
    Input('country_selector', 'value'),
    Input('ship_selector', 'value'),
    Input('main_graph', 'selectedData')
])
def make_count_figure(dates, countries, ships, selectedData):

    layout_count = copy.deepcopy(layout)
    funcs = ['by_country', 'by_name']
    columns = ['pays', 'nom']

    df = ship_df.copy()
    if not (selectedData is None) and not (len(selectedData['points']) == 0):
        df = df[(df['longitude'] == selectedData['points'][0]['lon'])
                & (df['latitude'] == selectedData['points'][0]['lat'])]
        ships = list(df['nom'])
        # index = fi.by_value(ship_df, [date, countries, ships], funcs, columns)

    df = ship_df[fi.by_value(ship_df, [countries, ships], funcs, columns)]

    if len(df) < 1:
        return []
    g = df.groupby('date').count().sort_index()

    colors = [
        'rgb(123, 199, 255)' if
        ((i - datetime.now()).days >= dates[0] and
         (i - datetime.now()).days < dates[1]) else 'rgba(123, 199, 255, 0.2)'
        for i in g.index
    ]

    data = [

        dict(
            type='bar',
            x=g.index,
            y=g['nom'],
            marker=dict(color=colors),
        ),
    ]

    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['autosize'] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# count graph
@app.callback(Output('date_selector', 'value'),
              [Input('count_graph', 'selectedData')])
def update_year_slider(count_graph_selected):
    end_index = (ship_df.date.max() - datetime.now()).days
    if count_graph_selected is None:
        return [end_index - DATERANGE, end_index]
    else:
        nums = []
        for point in count_graph_selected['points']:
            nums.append((datetime.strptime(point['x'], '%Y-%m-%d') -
                         datetime.now()).days)

        if len(nums) < 1:
            return [end_index - DATERANGE, end_index]

        return [min(nums), max(nums)]


@app.callback(
    [Output('ship_list', 'data'),
     Output('position_info', 'children')],
    [Input('main_graph', 'hoverData'),
     Input('aggregate_data', 'data')])
def update_x_timeseries(hoverData, index):
    if not hoverData:
        return pd.DataFrame({"nom": []}).to_dict('records'), "Ship List at Position: All"
        
    df = ship_df[index]
    df = df[(df['longitude'] == hoverData['points'][0]['lon'])
            & (df['latitude'] == hoverData['points'][0]['lat'])]
    df = df[['nom', 'date', 'tweet']]

    return df.to_dict("records"), "Ship List at Position:({}, {})".format(
        hoverData['points'][0]['lon'], hoverData['points'][0]['lat']),


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)

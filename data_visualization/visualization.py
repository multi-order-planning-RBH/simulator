import pandas as pd
import os, sys
sys.path.append(os.path.abspath("./"))
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

from data_visualization.config import ConfigAndShared
from data_visualization.component.rider_customer_map_renderer import rider_customer_map_renderrer
from data_visualization.utils import *

app = Dash(__name__)

slider_marker = get_slider_marker()
drop_down_options = get_drop_down_option()
number_of_riders = ConfigAndShared.NUMBER_OF_RIDERS
number_of_time_step = ConfigAndShared.NUMBER_OF_TIME_STEP

app.layout = html.Div([
    html.H4('Multiorder visualization'),
    dcc.Dropdown(
        id="multi-dropdown", 
        multi=True, 
        options = drop_down_options, 
        value = list(range(number_of_riders))
    ),
    html.Div([
        dcc.Graph(id="map", figure = go.Figure(), style={'width': '90vh', 'height': '90vh'}),
        dcc.Graph(id="map2", figure = go.Figure(), style={'width': '90vh', 'height': '90vh'}),
    ], style={'display': 'flex', 'flex-direction': 'row'}
    ),
    dcc.Slider(id="dash-slider", min=0, max=number_of_time_step-1, value=0, marks=slider_marker),
    html.Button(id="play-button", children="Play"),
    dcc.Interval(id='auto-stepper',interval=1.5*1000, n_intervals=0, disabled = True, max_intervals = number_of_time_step)
])

@app.callback(
    Output("map", "figure"),
    Output("map2", "figure"),
    Input("dash-slider", "value"),
    Input("multi-dropdown", "value"),
    State('map', 'figure')
)
def setFrame(frame, selected_rider_ids, figure):
    fig = rider_customer_map_renderrer.render(frame, selected_rider_ids, figure)
    return fig, fig

@app.callback(
    Output("dash-slider", "value"),
    Input('auto-stepper', 'n_intervals'))
def on_interval(n_intervals):
    n_intervals = n_intervals%number_of_time_step 
    return n_intervals

@app.callback(
    Output('auto-stepper', 'n_intervals'),
    Input("dash-slider", "drag_value"))
def on_drag(drag_value):
    return drag_value


@app.callback(
    Output("play-button", "children"),
    Output("auto-stepper", "disabled"),
    Input('play-button', 'n_clicks'),
    State("auto-stepper", "disabled"),)
def on_click(n_clicks, disabled):
    if disabled:
        return "Played", False
    return "Paused", True

app.run_server(debug=True, use_reloader=True, port=8050)
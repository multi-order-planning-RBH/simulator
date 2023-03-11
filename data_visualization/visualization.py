import pandas as pd
import os, sys
sys.path.append(os.path.abspath("./"))
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

from data_visualization.config import ConfigAndShared
from data_visualization.component.rider_customer_map_renderer import *
from data_visualization.component.order_time_query import *
from data_visualization.component.speed_click_handler import *
from data_visualization.utils import *

app = Dash(__name__)

slider_marker = get_slider_marker()
drop_down_options = get_drop_down_option()
number_of_riders = ConfigAndShared.NUMBER_OF_RIDERS
number_of_time_step = ConfigAndShared.NUMBER_OF_TIME_STEP

app.layout = html.Div([
    html.Div(
        [
            html.H4('Multiorder visualization',
                style = {'height': '40%', 'margin': '0px'}),
            html.Div(
            [
                dcc.Input(
                    id="order-id-input",
                    placeholder="Type order id"
                ),
                html.Button(
                    id="move-to-create", 
                    children="Created time"
                ),
                html.Button(
                    id="move-to-assigned", 
                    children="Assigned time"
                ),
                html.Button(
                    id="move-to-meal-finished-time", 
                    children="Meal finished time"
                ),
                html.Button(
                    id="move-to-picked-up", 
                    children="Picked up time"
                ),
                html.Button(
                    id="move-to-delivered", 
                    children="Delivered time"
                ),
            ], style = {
                'display': 'flex', 
                'flex-direction': 'row', 
                "justify-content": "space-between", 
                "hight": "40%",
                "witdh": "70%"}
            ),
        ],
        style={'display': 'flex', 'flex-direction': 'row', "justify-content": "space-between"}
    ),
    dcc.Dropdown(
        id="multi-dropdown", 
        multi=True, 
        options = drop_down_options, 
        value = list(range(number_of_riders))
    ),
    html.Div(
        [
            dcc.Checklist(
                id="checklist",
                options=[
                    {'label': 'Filter restaurant', 'value': FILTER_RESTAURANT},
                    {'label': 'Current destination', 'value': CURRENT_DESTINATION},
                    {'label': 'Assigned order', 'value': ASSIGNED_ORDER},
                    {'label': 'Recent suggested order', 'value': RECENT_SUGGESTED_ORDER},
                ],
                value=[FILTER_RESTAURANT, CURRENT_DESTINATION, ASSIGNED_ORDER],
                inline=True
            ),
            html.Div(
                [
                    html.Button(
                        id="x_5", 
                        children="x.5"
                    ),
                    html.Button(
                        id="x1", 
                        children="x1"
                    ),
                    html.Button(
                        id="x2", 
                        children="x2"
                    ),
                ], style = {
                    'width': "8vw",
                    'display': 'flex', 
                    'flex-direction': 'row', 
                    "justify-content": "space-between"
                }
            )
        ], 
        style={'display': 'flex', 'flex-direction': 'row', "justify-content": "space-between"}
    ),
    html.Div(
        [
            dcc.Graph(
                id="map", 
                figure = go.Figure(),
                style={'width': '98vw', 'height': '90vh'}
            ),
        ], 
        style={'display': 'flex', 'flex-direction': 'row'}
    ),
    html.Div(
        [
            html.Button(id="play-button", children="Playing"),
            html.Div(
                [
                    dcc.Slider(id="dash-slider", min=0, max=number_of_time_step-1, value=0, marks=slider_marker)
                ],
            )
        ], 
        style={'display': 'grid', "grid-template-columns": "5% 95%"}
    ),
    dcc.Interval(id='auto-stepper',interval=1*1000, n_intervals=0, disabled = True, max_intervals = number_of_time_step)
])

@app.callback(
    Output("map", "figure"),
    Input("dash-slider", "value"),
    Input("multi-dropdown", "value"),
    Input("checklist", "value"),
    Input("order-id-input", "value"),
    State('map', 'figure')
)
def setFrame(frame, selected_rider_ids, option_value, order_id, figure):
    fig = rider_customer_map_renderrer.render(frame, selected_rider_ids, option_value, order_id, figure)
    return fig

@app.callback(
    Output("auto-stepper", "interval"),
    Input('x_5', 'n_clicks'),
    Input('x1', 'n_clicks'),
    Input('x2', 'n_clicks'),
)
def on_interval(n_clicks_5, n_clicks_1, n_clicks_2):
    return speed_click_handler.speed_click_handler(n_clicks_5, n_clicks_1, n_clicks_2)


@app.callback(
    Output("dash-slider", "value"),
    Input('auto-stepper', 'n_intervals'))
def on_interval(n_intervals):
    n_intervals = n_intervals%number_of_time_step 
    return n_intervals

@app.callback(
    Output("play-button", "children"),
    Output("auto-stepper", "disabled"),
    Input('play-button', 'n_clicks'),
    State("auto-stepper", "disabled"),)
def on_click(n_clicks, disabled):
    if disabled:
        return "Playing", False
    return "Paused", True

@app.callback(
    Output('auto-stepper', 'n_intervals'),
    Input("dash-slider", "drag_value"),
    Input('order-id-input', 'value'),
    Input('move-to-create', 'n_clicks'),
    Input('move-to-assigned', 'n_clicks'),
    Input('move-to-meal-finished-time', 'n_clicks'),
    Input('move-to-picked-up', 'n_clicks'),
    Input('move-to-delivered', 'n_clicks'),
)
def on_click(drag_value, order_id,
    move_to_create_time_click,
    move_to_assigned_time_click,
    move_to_meal_finished_time_click,
    move_to_picked_up_time_click,
    move_to_finished_time_click
    ):
    set_value = drag_value
    set_value = order_time_query.move_to_create(order_id, move_to_create_time_click, set_value)
    set_value = order_time_query.move_to_assigned(order_id, move_to_assigned_time_click, set_value)
    set_value = order_time_query.move_to_meal_finished_time(order_id, move_to_meal_finished_time_click, set_value)
    set_value = order_time_query.move_to_picked_up(order_id, move_to_picked_up_time_click, set_value)
    set_value = order_time_query.move_to_finished(order_id, move_to_finished_time_click, set_value)
    try:
        set_value = round(set_value)
    except:
        set_value = 0
    return set_value%number_of_time_step 

app.run_server(debug=True, use_reloader=True, port=8050)
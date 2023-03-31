import pandas as pd
import os, sys
sys.path.append(os.path.abspath("./"))
import plotly.graph_objects as go
import plotly.express as px

from dash import Dash, dcc, html, Input, Output, State

from data_visualization.visconfig import ConfigAndShared
from data_visualization.component.rider_customer_map_renderer import *
from data_visualization.component.order_time_query import *
from data_visualization.component.speed_click_handler import *
from data_visualization.utils import *

from datetime import datetime


app = Dash(__name__)

slider_marker = get_slider_marker()
drop_down_options = get_drop_down_option()
number_of_riders = ConfigAndShared.NUMBER_OF_RIDERS
number_of_time_step = ConfigAndShared.NUMBER_OF_TIME_STEP

order_df = ConfigAndShared.ORDER_DF
order_df["Customer Waiting Time (minutes)"]=((order_df["finished_time"]-order_df["created_time"])/60)

rbh_df = ConfigAndShared.RBH_DF
rbh_df["arrivedAtCustLocationTime"]=rbh_df["arrivedAtCustLocationTime"].apply(lambda time_str: datetime.strptime(time_str, '%H:%M:%S'))
rbh_df["jobAcceptedTime"]=rbh_df["jobAcceptedTime"].apply(lambda time_str: datetime.strptime(time_str, '%H:%M:%S'))
rbh_df["Customer Waiting Time (minutes)"]=(rbh_df["arrivedAtCustLocationTime"]-rbh_df["jobAcceptedTime"]).apply(lambda x: x.total_seconds())/60

waiting_time_q3=rbh_df["Customer Waiting Time (minutes)"].quantile(0.75)
waiting_time_q1=rbh_df["Customer Waiting Time (minutes)"].quantile(0.25)
waiting_time_iqr = waiting_time_q3-waiting_time_q1
waiting_time_upper_bound = waiting_time_q3+1.5*waiting_time_iqr

num_huge_waiting_time = sum(order_df["Customer Waiting Time (minutes)"]>waiting_time_upper_bound)

rider_summary_df = ConfigAndShared.RIDER_SUMMARY_DF
rider_summary_df['Utilization time (minutes)'] = rider_summary_df['utilization_time'] / 60

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
                    {'label': 'Show restaurant area', 'value': SHOW_RESTAURANT_AREA},
                    {'label': 'Show customer area', 'value': SHOW_CUSTOMER_AREA},
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
    dcc.Interval(id='auto-stepper',interval=1*1000, n_intervals=0, disabled = True, max_intervals = number_of_time_step),

    html.Div(
        [
            html.H3('Stats visualization',
                style = {'height': '40%', 'margin-top': '30px'}),
            html.H4('Customers Waiting Time distribution',
                style = {'height': '40%', 'margin-top': '10px','margin-left':'10px'}),
            html.H5('Box plot of RBH original data',
                style = {'height': '40%', 'margin-top': '10px','margin-left':'20px'}),
            dcc.Graph(id="rbh-box-plot"),
            html.Div(id="dummy-boxplot"),
            html.H5('Histogram of generated data',
                style = {'height': '40%', 'margin-top': '10px','margin-left':'20px'}),
            dcc.Graph(id="customer-waiting-time-hist"),
            html.Div(id="dummy"),
            html.Div([
            html.H2(str(round(num_huge_waiting_time/len(order_df)*100,2))+" % of orders take too much time!!",style={"color":"red"})]
            ,style={"display":"flex","justify-content": "center"}),

            html.H5('Histogram of rider utilization time',
                style = {'height': '40%', 'margin-top': '10px','margin-left':'20px'}),
            dcc.Graph(id="rider-utilization-time-hist"),
            html.Div(id="dummy-input-rider-utilization-time")
        ], 
    ),
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


@app.callback(
    Output('rbh-box-plot', 'figure'),
    Input('dummy-boxplot', 'id')
)
def display_color(dummy_input):

    fig = px.box(order_df, range_x=[0,  order_df["Customer Waiting Time (minutes)"].max()+10],x="Customer Waiting Time (minutes)")
    fig.add_vline(x=waiting_time_upper_bound,line_dash="dash", line_color="red",annotation_text="Upper bound of customer waiting time",annotation_font_color="red")

    return fig

@app.callback(
    Output('customer-waiting-time-hist', 'figure'),
    Input('dummy', 'id')
)
def display_color(dummy_input):

    fig = px.histogram(order_df, range_x=[0,  order_df["Customer Waiting Time (minutes)"].max()+10],x="Customer Waiting Time (minutes)",histnorm='percent')
    
    fig.add_vline(x=waiting_time_upper_bound,line_dash="dash", line_color="red",annotation_text="Upper bound from boxplot",annotation_font_color="red")
    return fig

@app.callback(
    Output('rider-utilization-time-hist', 'figure'),
    Input('dummy-input-rider-utilization-time', 'id')
)
def display_color(dummy_input):
    fig = px.histogram(rider_summary_df, x="Utilization time (minutes)", nbins=5, histnorm='percent')
    return fig

app.run_server(debug=True, use_reloader=True, port=8050)
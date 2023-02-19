import pandas as pd

import plotly.graph_objects as go

from data_visualization.config import ConfigAndShared

rider_df = ConfigAndShared.RIDER_LOCAITON_DF
rider_color = ConfigAndShared.RIDER_COLOR
destination_df = ConfigAndShared.RIDER_DESTINATION_DF
order_df = ConfigAndShared.ORDER_DF
customer_color = ConfigAndShared.CUSTOMER_COLOR
restaurant_df = ConfigAndShared.RESTAURANT_DF
restaurant_color = ConfigAndShared.RESTAURANT_COLOR
selected_order_df:pd.DataFrame = None
selected_riders_df:pd.DataFrame = None
colors  = ConfigAndShared.COLORS
gold_color = ConfigAndShared.GOLD_COLOR

FILTER_RESTAURANT = "FILTER_RESTAURANT"
CURRENT_DESTINATION = "CURRENT_DESTINATION"
ASSIGNED_ORDER = "ASSIGNED_ORDER"

def add_rider(fig:go.Figure, time:int, rider_ids:list):
    global selected_riders_df
    selected_riders_df = rider_df[rider_df['time'] == time]
    selected_riders_df = selected_riders_df[selected_riders_df['id'].isin(rider_ids)]

    n = len(selected_riders_df)
    for i in range(n):
        id, lat, lng, action = selected_riders_df.iloc[i][['id', 'lat', 'lng', 'action']]
        fig.add_trace(
            go.Scattermapbox(
                lat=[lat],
                lon=[lng],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=5,
                    color=rider_color
                ),
                text=['Rider ID: {}\n Current: {}'.format(int(id), action)],
                showlegend=False
            )
        )
    return fig

def add_customer(fig:go.Figure, time:int, rider_ids:list, order_id:int, assigned_order:bool):

    selection_clause = (order_df['created_time'] <= time) & (time <= order_df['finished_time']) &\
        (order_df['rider_id'].isin(rider_ids))
    if assigned_order:
        selection_clause = selection_clause & (order_df['assigned_time']<=time)
    global selected_order_df
    selected_order_df = order_df[selection_clause]

    n = len(selected_order_df)
    for i in range(n):
        id, lat, lon= selected_order_df.iloc[i][['id', 'customer_location_lat', 'customer_location_lng']]
        fig.add_trace(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=6,
                    color=customer_color if id != order_id else gold_color
                ),
                text=['Order ID: {}\n'.format(int(id))],
                showlegend=False
            )
        )
    return fig

def add_restaurant(fig:go.Figure, filter_time:bool, order_id:int):
    selected_restaurant_id = None
    global selected_order_df
    if filter_time :
        selected_id = selected_order_df['restaurant_id'].unique()
        try:
            selected_restaurant_id = (selected_order_df[selected_order_df['id']==order_id]['restaurant_id']).item()
        except:
            selected_restaurant_id = None
        selected_df = restaurant_df[restaurant_df['id'].isin(selected_id)]
    else:
        selected_df = restaurant_df

    n = len(selected_df)
    for i in range(n):
        id, lat, lon= selected_df.iloc[i][['id', 'lat', 'lng']]
        fig.add_trace(
            go.Scattermapbox(
                lat=[lat],
                lon=[lon],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=7,
                    color=restaurant_color if id != selected_restaurant_id else gold_color
                ),
                text=['Restaurant ID: {}\n'.format(int(id))],
                showlegend=False
            )
        )
    return fig

def add_destination(fig:go.Figure, time:int, rider_ids:list, current_dest:bool):
    selected_destination_df = destination_df.loc[destination_df['time'] == time]
    selected_destination_df = selected_destination_df.loc[selected_destination_df['id'].isin(rider_ids)]
    selected_df = selected_riders_df.merge(selected_destination_df,suffixes = ['_rider', '_destination'], 
                                on = ['id', 'time'], how = "left")
    selected_df = selected_df.dropna(axis='index')
    n = len(selected_df)

    count, temp_id = 0, None
    for i in range(n):
        id = selected_df.iloc[i]['id']
        if current_dest and temp_id == id:
            continue
        count = count+1 if temp_id == id else 1
        temp_id = id
        dest_type = selected_df.iloc[i]['destination_type']
        lat_rider,lng_rider = selected_df.iloc[i]['lat_rider'], selected_df.iloc[i]['lng_rider']
        lat_dest,lng_dest = selected_df.iloc[i]['lat_destination'], selected_df.iloc[i]['lng_destination']

        fig.add_trace(
            go.Scattermapbox(
                lat=[lat_rider, lat_dest],
                lon=[lng_rider, lng_dest],
                mode="lines",
                line=go.scattermapbox.Line(
                    width=1/count,
                    color=colors[id],
                ),
                name='Rider: {} Dest: {}'.format(id, count),
                text='Destination: {} \nRider: {} Dest: {}'.format(dest_type, id, count)
            )
        )

    return fig


class RiderCustomerMapRenderer():
    def __init__(self):

        self.df = ConfigAndShared.RIDER_LOCAITON_DF.merge(ConfigAndShared.RIDER_DESTINATION_DF,
                                suffixes = ['_rider', '_destination'], 
                                on = ['id', 'time'], how = "left")

    def render(self, frame, selected_rider_ids, option_value, order_id, figure):

        time = frame*30
        
        figure_state = figure
        figure_state['data'] = []
        try:
            order_id  = int(order_id)
        except:
            order_id = -1
        fig = go.Figure(figure_state)
        fig = add_rider(fig, time, selected_rider_ids)
        fig = add_customer(fig, time, selected_rider_ids, order_id, ASSIGNED_ORDER in option_value)
        fig = add_restaurant(fig, FILTER_RESTAURANT in option_value, order_id)
        fig = add_destination(fig, time, selected_rider_ids, CURRENT_DESTINATION in option_value)
        
        if frame == 0:
            fig.update_layout(
                mapbox_style="carto-positron",
                margin={"r":0,"t":0,"l":0,"b":0},
                mapbox={'center': go.layout.mapbox.Center(lat=13.8268, lon=100.5683), 'zoom': 12}
            )
        
        return fig

rider_customer_map_renderrer = RiderCustomerMapRenderer()

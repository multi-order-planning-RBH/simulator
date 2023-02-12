import plotly.graph_objects as go
from dash import dcc

from data_visualization.config import ConfigAndShared

class RiderCustomerMapRenderer():
    def __init__(self):

        self.df = ConfigAndShared.LOCAITON_DF.merge(ConfigAndShared.DESTINATION_DF,
                                suffixes = ['_rider', '_destination'], 
                                on = ['id', 'time'], how = "left")
        self.colors  = ConfigAndShared.COLORS

    def render(self, frame, selected_rider_ids, figure):

        t = frame*30
        select_clause = (self.df['time'] == t) & (self.df['id'].isin(selected_rider_ids))
        selected_df = self.df[select_clause]

        id = list(selected_df['id'])
        destination_type = list(selected_df['destination_type'])
        lats_rider = list(selected_df['lat_rider'])
        longs_rider = list(selected_df['long_rider'])
        lats_destination = list(selected_df['lat_destination'])
        longs_destination = list(selected_df['long_destination'])
        n = len(lats_rider)
        
        figure_state = figure
        figure_state['data'] = []
        fig = go.Figure(figure_state)

        for i in range(n):
            if id[i] not in selected_rider_ids:
                continue
            fig.add_trace(
                go.Scattermapbox(
                    lat=[lats_rider[i], lats_destination[i]],
                    lon=[longs_rider[i], longs_destination[i]],
                    mode="markers+lines",
                    marker=go.scattermapbox.Marker(
                        size=5,
                        color=self.colors[id[i]]
                    ),
                    line=go.scattermapbox.Line(
                        width=0.5,
                        color=self.colors[id[i]],
                    ),
                    text=['Rider {}'.format(id[i]), destination_type[i]],
                )
            )
        if frame == 0:
            fig.update_layout(
                mapbox_style="carto-positron",
                margin={"r":0,"t":0,"l":0,"b":0},
                mapbox={'center': go.layout.mapbox.Center(lat=13.8268, lon=100.5683), 'zoom': 11}
            )
        
        return fig

rider_customer_map_renderrer = RiderCustomerMapRenderer()

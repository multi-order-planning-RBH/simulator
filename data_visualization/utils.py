from data_visualization.config import ConfigAndShared
from dash import html

def get_slider_marker():
    return {i:str(i*30) for i in range(0, ConfigAndShared.NUMBER_OF_TIME_STEP, 10)}

def get_drop_down_option():
    return [{
        "label": html.Span(['Rider {}'.format(i)], style={'color': ConfigAndShared.COLORS[i]}),
        "value": i,
        } for i in range(ConfigAndShared.NUMBER_OF_RIDERS)
    ]  
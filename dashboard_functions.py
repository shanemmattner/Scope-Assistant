import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html


def parse_contents(df, sample_rate):
    try:
        pts = len(df)
        xAxis = np.linspace(0,(pts/sample_rate), pts) 
        #create empty list for putting traces in
        traces = []
        for col in df:
            #TODO: add to different axis depending on the highest value of the signals
            traces.append(go.Scattergl(x=xAxis,y=df[col],mode='lines',name=str(col),opacity=0.8))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return html.Div([
        dcc.Graph(figure = go.Figure(data=traces[:]))
    ])

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import RIGOL_DS1104Z as rg

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
    fig =  go.Figure(data=traces[:])
    fig.update_layout(
            xaxis_title = "Time (s)",
            yaxis_title = "Volts (V)"
            )
    return html.Div([
        dcc.Graph(figure = fig)
        ])

def calc_query_req(frmt, mDepth):
        if frmt == 'BYTE':
            maxReadsPerQuery = 250000
        elif frmt == 'WORD':
            maxReadsPerQuery = 125000
        elif frmt == 'ASC':
            maxReadsPerQuery = 15625
        else:
            maxReadsPerQuery = 15625
        return (int(int(mDepth) /int( maxReadsPerQuery)) + 1), maxReadsPerQuery


def create_options(dfCol):
    i = 0
    lstBuf = []
    for row in dfCol:
        if row != "NULL":
            lstBuf.append({'label':row, 'value':i})
        i = i + 1
    return lstBuf

import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import RIGOL_DS1104Z as rg
import math

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
            yaxis_title = "Volts (V)",
            showlegend = True
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


def to_si(d, sep= ' '):
    #convert number to string with SI prefix

    incPrefixes = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    decPrefixes = ['m', 'u', 'n', 'p', 'f', 'a', 'z', 'y']

    if d == 0:
        return str(0)

    degree = int(math.floor(math.log10(math.fabs(d))/3))
    prefix = ''
    if degree != 0:
        ds = degree/math.fabs(degree)
        if ds == 1:
            if degree -1 < len(incPrefixes):
                prefix = incPrefixes[degree -1]
            else:
                prefix = incPrefixes[-1]
                degree = len(incPrefixes)

        elif ds == -1:
            if -degree -1 < len(decPrefixes):
                prefix = decPrefixes[-degree -1]
            else:
                prefix = decPrefixes[-1]
                degree = -len(decPrefixes)

        scaled = float(d * math.pow(1000, -degree))

        s = "{scaled}{sep}{prefix}".format(scaled = scaled,sep = sep, prefix = prefix)

    else:
        s = "{d}".format(d=d)
    s = s + "Sa/s"
    return(s)


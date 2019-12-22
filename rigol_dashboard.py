#ip installed imports
import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from time import sleep
#user created imports
import RIGOL_DS1104Z as rg
from os import chdir
import visa
from os import system
import plotly.graph_objs as go

chdir("/home/pi/dashboard/Scope-Assistant")
#import Rite-Hite logo and encode as base 64
scope_pic = base64.b64encode(open('ds1104z.png', 'rb').read()) 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#import styling
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#create the server
server = app.server
app.config.suppress_callback_exceptions = True #prevents errors if we reference components before they're defined

def parse_contents(df):
    try:
        xAxis = df['Time']
        df.drop(['Time'], axis = 1, inplace = True)
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

#BUTTONS
btn1 = html.Button('Trigger / Get Data', id='btn-1', n_clicks=0)

'''*************************************************************************'''
#CHECKLISTS
checklist1 = dcc.Checklist(
                id = 'oscillChannelList',
                options=[
                     {'label': 'Channel 1', 'value': '1'},
                     {'label': 'Channel 2', 'value': '2'},
                     {'label': 'Channel 3', 'value': '3'},
                     {'label': 'Channel 4', 'value': '4'}],
                value=['1'])
'''*************************************************************************'''
memDepthImport = pd.read_csv('memoryDepth.csv')
i = 0
memDepthOptions = []
for row in memDepthImport['oneChannel']:
    if row != 'NULL':
        memDepthOptions.append({'label':row, 'value':i})
    i = i + 1

#RADIO ITEMS
radioList1 = dcc.RadioItems(
        id = 'memDepthList',
        options = memDepthOptions,
        value = 4)
'''*************************************************************************'''
#TABS
tabs = dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='DS1104Z', value='tab-1')
])
'''*************************************************************************'''
app.layout = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(scope_pic.decode()), width = 200),
    html.Div([
        html.Div([
            tabs,
            html.Div(id = 'tabs-content')],
            className="three columns" ),
        html.Div([
            html.Div(id = 'output')],
            className="nine columns"),], 
        className="row")])



#function which manages content displayed in tabs 
#When each tab is chosen we replace the main Div 'output' with a specific Div for this tab
#ie tab1-output, tab2-output, tab3-output
@app.callback([Output('tabs-content', 'children'), Output("output","children")],
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        child1 = html.Div([
                        html.H3('Channels'),
                        checklist1,
                        html.H3('Sampling Rate'),
                        radioList1,
                        btn1],
                    style = {'overflow':'auto','height':'80vh'})
        child2 = html.Div(id = 'tab1-output')
        return child1, child2


#define function for Button 2
#Oscilloscope app
@app.callback(Output('tab1-output', 'children'),
              [Input('btn-1', 'n_clicks')],
              [State('oscillChannelList', 'value'), State('memDepthList', 'value')])
#start the signal plotter script
def button1(clicks, CH, mDepth):
    #prevent the scope from triggering upon entering application before button is clicked
    #also guard against users trying to get data with no channels selected
    if (clicks == 0) or (len(CH) == 0):
        return
    system('clear')
    #get the memory depth
    if len(CH) == 1:
        depth = memDepthImport.iloc[mDepth]['oneChannel']
        print("MEMORY DEPTH: " + str(depth))
    elif len(CH) == 2:
        depth = memDepthImport.iloc[mDepth]['twoChannels']
        print("MEMORY DEPTH: " + str(depth))
    else:
        depth = memDepthImport.iloc[mDepth]['threeFourChannels']
        print("MEMORY DEPTH: " + str(depth))

    scope=rg.RIGOL_DS1104Z()
    data = pd.DataFrame()
    scope.initialize_scope(channel = CH, memDepth = depth)
    print("Channels Initialized")
    print("Triggering Single")
    print(scope.wave_source_get())
    print(scope.acquire_depth_get())
    scope.single()
    sleep(1)
    #wait until the scope is done with it's trigger
    scope_status = scope.trigger_status()
    while "STOP" not in scope_status:
        sleep(0.3)
        scope_status = scope.trigger_status()
    print("Trigger event complete\n")
    
    
    for i in CH:
        data['CH' + str(i)] = scope.channel_data_return(int(i))
    #now we have all the channel data, let's generate an x-axis
    pts = len(data)
    srate = scope.acquire_srate_get()
    data['Time']=np.linspace(0,(pts/srate), pts)
    #the 'Time' column is at the end of the dataframe, let's move it to the first column
    cols = data.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    data = data[cols]
    return parse_contents(data)
    #return html.Div(["succuss!"])
    
@app.callback(Output('memDepthList','options'),
            [Input('oscillChannelList','value')])
def memDepthOptions(CH):
    if len(CH) <= 1:
        i = 0
        mDepthOptions = []
        for row in memDepthImport['oneChannel']:
            if row != 'NULL':
                mDepthOptions.append({'label':row, 'value':i})
            i = i + 1
        return mDepthOptions
    elif len(CH) == 2:
        i = 0
        mDepthOptions = []
        for row in memDepthImport['twoChannels']:
            if row != 'NULL':
                mDepthOptions.append({'label':row, 'value':i})
            i = i + 1
        return mDepthOptions
    else:
        i = 0
        mDepthOptions = []
        for row in memDepthImport['threeFourChannels']:
            if row != 'NULL':
                mDepthOptions.append({'label':row, 'value':i})
            i = i + 1
        return mDepthOptions

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)

#ip installed imports
import base64
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import numpy as np
from os import chdir, system
import pandas as pd
#import plotly.graph_objs as go
from time import sleep
import visa
#user created imports
import dashboard_functions as dbf
import RIGOL_DS1104Z as rg

chdir("/home/pi/dashboard/Scope-Assistant")
#import Rite-Hite logo and encode as base 64
scope_pic = base64.b64encode(open('ds1104z.png', 'rb').read()) 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#import styling
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#create the server
server = app.server
app.config.suppress_callback_exceptions = True #prevents errors if we reference components before they're defined

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

#RADIO ITEMS
radioList1 = dcc.RadioItems(
        id = 'memDepthList')
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
    if (clicks == 0) or (len(CH) == 0) or (str(type(mDepth)) == "<class 'NoneType'>"):
        return
    system('clear')
    #get the memory depth
    if len(CH) == 1:
        depth = memDepthImport.iloc[mDepth]['oneChannel']
    elif len(CH) == 2:
        depth = memDepthImport.iloc[mDepth]['twoChannels']
    else:
        depth = memDepthImport.iloc[mDepth]['threeFourChannels']

    scope=rg.RIGOL_DS1104Z()
    data = pd.DataFrame() #make an empty dataframe where the data will go
    scope.initialize_scope(channel = CH, memDepth = depth) #initialize the scope and channels
    scope.single()
    sleep(1)
    #wait until the scope is done with it's trigger
    scope_status = scope.trigger_status()
    while "STOP" not in scope_status:
        sleep(0.3)
        scope_status = scope.trigger_status()
    for i in CH:
        data['CH' + str(i)] = scope.channel_data_return(int(i))
    #now we have all the channel data, let's generate an x-axis
    sample_rate = scope.acquire_srate_get()
    return dbf.parse_contents(data, sample_rate) #
    #return html.Div(["succuss!"])
    
@app.callback(Output('memDepthList','options'),
            [Input('oscillChannelList','value')])
def memDepthOptions(CH):
    scope = rg.RIGOL_DS1104Z()
    scope.get_USB_port()
    time_scale = float(scope.time_scale_get())
    divisions = 12 #there are 12 divisions on the Rigol DS1104Z screen
    total_time = time_scale * divisions
    #get the time scale
    if len(CH) <= 1:
        sRateCol = (memDepthImport['oneChannel'] / total_time).apply(lambda x : "{:,}".format(x))# format the sampling rate with commas
        return (dbf.create_options(sRateCol))
    elif len(CH) == 2:
        sRateCol = (memDepthImport['twoChannels'] / total_time).apply(lambda x : "{:,}".format(x))
        return (dbf.create_options(sRateCol))
    else:
        sRateCol = (memDepthImport['threeFourChannels'] / total_time).apply(lambda x : "{:,}".format(x))
        return (dbf.create_options(sRateCol))
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)

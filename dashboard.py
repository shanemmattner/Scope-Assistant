#ip installed imports
import base64
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import numpy as np
import os
from os import chdir, system
import pandas as pd
import sqlite3
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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#create the server
server = app.server
app.config.suppress_callback_exceptions = True #prevents errors if we reference components before they're defined

#BUTTONS
btn_trigger = html.Button('Trigger', id='btn-trig', n_clicks=0, style={'padding':'30px 100px', 'boarder-radius':'10px'})
btn_update_sRate = html.Button('Update', id='btn-uSrate',n_clicks=0, style={'padding':'10px 20px'})
'''*************************************************************************'''

#CHECKLISTS
channel_checklist = dcc.Checklist(
                id = 'chkLst_channels',
                options=[
                     {'label': 'Channel 1', 'value': '1'},
                     {'label': 'Channel 2', 'value': '2'},
                     {'label': 'Channel 3', 'value': '3'},
                     {'label': 'Channel 4', 'value': '4'}],
                value=['1'],
                labelStyle={'display':'vertical'})
'''*************************************************************************'''
memDepthImport = pd.read_csv('memoryDepth.csv')

#RADIO ITEMS
radio_sampleRate = dcc.RadioItems(
        id = 'radio_sRate')
'''*************************************************************************'''
channel_labels = dbc.Col([
                    dcc.Input(id="channel_1", type="text", value = "Channel 1", style={'width':100}),
                    dcc.Input(id="channel_2", type="text", value = "Channel 2", style={'width':100}),
                    dcc.Input(id="channel_3", type="text", value = "Channel 3", style={'width':100}),
                    dcc.Input(id="channel_4", type="text", value = "Channel 4", style={'width':100})
                    ])


header = html.Div([
    html.Img(src='data:image/png;base64,{}'.format(scope_pic.decode()), width = 200)])

col1_row1 = dbc.Row([
                html.H5("Rigol DS1104Z+"),
                html.H5("Scope Assistant v0.2")
                ],
                justify = "center")


col1_row2 = dbc.Row([
                html.H6("Channels",
                    style={
                        'textAlign':'left',
                        'padding-right':'100px'}),
                html.H6("Labels")],
                justify = "center")

col1_row3 = dbc.Row([
                dbc.Col([
                    channel_checklist],
                width={'size':4, "offset":3}),
                channel_labels])

col1_row4 = dbc.Row([
                html.H4("Sampling Rate")],
                justify = "center")


col1_row5 = dbc.Row([
                dbc.Col([
                    radio_sampleRate],
                width={'size':4, "offset":3}),
                html.Div([html.Div(""),btn_update_sRate])]) #we're doing this weird placement because otherwise the button strecthes to the size of the radio buttons


col1_row6 = dbc.Row([
                btn_trigger],
                justify = "center")



column1 =  dbc.Col(html.Div([col1_row1,
                             col1_row2,
                             col1_row3,
                             col1_row4,
                             col1_row5,
                             col1_row6], 
                        id = 'userInputDiv'), width = 3)

column2 =  dbc.Col(html.Div("column2", id = 'outputDiv'), width = 9)

row1 = html.Div([
            dbc.Row([
                column1,
                column2]),
                ])


app.layout = html.Div([
                    header,
                    row1
                     ])

#define function for Button 2
#Oscilloscope app
@app.callback(Output('outputDiv', 'children'),
              [Input('btn-trig', 'n_clicks')],
              [State('chkLst_channels', 'value'), State('radio_sRate', 'value'), State('channel_1', 'value'), State('channel_2', 'value'), State('channel_3', 'value'), State('channel_4', 'value')])
#start the signal plotter script
def button1(clicks, CH, mDepth, ch1_label, ch2_label, ch3_label, ch4_label):
    #prevent the scope from triggering upon entering application before button is clicked
    #also guard against users trying to get data with no channels selected
    if (clicks == 0) or (len(CH) == 0) or (str(type(mDepth)) == "<class 'NoneType'>"):
        return
    system('clear')
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
        if int(i) == 1:
            data[ch1_label] = scope.channel_data_return(int(i))
        elif int(i) == 2:
            data[ch2_label] = scope.channel_data_return(int(i))
        elif int(i) == 3:
            data[ch3_label] = scope.channel_data_return(int(i))
        else:
            data[ch4_label] = scope.channel_data_return(int(i))
    
    
    sample_rate = scope.acquire_srate_get()
    return dbf.parse_contents(data, sample_rate)
    
@app.callback(Output('radio_sRate','options'),
            [Input('chkLst_channels','value'), Input('btn-uSrate', 'n_clicks')])
def memDepthOptions(CH, u_clicks):
   # if u_clicks == 0:
    #    return
    scope = rg.RIGOL_DS1104Z()
    scope.get_USB_port()
    time_scale = float(scope.time_scale_get())
    divisions = 12 #there are 12 divisions on the Rigol DS1104Z screen
    total_time = time_scale * divisions
    #get the time scale
    if len(CH) <= 1:
        srate = (memDepthImport['oneChannel'] / total_time).round()
        lst = []
        for i in srate:
            lst.append(dbf.to_si(i))
        return (dbf.create_options(lst))
    elif len(CH) == 2:
        srate = (memDepthImport['twoChannels'] / total_time).round()
        lst = []
        for i in srate:
            lst.append(dbf.to_si(i))
        return (dbf.create_options(lst))
    else:

        srate = (memDepthImport['threeFourChannels'] / total_time).round()
        lst = []
        for i in srate:
            lst.append(dbf.to_si(i))
        return (dbf.create_options(lst))
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)

#ip installed imports
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
import dashboard_html as dbh
import RIGOL_DS1104Z as rg

chdir("/home/pi/dashboard/Scope-Assistant")
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True #prevents errors if we reference components before they're defined

memDepthImport = pd.read_csv('memoryDepth.csv')

app.layout = html.Div([
                    dbh.header,
                    dbh.row_1
                     ])

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
    scope = rg.RIGOL_DS1104Z()
    scope.get_USB_port()
    time_scale = float(scope.time_scale_get())
    divisions = 12 #there are 12 divisions on the Rigol DS1104Z screen
    total_time = time_scale * divisions
    #get the time scale options based on the number of channels selected
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

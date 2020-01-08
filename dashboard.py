#ip installed imports
import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import numpy as np
from os import chdir, system
import pandas as pd
import sqlite3
from time import sleep
import visa
#user created imports
import dashboard_db as dbdb
import dashboard_functions as dbf
import dashboard_html as dbh
import RIGOL_DS1104Z as rg

chdir("/home/pi/dashboard/Scope-Assistant")
system('clear')

memDepthImport = pd.read_csv('memoryDepth.csv')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True #prevents errors if we reference components before they're defined
app.layout = html.Div([
                    dbh.header,
                    dbh.row_1
                     ])

@app.callback(Output('outputDiv', 'children'),
              [Input('btn-trig', 'n_clicks')],
              [State('chkLst_CH1','value'), State('chkLst_CH2','value'), State('chkLst_CH3','value'), State('chkLst_CH4','value'), State('radio_sRate', 'value'), State('channel_1', 'value'), State('channel_2', 'value'), State('channel_3', 'value'), State('channel_4', 'value'), State('desc','value')])
#start the signal plotter script
def button1(clicks, CH1, CH2, CH3, CH4, mDepth, ch1_label, ch2_label, ch3_label, ch4_label, description):
    buf=[CH1,CH2,CH3,CH4]
    CH=[]
    for i in buf:
        if i:
            CH.append(i[0]) 
    #prevent the scope from triggering upon entering application before button is clicked
    #also guard against users trying to get data with no channels selected
    if (clicks == 0) or (len(CH) == 0) or (str(type(mDepth)) == "<class 'NoneType'>"):
        return

    if len(CH) == 1:
        depth = memDepthImport.iloc[mDepth]['oneChannel']
    elif len(CH) == 2:
        depth = memDepthImport.iloc[mDepth]['twoChannels']
    else:
        depth = memDepthImport.iloc[mDepth]['threeFourChannels']
    print("depth: " + str(depth))
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
        print("getting data from channel " + str(i))
        scope_data = scope.channel_data_return(int(i))
        print("length of scope data = " + str(len(scope_data)))
        if int(i) == 1:
            data[ch1_label] = scope_data
        elif int(i) == 2:
            data[ch2_label] = scope_data
        elif int(i) == 3:
            data[ch3_label] = scope_data
        else:
            data[ch4_label] = scope_data
    sample_rate = scope.acquire_srate_get() #get sample rate for calculating x axis
    data['Time'] = np.linspace(0,(len(data)/sample_rate), len(data))# make the time axis
    dbdb.create_table(dbdb.connect(), data)
    #add an entry to the desc table
    dbdb.add_desc_entry(dbdb.connect(), description, sample_rate) 
    df_test = dbdb.retrieve_table(dbdb.connect())
    print(dbdb.list_tables(dbdb.connect()))
    #return dbf.create_fig(df_test)
   
    return []


@app.callback([Output('radio_sRate','options'),Output('radio_sRate','value')],
            [Input('chkLst_CH1','value'), Input('chkLst_CH2','value'), Input('chkLst_CH3','value'),Input('chkLst_CH4','value'),Input('btn-uSrate', 'n_clicks')],
            [State('radio_sRate','value')])
def memDepthOptions(CH1, CH2, CH3, CH4, u_clicks,sRate):
    buf=[CH1,CH2,CH3,CH4]
    CH=[]
    for i in buf:
        if i:
            CH.append(i[0])
    #if the user has selected a sampling rate then sRate will not be 'None'
    if str(sRate) == 'None':
        usr_sel = 4 #set the user selected sampling rate to lowest if nothing is selected
    else:
        usr_sel = sRate
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
        return (dbf.create_options(lst), usr_sel)
    elif len(CH) == 2:
        srate = (memDepthImport['twoChannels'] / total_time).round()
        lst = []
        for i in srate:
            lst.append(dbf.to_si(i))
        return (dbf.create_options(lst), usr_sel)
    else:
        srate = (memDepthImport['threeFourChannels'] / total_time).round()
        lst = []
        for i in srate:
            lst.append(dbf.to_si(i))
        return (dbf.create_options(lst), usr_sel)
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)

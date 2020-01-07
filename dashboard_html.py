import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import base64
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

channel_checklist_1 = dcc.Checklist(
                id = 'chkLst_CH1',
                options = [{'label': 'Channel 1 ', 'value': '1'}],
                style = {'font-weight':'bold', 'font-size':'200%'}
                )
channel_checklist_2 = dcc.Checklist(
                id = 'chkLst_CH2',
                options = [{'label': 'Channel 2 ', 'value': '3'}],
                style = {'font-weight':'bold', 'font-size':'200%'}
                )

channel_checklist_3 = dcc.Checklist(
                id = 'chkLst_CH3',
                options = [{'label': 'Channel 3 ', 'value': '3'}],
                style = {'font-weight':'bold', 'font-size':'200%'}
                )
channel_checklist_4= dcc.Checklist(
                id = 'chkLst_CH4',
                options = [{'label': 'Channel 4 ', 'value': '4'}],
                style = {'font-weight':'bold', 'font-size':'200%'}
                )

#BUTTONS
btn_trigger = html.Button('Trigger', id='btn-trig', n_clicks=0, style={'padding':'30px 100px', 'boarder-radius':'10px'})
btn_update_sRate = html.Button('Update', id='btn-uSrate',n_clicks=0, style={'padding':'10px 20px'})
'''*************************************************************************'''


#RADIO ITEMS
radio_sRate = dcc.RadioItems(
        id = 'radio_sRate')
'''*************************************************************************'''

channel_labels = dbc.Col([
                    dbc.Row([dcc.Input(id="channel_1", type="text", value = "Signal 1", style={'width':300, 'height':75})]),
                    dbc.Row([dcc.Input(id="channel_2", type="text", value = "Signal 2", style={'width':300, 'height':75})]),
                    dbc.Row([dcc.Input(id="channel_3", type="text", value = "Signal 3", style={'width':300, 'height':75})]),
                    dbc.Row([dcc.Input(id="channel_4", type="text", value = "Signal 4", style={'width':300, 'height':75})])
                    ])

channel_chkLst = dbc.Col([
                        dbc.Row([channel_checklist_1],justify = "end", align = "center", style={'height':75}),                
                        dbc.Row([channel_checklist_2],justify = "end", align = "center", style={'height':75}),                
                        dbc.Row([channel_checklist_3],justify = "end", align = "center", style={'height':75}),                
                        dbc.Row([channel_checklist_4],justify = "end", align = "center", style={'height':75})              
                        ])


scope_pic = base64.b64encode(open('ds1104z.png', 'rb').read()) 
header = dbc.Row([
    html.Img(src='data:image/png;base64,{}'.format(scope_pic.decode()), width = 200),
    html.H2(" Rigol DS1104Z+ Scope Assistant v0.3")
    ],
    align = 'center')

col1_row3 = dbc.Row([
                channel_chkLst,
                channel_labels],
                justify = "center")

col1_row4 = dbc.Row([
                html.H3("Sampling Rate")],
                justify = "center")


col1_row5 = dbc.Row([
                dbc.Col([
                        radio_sRate]),
                dbc.Col([
                        btn_update_sRate])
                ]) #we're doing this weird placement because otherwise the button strecthes to the size of the radio buttons


col1_row6 = dbc.Row([
                    dcc.Input(id="desc", type="text", value = "Enter description", style={'width':400})
                    ],
                    justify = "center")

col1_row7 = dbc.Row([
                btn_trigger],
                justify = "center")
col1_row8 = dbc.Row([
                dbc.Col(html.Div("column2", id = 'outputDiv'), width = 1)
                ])

column1 =  dbc.Col(html.Div([
                             col1_row3,
                             col1_row4,
                             col1_row5,
                             col1_row6,
                             col1_row7,
                             col1_row8], 
                             id = 'userInputDiv')
                    )


row_1 = html.Div([
            dbc.Row([
                column1]),
                ])

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


#BUTTONS
btn_trigger = html.Button('Trigger', id='btn-trig', n_clicks=0, style={'padding':'30px 100px', 'boarder-radius':'10px'})
btn_update_sRate = html.Button('Update', id='btn-uSrate',n_clicks=0, style={'padding':'10px 20px'})
'''*************************************************************************'''


#RADIO ITEMS
radio_sRate = dcc.RadioItems(
        id = 'radio_sRate')
'''*************************************************************************'''

channel_labels = dbc.Col([
                    dcc.Input(id="channel_1", type="text", value = "Channel 1", style={'width':100}),
                    dcc.Input(id="channel_2", type="text", value = "Channel 2", style={'width':100}),
                    dcc.Input(id="channel_3", type="text", value = "Channel 3", style={'width':100}),
                    dcc.Input(id="channel_4", type="text", value = "Channel 4", style={'width':100})
                    ])




scope_pic = base64.b64encode(open('ds1104z.png', 'rb').read()) 
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
                    radio_sRate],
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

row_1 = html.Div([
            dbc.Row([
                column1,
                column2]),
                ])

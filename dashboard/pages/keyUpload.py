from dashboard.dashServer import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table_experiments as dt
import base64
from server.DataManager import DataManager

dm = DataManager()

layout = html.Div([
    html.Label("Provider"),
    dcc.Dropdown(
        id='provider-dropdown',
        options=[
            {'label': 'Amazon Web Services', 'value': 'aws'},
            {'label': 'OpenStack', 'value': 'openstack'}
        ],
        value=''
    ),
    html.Hr(),
    html.Label("keys to be uploaded"),
    dcc.Upload(
        id='file-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Hr(),
    dt.DataTable(
        rows=[{}],
        # optional - sets the order of columns
        columns=["Key File"],
        row_selectable=True,
        selected_row_indices=[],
        id='key-table'
    ),
    html.Button('Delete Key', id='delete-key-button'),
    html.Div(id='upload-status'),
    html.Div(id='delete-status')
])


def parse_contents(contents, filename, provider):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    status = False
    if 'pem' in filename:
        payload = {
            "PROVIDER": provider,
            "KEY_NAME": filename,
            "KEY_VALUE": decoded
        }
        dm.add_key(payload)
    return status

@app.callback(Output('key-table', 'rows'),
              [Input('provider-dropdown', 'value')])
def add_key(provider_value):
    keys = dm.get_keys(provider_value)
    dict_list = []
    for key in keys:
        dict_list.append({"Key File": key})
    return dict_list

@app.callback(Output('upload-status', 'children'),
              [Input('file-upload', 'contents'),
               Input('file-upload', 'filename'),
               Input('provider-dropdown', 'value')])
def add_key(list_of_contents, list_of_names, provider_value):
    child = html.Div([
        html.H2('File upload status:')
    ])
    if list_of_contents is not None:
        for content, name in zip(list_of_contents, list_of_names):
            status = parse_contents(content, name, provider_value)
            if status:
                return html.Div([child, html.P("File: {} Successfully uploaded.".format(name))])
            return html.Div([child, html.P("File: {} Failed to be uploaded.".format(name))])

@app.callback(
    Output('delete-status', 'children'),
    [Input('delete-key-button', 'n_clicks'),
     Input('key-table', 'rows')],
    [State('key-table', 'selected_row_indices')])
def delete_key(n_clicks, table_rows, selected_row_indices):
    for index in selected_row_indices:
        key_dict = table_rows[index]
        result = dm.delete_key(key_dict["Key File"], "aws")
        if result:
            return html.Div([html.H2("Key: {} was deleted".format(key_dict["Key File"]))])
        return html.Div([html.H2("ERROR: Key: {} was not deleted".format(key_dict["Key File"]))])

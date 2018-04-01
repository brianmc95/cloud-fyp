from dashboard.dashServer import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64
from server.DataManager import DataManager

dm = DataManager()
file = None

layout = html.Div([
    html.Label("Provider"),
    dcc.Dropdown(
        id='provider-dropdown',
        options=[
            {'label': 'Amazon Web Services', 'value': 'aws'},
            {'label': 'OpenStack', 'value': 'openstack'}
        ],
        value='aws'
    ),
    html.Div([
        dcc.Input(
            placeholder="Account Name",
            type="text",
            value="",
            id="aws_account_name"
        ),
        dcc.Input(
            placeholder="AWS account ID",
            type="text",
            value="",
            id="aws_account_id"
        ),
        dcc.Input(
            placeholder="AWS Region to use",
            type="text",
            value="",
            id="aws_region"
        ),
        html.Hr(),
        html.Label("Secret key to be uploaded"),
        dcc.Upload(
            id='aws-key-upload',
            children=html.Div([
                'Drag and Drop Key ',
                html.A('Select Key')
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
        ),
    ]),
    html.Div([
        dcc.Input(
            placeholder="Account Name",
            type="text",
            value="",
            id="openstack_account_name"
        ),
        dcc.Input(
            placeholder="OpenStack tenant name",
            type="text",
            value="",
            id="openstack_account_id"
        ),
        dcc.Input(
            placeholder="OpenStack URL",
            type="text",
            value="",
            id="openstack_auth_url"
        ),
        dcc.Input(
            placeholder="OpenStack Authorization Version",
            type="text",
            value="",
            id="openstack_auth_version"
        ),
        html.Hr(),
        html.Label("Password file"),
        dcc.Upload(
            id='aws-key-upload',
            children=html.Div([
                'Drag and Drop Key ',
                html.A('Select Key')
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
        ),
    ]),
    html.Div(id='account-status')
])

def parse_contents(contents, filename, provider):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'pem' in filename:
            dm.add_key(decoded, filename, provider)
    except Exception as e:
        print(e)
        return "FAILED"
    return "SUCCESS"

@app.callback(Output('account-status', 'children'),
              [Input('file-upload', 'contents'),
               Input('file-upload', 'filename'),
               Input('provider-dropdown', 'value')])
def update_output(list_of_contents, list_of_names, provider_value):
    child = html.Div([
        html.H2('File upload status:')
    ])
    if list_of_contents is not None:
        for content, name in zip(list_of_contents, list_of_names):
            status = parse_contents(content, name, provider_value)
            if status == "FAILED":
                child = html.Div([child, html.P("File: {} Failed to be uploaded.".format(name))])
            else:
                child = html.Div([child, html.P("File: {} Successfully uploaded.".format(name))])
        return child

@app.callback(Output('', 'style'),
              [Input('provider-dropdown', 'value'),])
def reveal_openstack(selected_provider):
    if selected_provider == "openstack":
        return
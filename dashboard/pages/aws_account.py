import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import base64

from dashboard.dashServer import app
from server.DataManager import DataManager

dm = DataManager()

def deal_with_bools():
    accounts = dm.get_accounts("aws")
    accounts_fix = []
    for account in accounts:
        if account["SET_ACCOUNT"]:
            account["SET_ACCOUNT"] = "True"
        else:
            account["SET_ACCOUNT"] = "False"
        accounts_fix.append(account)
    return accounts_fix

layout = html.Div([
    html.Label("Account Name:"),
    dcc.Input(
        placeholder="Account Name",
        type="text",
        value="",
        id="aws-account-name"
    ),
    html.Br(),
    html.Label("Account ID:"),
    dcc.Input(
        placeholder="AWS account ID",
        type="text",
        value="",
        id="aws-account-id"
    ),
    html.Br(),
    html.Label("AWS Region:"),
    dcc.Input(
        placeholder="AWS Region to use",
        type="text",
        value="",
        id="aws-region"
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
    html.Button('Add account', id='add-account-button'),
    dt.DataTable(
        rows=deal_with_bools(),
        # optional - sets the order of columns
        columns=["ACCOUNT_NAME", "SET_ACCOUNT"],
        row_selectable=True,
        selected_row_indices=[],
        id='aws-account-table'
    ),
    html.Button('Set account', id='select-account-button'),
    html.Button('Delete account', id='delete-account-button'),
    html.Div(id="aws-current-status"),
    html.Div(id="aws-account-status"),
    html.Div(id="aws-delete-status")
], style={})


def parse_contents(contents, account_name, account_id, account_region):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8')
    decoded = decoded.strip()
    account = {
        "ACCOUNT_NAME": account_name,
        "ACCOUNT_ID": account_id,
        "ACCOUNT_REGION": account_region,
        "ACCOUNT_SECRET_KEY": decoded,
        "PROVIDER": "AWS",
        "SET_ACCOUNT": False
    }
    try:
        dm.add_account(account)
    except Exception as e:
        print(e)
        return "FAILED"
    return "SUCCESS"


@app.callback(Output('aws-current-status', 'children'),
              [Input('aws-key-upload', 'contents'),
               Input('aws-key-upload', 'filename'),
               Input('aws-account-name', 'value'),
               Input('aws-account-id', 'value'),
               Input('aws-region', 'value'),
               Input('add-account-button', 'n_clicks')])
def add_account(secret_key_content, secret_key_name, account_name, account_id, account_region, n_clicks):
    if secret_key_content is not None and secret_key_name is not None and n_clicks:
        if account_id == "" or account_name == "" or account_region == "":
            return html.Div([html.H2("Please fill in your account details")])
        result = parse_contents(secret_key_content, account_name, account_id, account_region)
        if result:
            return html.Div([html.H2("Account: {} Successfully added".format(account_name))])

@app.callback(
    Output('aws-account-status', 'children'),
    [Input('select-account-button', 'n_clicks'),
     Input('aws-account-table', 'rows')],
    [State('aws-account-table', 'selected_row_indices')])
def set_account(n_clicks, table_rows, selected_row_indices):
    for index in selected_row_indices:
        account_details = table_rows[index]
        account_name = account_details["ACCOUNT_NAME"]
        result = dm.set_account(account_name, "AWS")
        if result:
            return html.Div([html.H2("Account: {} is now the set account".format(account_name))])
        else:
            return html.Div([html.H2("ERROR: Account: {} could not be set".format(account_name))])

@app.callback(
    Output('aws-delete-status', 'children'),
    [Input('delete-account-button', 'n_clicks'),
     Input('aws-account-table', 'rows')],
    [State('aws-account-table', 'selected_row_indices')])
def delete_account(n_clicks, table_rows, selected_row_indices):
    for index in selected_row_indices:
        account_details = table_rows[index]
        account_name = account_details["ACCOUNT_NAME"]
        result = dm.delete_account(account_name, "AWS")
        if result:
            return html.Div([html.H2("Account: {} was deleted".format(account_name))])
        else:
            return html.Div([html.H2("ERROR: Account: {} was not deleted".format(account_name))])

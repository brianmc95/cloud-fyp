import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import base64

from dashboard.dashServer import app
from server.DataManager import DataManager

dm = DataManager()

def deal_with_bools():
    accounts = dm.get_accounts("OPENSTACK")
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
        id="openstack-account-name"
    ),
    html.Br(),
    html.Label("Account ID:"),
    dcc.Input(
        placeholder="Account ID",
        type="text",
        value="",
        id="openstack-account-id"
    ),
    html.Br(),
    html.Label("Authorization URL:"),
    dcc.Input(
        placeholder="Auth URL",
        type="text",
        value="",
        id="openstack-authurl-id"
    ),
    html.Br(),
    html.Label("Authorization version:"),
    dcc.Input(
        placeholder="Auth version",
        type="text",
        value="",
        id="openstack-authversion-id"
    ),
    html.Br(),
    html.Label("Image API Version:"),
    dcc.Input(
        placeholder="Glance version",
        type="text",
        value="",
        id="openstack-image-id"
    ),
    html.Br(),
    html.Label("Tenant Name:"),
    dcc.Input(
        placeholder="Tenant",
        type="text",
        value="",
        id="openstack-tenant-id"
    ),
    html.Br(),
    html.Label("Password:"),
    dcc.Input(
        placeholder="Password",
        type="text",
        value="",
        id="openstack-pass-id"
    ),
    html.Hr(),
    html.Button('Add account', id='add-account-button'),
    dt.DataTable(
        rows=deal_with_bools(),
        # optional - sets the order of columns
        columns=["ACCOUNT_NAME", "SET_ACCOUNT"],
        row_selectable=True,
        selected_row_indices=[],
        id='openstack-account-table'
    ),
    html.Button('Set account', id='select-account-button'),
    html.Button('Delete account', id='delete-account-button'),
    html.Div(id="openstack-current-status"),
    html.Div(id="openstack-account-status"),
    html.Div(id="openstack-delete-status")
], style={})

@app.callback(Output('openstack-current-status', 'children'),
              [Input('openstack-account-name', 'value'),
               Input('openstack-account-id', 'value'),
               Input('openstack-authurl-id', 'value'),
               Input('openstack-authversion-id', 'value'),
               Input('openstack-image-id', 'value'),
               Input('openstack-tenant-id', 'value'),
               Input('openstack-pass-id', 'value'),
               Input('add-account-button', 'n_clicks')])
def add_account(account_name, account_id, auth_url, auth_version, image_version, tenant_name, password, n_clicks):
    if n_clicks:
        if account_name != "" or account_id != "" or auth_url != "" or auth_version != "" or image_version != "" or tenant_name != "" or password != "":
            account = {
                "ACCOUNT_NAME": account_name,
                "ACCOUNT_ID": account_id,
                "ACCOUNT_AUTH_URL": auth_url,
                "ACCOUNT_AUTH_VERSION": auth_version,
                "ACCOUNT_IMAGE_VERSION": image_version,
                "ACCOUNT_TENANT_NAME": tenant_name,
                "ACCOUNT_PASSWORD": password,
                "PROVIDER": "OPENSTACK",
                "SET_ACCOUNT": False
            }
            result = dm.add_account(account)
            if result:
                return html.Div([html.H2("Account: {} has been added.".format(account_name))])
        return html.Div([html.H2("Please fill out all account details before submitting.")])

@app.callback(
    Output('openstack-account-status', 'children'),
    [Input('select-account-button', 'n_clicks'),
     Input('openstack-account-table', 'rows')],
    [State('openstack-account-table', 'selected_row_indices')])
def set_account(n_clicks, table_rows, selected_row_indices):
    for index in selected_row_indices:
        account_details = table_rows[index]
        account_name = account_details["ACCOUNT_NAME"]
        result = dm.set_account(account_name, "OPENSTACK")
        if result:
            return html.Div([html.H2("Account: {} is now the set account".format(account_name))])
        else:
            return html.Div([html.H2("ERROR: Account: {} could not be set".format(account_name))])

@app.callback(
    Output('openstack-delete-status', 'children'),
    [Input('delete-account-button', 'n_clicks'),
     Input('openstack-account-table', 'rows')],
    [State('openstack-account-table', 'selected_row_indices')])
def delete_account(n_clicks, table_rows, selected_row_indices):
    for index in selected_row_indices:
        account_details = table_rows[index]
        account_name = account_details["ACCOUNT_NAME"]
        result = dm.delete_account(account_name, "OPENSTACK")
        if result:
            return html.Div([html.H2("Account: {} was deleted".format(account_name))])
        else:
            return html.Div([html.H2("ERROR: Account: {} was not deleted".format(account_name))])

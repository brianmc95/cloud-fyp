import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output

from dashboard.dashServer import app
from dashboard.pages import deployment, monitoring, keyUpload, aws_account, openstack_account

app.layout = html.Div([
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

basicLayout = html.Div([
    html.H1("Cloud monitoring"),
    html.H3("Brian McCarthy - 114302146 - FYP"),
    html.A(html.Button('Deploy'), href='/deploy'),
    html.A(html.Button('Monitor'), href='/monitoring'),
    html.A(html.Button('management'), href='/account-management'),
    html.A(html.Button('AWS Account Management'), href='/aws-account-management'),
    html.A(html.Button('OpenStack Account Management'), href='/openstack-account-management'),
    html.A(html.Button('Key Management'), href='/key-management'),
    html.A(html.Button('Migrate'), href='/migration')])

errorLayout = html.Div([
    basicLayout,
    html.P('404: Page not found returning to home page'),
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/deploy':
        return deployment.layout
    elif pathname == '/monitoring':
        return monitoring.layout
    elif pathname == '/aws-account-management':
        return aws_account.layout
    elif pathname == '/openstack-account-management':
        return openstack_account.layout
    elif pathname == '/key-management':
        return keyUpload.layout
    elif pathname == '/':
        return basicLayout
    else:
        return errorLayout


if __name__ == "__main__":
    app.run_server(debug=True)

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard.dashServer import app
from dashboard.pages import deploymentPage

app.layout = html.Div([

    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

])

basicLayout = html.Div([
    html.H1("Cloud monitoring"),
    html.H3("Brian McCarthy - 114302146 - FYP"),
    html.A(html.Button('Deploy') , href='/deploy'),
    html.A(html.Button('Monitor'), href='/monitor'),
    html.A(html.Button('Alerts') , href='/alerts'),
    html.A(html.Button('Migrate'), href='/migrate')])

errorLayout = html.Div([
    basicLayout,
    html.P('404: Page not found returning to home page'),
])


@app.callback(Output('page-content', 'children'),
                     [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/deploy':
         return deploymentPage.layout
    elif pathname == '/':
        return basicLayout
    else:
        return errorLayout


if __name__ == '__main__':
    app.run_server(debug=True)
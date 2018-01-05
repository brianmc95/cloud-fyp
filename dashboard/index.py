import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard.dashServer import app
from dashboard.pages import deploymentPage
from dashboard.pages import mainPage

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
                     [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/deploy':
         return deploymentPage.layout
    elif pathname == '/main':
         return mainPage.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
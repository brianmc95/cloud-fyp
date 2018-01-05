import dash_html_components as html
from dash.dependencies import Input, Output

from dashboard.dashServer import app

layout = html.Div([
        html.Button(id='deploy-button', n_clicks=0, children='Deployment'),
        html.Div(id='main-output')
])


@app.callback(Output('main-output', 'children'),
                         [Input('deploy-button', 'n_clicks')],
                         [])
def move_to_deploy(n_clicks):
    return u"We just hit the deploy button: {} times".format(n_clicks)





"""
DF_GAPMINDER = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv'
)
DF_GAPMINDER = DF_GAPMINDER[DF_GAPMINDER['year'] == 2007]
DF_GAPMINDER.loc[0:20]

DF_SIMPLE = pd.DataFrame({
    'x': ['A', 'B', 'C', 'D', 'E', 'F'],
    'y': [4, 3, 1, 2, 3, 6],
    'z': ['a', 'b', 'c', 'a', 'b', 'c']
})


dataframes = {'DF_GAPMINDER': DF_GAPMINDER,
              'DF_SIMPLE': DF_SIMPLE}


def get_data_object(user_selection):
    '''
    For user selections, return the relevant in-memory data frame.
    '''
    return dataframes[user_selection]


app.layout = html.Div([
    html.H4('DataTable'),
    html.Label('Report type:', style={'font-weight': 'bold'}),
    dcc.Dropdown(
        id='field-dropdown',
        options=[{'label': df, 'value': df} for df in dataframes],
        value='DF_GAPMINDER',
        clearable=False
    ),
    dt.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='table'
    ),
    html.Div(id='selected-indexes')
], className="container")


@app.callback(Output('table', 'rows'), [Input('field-dropdown', 'value')])
def update_table(user_selection):
    '''
    For user selections, return the relevant table
    '''
    df = get_data_object(user_selection)
    return df.to_dict('records')


app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})

"""

if __name__ == '__main__':
    app.run_server(debug=True)

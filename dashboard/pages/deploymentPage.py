import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from openStack import Nova
from dashboard.dashServer import app


# https://github.com/plotly/dash/issues/71

deployableNove = Nova.Nova()
sizes = deployableNove.getSizes()
images = deployableNove.getImages()


imageOptions = []
for i in range(len(images)):
    option = {"label": images[i].name, "value": i}
    imageOptions.append(option)

sizeOptions = []
for i in range(len(sizes)):
    option = {"label": sizes[i].name, "value": i}
    sizeOptions.append(option)


layout = html.Div([
            html.Label('Nova Image Type'),
            dcc.Dropdown(
                id="image",
                options=imageOptions,
                value=''
            ),

            html.Label('Nova Image Size'),
            dcc.Dropdown(
                id="size",
                options=sizeOptions,
                value='',
            ),

            html.Button(id='launch', children='Launch'),

            html.Div(id='output-state')
        ], style={})


@app.callback(Output('output-state', 'children'),
            [Input('launch', 'n_clicks')],
            [State('image', 'value'),
            State('size', 'value')])
def launch_instance(n_clicks, imageIndex, sizeIndex):
    deployableNove.setImage(images[imageIndex])
    deployableNove.setSize(sizes[sizeIndex])
    deployableNove.instantiate_nova()
    return u'''The nova instance was launched with: image "{}", of size"{}"'''.format(images[imageIndex], sizes[sizeIndex])


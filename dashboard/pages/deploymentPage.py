import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from openStack import Nova
from aws import EC2
from aws import EBS_volume
from dashboard.dashServer import app


# https://github.com/plotly/dash/issues/71

deployable_ec2 = EC2.EC2()
deployable_nove = Nova.Nova()

nova_sizes = deployable_nove.getSizes()
nova_images = deployable_nove.getImages()


def image_size_options(provider):
    if provider == "aws":
        imageOptions = []
        for i in range(len(nova_images)):
            option = {"label": nova_images[i].name, "value": i}
            imageOptions.append(option)

        sizeOptions = []
        for i in range(len(nova_sizes)):
            option = {"label": nova_sizes[i].name, "value": i}
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
    deployable_nove.setImage(nova_images[imageIndex])
    deployable_nove.setSize(nova_sizes[sizeIndex])
    deployable_nove.instantiate_nova()
    return u'''The nova instance was launched with: image "{}", of size"{}"'''.format(nova_images[imageIndex], nova_sizes[sizeIndex])


import os
import glob
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from openStack import Nova

app = dash.Dash()

deployableNova = Nova.Nova()

images = deployableNova.getImages()
sizes = deployableNova.getSizes()

# <NodeImage: id=fd8d1f8f-8b3f-4125-9bd6-1a5dd8f4067b, name=keele-mapr-sahara, driver=OpenStack  ...>
# <OpenStackNodeSize: id=1, name=m1.tiny, ram=512, disk=1, bandwidth=None, price=0.0, driver=OpenStack, vcpus=1,  ...>

imageOptions = []
for i in range(len(images)):
    option = {"label": images[i].name, "value": i}
    imageOptions.append(option)

sizeOptions = []
for i in range(len(sizes)):
    option = {"label": sizes[i].name, "value": i}
    sizeOptions.append(option)

# https://github.com/plotly/dash/issues/71

image_directory = '/Users/BrianMcCarthy/Downloads/'
list_of_images = [os.path.basename(x) for x in glob.glob('{}*.png'.format(image_directory))]
static_image_route = '/static/'

app = dash.Dash()

app.layout = html.Div([

])

app.layout = html.Div([
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
    deployableNova.setImage(images[imageIndex])
    deployableNova.setSize(sizes[sizeIndex])
    deployableNova.instantiate_nova()
    return u'''
            The nova instance was launched with:
            image "{}",
            of size"{}"
        '''.format(images[imageIndex], sizes[sizeIndex])


if __name__ == '__main__':
    app.run_server(debug=True)

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event

from dashboard.dashServer import app
from nodes.aws.EC2 import EC2
from nodes.aws.EBS_volume import EBS_volume
from nodes.openStack.Nova import Nova

# https://github.com/plotly/dash/issues/71

deployable_ec2 = EC2(user="me", name="myEC2", region="eu-west-1", keyPair="firstTestInstance",
                     accessID_Local="/Users/BrianMcCarthy/amazonKeys/accessID",
                     accessKey_Local="/Users/BrianMcCarthy/amazonKeys/sak2")
deployable_nova = Nova(name="test", keyPair="help me")

provider_dropdown_options = {
    "Amazon Web Services": {
        "images": [{"label": image.name, "value": image.id} for image in deployable_ec2.get_images()],
        "sizes": [{"label": size.name, "value": size.id} for size in deployable_ec2.get_sizes()]},
    "Vscaler": {"images": [{"label": image.name, "value": image.id} for image in deployable_nova.get_images()],
                "sizes": [{"label": size.name, "value": size.id} for size in deployable_nova.get_sizes()]}
}

layout = html.Div([
    html.Label("Provider"),
    dcc.Dropdown(
        id="provider-dropdown",
        options=[{"label": key, "value": key} for key in provider_dropdown_options.keys()]
    ),
    html.Label("Name of instance"),
    dcc.Input(
        id="name-input",
        placeholder="Enter name of instance",
        type="text",
        value=""
    ),
    html.Label("Instance Type"),
    dcc.Dropdown(
        id="image-dropdown",
        searchable=False,
        placeholder="Select type of instance"
    ),

    html.Label("instance Size"),
    dcc.Dropdown(
        id="size-dropdown",
        searchable=False,
        placeholder="Select size of instance"
    ),

    html.Label("Disk Size"),
    dcc.Input(
        id="disk-size-input",
        placeholder="Enter Size of volume",
        type="number",
        value=""
    ),

    html.Button(id="launch-button", children="Launch"),

    html.Div(id="launch-status")
], style={})


@app.callback(
    Output("image-dropdown", "options"),
    [Input("provider-dropdown", "value")])
def set_provider_images(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return provider_dropdown_options[selected_provider]["images"]
    return ""


@app.callback(
    Output("size-dropdown", "options"),
    [Input("provider-dropdown", "value")])
def set_provider_sizes(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return provider_dropdown_options[selected_provider]["sizes"]
    return ""


@app.callback(
    Output("image-dropdown", "searchable"),
    [Input("provider-dropdown", "value")])
def set_images_active(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return True
    return False


@app.callback(
    Output("size-dropdown", "searchable"),
    [Input("provider-dropdown", "value")])
def set_sizes_active(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return True
    return False


@app.callback(
    Output('launch-status', 'children'),
    [Input('launch-button', 'n_clicks')],
    state=[State("provider-dropdown", "value"),
           State("name-input", "value"),
           State("image-dropdown", "value"),
           State("size-dropdown", "value"),
           State("disk-size-input", "value")])
def launch_instance(n_clicks, provider, name, image, size, disk_size):
    if provider == "Vscaler":
        node = deployable_nova
    elif provider == "Amazon Web Services":
        node = deployable_ec2
    else:
        return None

    node.set_image(image)
    node.set_size(size)

    node.instantiate_node()

    return u"Instance: {} Provider: {} Instance Type: {} Instance Size: {} Disk size: {}".format(name, provider, image, size, disk_size)



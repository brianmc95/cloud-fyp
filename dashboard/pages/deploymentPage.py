import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from dashboard.dashServer import app
from accounts.AWS import AWS
from accounts.OpenStack import OpenStackProvider


aws = AWS()
vscaler = OpenStackProvider()

providers = {"Amazon Web Services": aws, "Vscaler": vscaler}

layout = html.Div([
    html.Label("Provider"),
    dcc.Dropdown(
        id="provider-dropdown",
        options=[{"label": key, "value": key} for key in providers]
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

    html.Label("Instance Size"),
    dcc.Dropdown(
        id="size-dropdown",
        searchable=False,
        placeholder="Select size of instance"
    ),
    html.Label("Instance Networks"),
    dcc.Dropdown(
        id="networks-dropdown",
        searchable=False,
        multi=True,
        placeholder="Select instance Networks"
    ),

    html.Label("Instance Security"),
    dcc.Dropdown(
        id="security-dropdown",
        searchable=False,
        multi=True,
        placeholder="Select security groups instance is in"
    ),

    html.Label("Volume name"),
    dcc.Input(
        id="volume-name-input",
        placeholder="Enter name of volume to attach",
        type="text",
        value=""
    ),
    html.Label("Volume size"),
    dcc.Input(
        id="volume-size-input",
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
        return [{"label": image.name, "value": image.id} for image in providers[selected_provider].list_images()]
    return ""


@app.callback(
    Output("size-dropdown", "options"),
    [Input("provider-dropdown", "value")])
def set_provider_sizes(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return [{"label": size.name, "value": size.id} for size in providers[selected_provider].list_sizes()]
    return ""


@app.callback(
    Output("networks-dropdown", "options"),
    [Input("provider-dropdown", "value")])
def set_provider_networks(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return [{"label": net.name, "value": net.id} for net in providers[selected_provider].list_networks()]
    return ""


@app.callback(
    Output("security-dropdown", "options"),
    [Input("provider-dropdown", "value")])
def set_provider_security_groups(selected_provider):
    if selected_provider == "Vscaler":
        return [{"label": sec_group.name, "value": sec_group.id} for sec_group in
                providers[selected_provider].list_security_groups()]
    elif selected_provider == "Amazon Web Services":
        return [{"label": sec_group, "value": sec_group} for sec_group in
                providers[selected_provider].list_security_groups()]
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
    Output("networks-dropdown", "searchable"),
    [Input("provider-dropdown", "value")])
def set_images_active(selected_provider):
    if selected_provider == "Amazon Web Services" or selected_provider == "Vscaler":
        return True
    return False


@app.callback(
    Output("security-dropdown", "searchable"),
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
           State("networks-dropdown", "value"),
           State("security-dropdown", "value"),
           State("volume-name-input", "value"),
           State("volume-size-input", "value")])
def launch_instance(n_clicks, provider, name, image_id, size_id, network_ids, security_ids, volume_name, volume_size):
    deploy_image = providers[provider].get_image(image_id)
    deploy_size = providers[provider].get_size(size_id)
    deploy_nets = providers[provider].get_networks(network_ids)
    deploy_sec = providers[provider].get_security_groups(security_ids)

    vol = providers[provider].create_volume(name=volume_name, size=volume_size)
    node = providers[provider].create_node(name=name,
                                           size=deploy_size,
                                           image=deploy_image,
                                           networks=deploy_nets,
                                           security_groups=deploy_sec)

    providers[provider].attach_volume(node, vol)

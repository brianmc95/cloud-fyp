import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from dash.dependencies import Input, Output, State
import pandas as pd
from dashboard.dashServer import app
from server.DataManager import DataManager
import plotly

dm = DataManager()
years, months = dm.get_dates()
days = range(1, 31)

# What do I want in my table

def get_columns():
    return ["DATE_TIME", "INSTANCE_ID", "INSTANCE_NAME", "PROVIDER", "CPU_USAGE",
            "MEMORY_USAGE", "MEMORY_TOTAL", "NETWORK_USAGE", "CONNECTIONS", "COST"]


layout = html.Div([
    html.Label("Year"),
    dcc.Dropdown(
        id="year-dropdown",
        options=[{"label": year, "value": year} for year in years]
    ),
    html.Label("Month"),
    dcc.Dropdown(
        id="month-dropdown",
        disabled=True,
        options=[{"label": key, "value": value} for key, value in months.items()]
    ),
    html.Label("Day"),
    dcc.Dropdown(
        id="day-dropdown",
        disabled=True,
        options=[{"label": day, "value": day} for day in days]
    ),
    html.H4('Usage DataTable'),

    dt.DataTable(
        rows=[],   #dm.get_current_data(),

        # optional - sets the order of columns
        columns=get_columns(),

        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='usage-table'
    ),
    html.Div(id='selected-indexes'),
    dcc.Graph(
        id='graph-usage'
    ),
    # Want some sort of table with all the info about an individual node
], className="container")

@app.callback(
    Output("month-dropdown", "disabled"),
    [Input("year-dropdown", "value")])
def set_months_active(selected_year):
    if selected_year in years:
        return False
    return True


@app.callback(
    Output("day-dropdown", "disabled"),
    [Input("month-dropdown", "value"),
     Input("year-dropdown", "value")])
def set_days_active(selected_month, selected_year):
    if (selected_month is not None and 1 <= selected_month <= 12) and selected_year in years:
        return False
    return True


@app.callback(
    Output("day-dropdown", "options"),
    [Input("month-dropdown", "value"),
     Input("year-dropdown", "value")])
def set_days(selected_month, selected_year):
    if (selected_month is not None and 1 <= selected_month <= 12) and selected_year in years:
        rows = [{"label": day, "value": day} for day in range(1, dm.get_days(selected_month, selected_year) + 1)]
        return rows
    return False

@app.callback(
    Output("usage-table", "rows"),
    [Input("year-dropdown", "value"),
     Input("month-dropdown", "value"),
     Input("day-dropdown", "value")])
def update_table(selected_year, selected_month, selected_day):
    if selected_year in years:
        json_df = dm.get_specific_data(selected_year, selected_month, selected_day)
        if not json_df:
            return []
        all_df = pd.read_json(json_df)
        return all_df.to_dict("records")
    return dm.get_current_data()


@app.callback(
    Output('usage-table', 'selected_row_indices'),
    [Input('graph-gapminder', 'clickData')],
    [State('datatable-gapminder', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices

@app.callback(
    Output('graph-usage', 'figure'),
    [Input('usage-table', 'rows'),
     Input('usage-table', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    print(dff)
    print(dff.columns)
    fig = plotly.tools.make_subplots(
        rows=4, cols=1,
        subplot_titles=('CPU Usage', 'Memory Usage', 'Network Usage', 'Costing'),
        shared_xaxes=True)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    fig.append_trace({
        'x': dff['INSTANCE_NAME'],
        'y': dff['CPU_USAGE'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['INSTANCE_NAME'],
        'y': dff["MEMORY_USAGE"]/dff["MEMORY_TOTAL"],
        'type': 'bar',
        'marker': marker
    }, 2, 1)
    fig.append_trace({
        'x': dff['INSTANCE_NAME'],
        'y': dff['NETWORK_USAGE'],
        'type': 'bar',
        'marker': marker
    }, 3, 1)
    fig.append_trace({
        'x': dff['INSTANCE_NAME'],
        'y': dff['COST'],
        'type': 'bar',
        'marker': marker
    }, 4, 1)
    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 800
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    fig['layout']['yaxis1'].update(range=[0, 100])
    fig['layout']['yaxis2'].update(range=[0, 100])
    return fig

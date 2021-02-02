import os
import copy
import json

import flask

from dash.dependencies import Input, Output, State

from analytics_sdk.utilities import (
    save_archive,
    get_archives,
    get_archive,
    generate_pdf
)

from utils import *
from pages.utils import *


PLATFORM_ROUTE = os.getenv("PLATFORM_ROUTE", '')
in_store_id = "_oap_data_in_" + PLATFORM_ROUTE
out_store_id = "_oap_data_out_" + PLATFORM_ROUTE
oap_name = os.getenv("PLATFORM_ROUTE", 'metered-usage-insight')

def register_callbacks(app):
    """ Common settings """

    # handle pdf
    @app.callback(
        # [
        #     Output("download-pdf", "children"),
        #     Output("download-pdf", "href")
        # ],
        Output('dummy-store', 'data'),
        Input('gen-pdf', 'n_clicks'),
        State(out_store_id, 'data')
    )
    def generate_report(n_clicks, data):
        if n_clicks:  # avoid initial loading
            print_route = '/full-view'
            res = generate_pdf(oap_name, data, 'A4', print_route)
            return res['Location'] 

    # handle archive
    @app.callback(
        [
            Output("list-archives", "options"),
            Output('list-archives', 'value'),
        ],
        Input('gen-archive', 'n_clicks'),
        State(out_store_id, 'data')
    )
    def create_archive(n_clicks, data):
        archive_id = None
        if n_clicks:
            print_route = '/full-view'
            archive_id = save_archive(oap_name, data, 'A4', print_route)['archive_id']

        archives = get_archives(oap_name)

        return archives, archive_id

    @app.callback(
        Output(in_store_id, "data"),
        Input('list-archives', 'value')
    )
    def load_archive(archive_id):
        if not archive_id:
            return

        archive = get_archive(archive_id)

        return json.loads(archive['state'])

    # save / load settings
    @app.callback(
        Output(out_store_id, "data"),
        [
            Input("reporting_priod_picker", "start_date"),
            Input("reporting_priod_picker", "end_date"),
        ]
    )
    def save_settings(start_date, end_date):
        return start_date, end_date

    @app.callback(
        Output("reporting_priod_picker", "start_date"),
        Output("reporting_priod_picker", "end_date"),
        Input(in_store_id, "data"),
    )
    def load_settings(data):
        return data if data else [None, None]

    layout = dict(
        autosize=True,
        automargin=True,
        height=150,
        margin=dict(l=30, r=30, b=00, t=00),
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#fff",
        font=dict(color="#777777"),
        legend=dict(
            font=dict(color="#333", size="10"),
            orientation="v",
            bgcolor="rgba(0,0,0,0)",
            y=0.8),
        title=""
    )

    graph_data = dict(
        type="pie",
        hoverinfo="label+value+percent",
        textinfo="percent",
        textfont=dict(size=9, color="#fff"),
        hole=0.5,
        direction="clockwise",
        sort=False,
        marker=dict(
            colors=["#0077C8", "#32a3df", "#673ab7", "#9c27b0"],
            line=dict(color='#fff', width=1)
        ),
    )

    @app.callback(
        Output("pie-graph-total-usage", "figure"),
        [
            Input(in_store_id, "data"),
        ],
    )
    def pie_graph_total_usage(search_types):
        layout_pie = copy.deepcopy(layout)

        device_types = ['Events-Only', 'Inventory-Only', 'Up-Down', 'Fully-Managed']
        yy = [27.5, 26.4, 32.3, 13.8]

        data = copy.deepcopy(graph_data)
        data['labels'] = device_types
        data['values'] = yy

        figure = dict(data=[data], layout=layout_pie)
        return figure

    @app.callback(
        Output("pie-graph-unweighted-usage", "figure"),
        [
            Input(in_store_id, "data"),
        ],
    )
    def pie_graph_unweighted_usage(search_types):
        layout_pie = copy.deepcopy(layout)

        device_types = ['Client A', 'Client B', 'Client C', 'Client D']
        yy = [27.5, 26.4, 32.3, 13.8]

        data = copy.deepcopy(graph_data)
        data['labels'] = device_types
        data['values'] = yy

        figure = dict(data=[data], layout=layout_pie)
        return figure

    @app.callback(
        Output("pie-graph-weighted-usage", "figure"),
        [
            Input(in_store_id, "data"),
        ],
    )
    def pie_graph_weighted_usage(search_types):
        layout_pie = copy.deepcopy(layout)

        device_types = ['Client A', 'Client B', 'Client C', 'Client D']
        yy = [27.5, 26.4, 32.3, 13.8]

        data = copy.deepcopy(graph_data)
        data['labels'] = device_types
        data['values'] = yy

        figure = dict(data=[data], layout=layout_pie)
        return figure

    @app.callback(
        Output("pie-graph-unweighted-type-usage", "figure"),
        [
            Input(in_store_id, "data"),
        ],
    )
    def pie_graph_unweighted_type_usage(search_types):
        layout_pie = copy.deepcopy(layout)
        layout_pie['legend'] = dict(
            font=dict(color="#333", size="10"),
            orientation="v",
            bgcolor="rgba(0,0,0,0)",
            y=0.1
        )
        layout_pie['margin'] = dict(l=0, r=50, b=00, t=00)

        resource_types = get_resource_types()
        yy = [27.5, 26.4, 32.3, 13.8, 7, 6]

        data = copy.deepcopy(graph_data)
        data['labels'] = resource_types
        data['values'] = yy

        figure = dict(data=[data], layout=layout_pie)
        return figure

    @app.callback(
        Output("pie-graph-weighted-type-usage", "figure"),
        [
            Input(in_store_id, "data"),
        ],
    )
    def pie_graph_weighted_type_usage(search_types):
        layout_pie = copy.deepcopy(layout)
        layout_pie['legend'] = dict(
            font=dict(color="#333", size="10"),
            orientation="v",
            bgcolor="rgba(0,0,0,0)",
            y=0.1
        )

        resource_types = get_resource_types()
        yy = [27.5, 26.4, 32.3, 13.8, 7, 6]

        data = copy.deepcopy(graph_data)
        data['labels'] = resource_types
        data['values'] = yy

        figure = dict(data=[data], layout=layout_pie)
        return figure

    @app.callback(
        Output("table-resource-type", "children"),
        [
            Input("reporting_priod_picker", "start_date"),
            Input("reporting_priod_picker", "end_date"),
        ]
    )
    def pie_graph_weighted_type_usage(start_date, end_date):
        rows = {}
        tenant_id = "0"
        metric_names = get_metric_types()
        table_rows = [['Resource Tier', 'Usage (Unweighted)', 'Usage (Weighted)']]

        for metric_name, types in metric_names.items():
            unweighted = get_metric_value(tenant_id, types['unweighted'], start_date, end_date)
            weighted = get_metric_value(tenant_id, types['weighted'], start_date, end_date)
            _unweighted = unweighted['data']['result'][0]['value'][0]
            _weighted = weighted['data']['result'][0]['value'][0]

            table_rows.append([metric_name.title(), _unweighted, _weighted])

        return make_dash_table(table_rows)

    # api integration
    @app.callback(
        Output('total_clients', 'children'),
        Input('gen-pdf', 'n_clicks'),
        State(out_store_id, 'data')
    )
    def get_total_clients(n_clicks, data):
        if not n_clicks:  # initial loading
            tenants = get_tenants()
            return len(tenants)

    @app.callback(
        Output('total_resources', 'children'),
        Input('gen-pdf', 'n_clicks'),
        State(out_store_id, 'data')
    )
    def get_total_resources(n_clicks, data):
        if not n_clicks:  # initial loading
            resource_types = get_resource_types()
            return len(resource_types)

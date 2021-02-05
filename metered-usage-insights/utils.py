import os
import json

import requests
import requests_cache

requests_cache.install_cache('opsramp_cache', backend='sqlite', expire_after=3600*30, allowable_methods=("GET", "POST"))

BASE_URL = os.getenv('API_SERVER', '')


def get_tenants():
    url = BASE_URL + '/metricsql/tenants'
    res = requests.get(url).json()

    return res


def get_resource_types():
    url = BASE_URL + '/metricsql/resource-types'
    res = requests.get(url).json()

    return res


def get_metric_names():
    url = BASE_URL + '/metricsql/metric-names'
    res = requests.get(url).json()

    return res


def get_metric_value(tenant_id, metric_name, resource_type=None, start=None, end=None):
    url = BASE_URL + '/metricql/query'

    body = {
        "tenantId": tenant_id,
        "metricName": metric_name,
        "resourceType": resource_type,
        "start": start,
        "end": end
    }

    res = requests.post(url, data=json.dumps(body)).json()

    return res


def get_breakdown_resource_tier(start_date, end_date):
    tenants = get_tenants()
    metric_names = get_metric_names()
    resp = {}

    for metric_name, types in metric_names.items():
        resp[metric_name] = { 'unweighted': 0, 'weighted': 0 }

        for tenant in tenants:
            tenant_id = tenant['tenantId']
            unweighted = get_metric_value(tenant_id, types['unweighted'], start_date, end_date)
            weighted = get_metric_value(tenant_id, types['weighted'], start_date, end_date)
            _unweighted = unweighted['data']['result'][0]['value'][0]
            _weighted = weighted['data']['result'][0]['value'][0]
            resp[metric_name]['unweighted'] += _unweighted
            resp[metric_name]['weighted'] += _weighted

    return resp

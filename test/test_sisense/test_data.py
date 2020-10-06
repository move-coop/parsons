ENV_PARAMETERS = {
    'SISENSE_SITE_NAME': 'my_site_name',
    'SISENSE_API_KEY': 'my_api_key'
}

TEST_GET_DASHBOARDS = [{
    "title": "string",
    "desc": "string",
    "oid": "string",
    "source": "Unknown Type: string,null",
    "parentFolder": "Unknown Type: string,null",
    "type": "string",
    "shares": [
        {
            "shareId": "string",
            "type": "user",
            "rule": "view",
            "subscribe": 'true'
        }
    ],
    "style": {
        "name": "string",
        "palette": {
            "colors": [
                "string"
            ],
            "name": "string",
            "isSystem": 'true'
        }
    },
    "owner": "string",
    "userId": "string",
    "created": "2020-09-30T16:04:45.387Z",
    "lastUpdated": "2020-09-30T16:04:45.387Z",
    "datasource": {
        "title": "string",
        "id": "string",
        "address": "string",
        "database": "string",
        "fullname": "string"
    },
    "filters": [
        {
            "jaql": {
                "dim": "string",
                "datatype": "string",
                "title": "string"
            }
        }
    ],
    "instanceType": "string",
    "dataExploration": 'true',
    "layout": {
        "type": "string",
        "columns": [
            {
                "width": 0,
                "cells": [
                    {
                        "subcells": [
                            {
                                "elements": [
                                    {
                                        "widgetId": "string",
                                        "minHeight": 0,
                                        "maxHeight": 0,
                                        "minWidth": 0,
                                        "maxWidth": 0,
                                        "height": "Unknown Type: number,string",
                                        "defaultWidth": 0
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "previewLayout": [
        {
            "type": "string",
            "format": "string",
            "orientation": "string",
            "layout": "string",
            "headerSize": "string",
            "title": 'true',
            "elasticubeBuilt": 'true',
            "elasticubeName": 'true',
            "filters": 'true',
            "logo": 'true',
            "pageNumbers": 'true',
            "pages": [
                {
                    "type": "string",
                    "columns": [
                        {
                            "width": 0,
                            "cells": [
                                {
                                    "subcells": [
                                        {
                                            "elements": [
                                                {
                                                    "widgetId": "string",
                                                    "minHeight": 0,
                                                    "maxHeight": 0,
                                                    "minWidth": 0,
                                                    "maxWidth": 0,
                                                    "height": "Unknown Type: number,string",
                                                    "defaultWidth": 0
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "defaultFilters": "Unknown Type: null,array"
}]

TEST_GET_DASHBOARD_SHARES = [
    {
        "shareId": "string",
        "type": "user",
        "rule": "view",
        "subscribe": 'true'
    }
]

TEST_PUBLISH_DASHBOARD_URL = {'url': 'https://www.periscopedata.com/api/embedded_dashboard?data=%7B%22dashboard%22%3A7863%2C%22embed%22%3A%22v2%22%2C%22filters%22%3A%5B%7B%22name%22%3A%22Filter1%22%2C%22value%22%3A%22value1%22%7D%2C%7B%22name%22%3A%22Filter2%22%2C%22value%22%3A%221234%22%7D%5D%7D&signature=adcb671e8e24572464c31e8f9ffc5f638ab302a0b673f72554d3cff96a692740'} # noqa

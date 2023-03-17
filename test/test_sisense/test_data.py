ENV_PARAMETERS = {"SISENSE_SITE_NAME": "my_site_name", "SISENSE_API_KEY": "my_api_key"}

TEST_PUBLISH_SHARED_DASHBOARD = {
    "url": "https://www.periscopedata.com/api/embedded_dashboard?data=%7B%22dashboard%22%3A7863%2C%22embed%22%3A%22v2%22%2C%22filters%22%3A%5B%7B%22name%22%3A%22Filter1%22%2C%22value%22%3A%22value1%22%7D%2C%7B%22name%22%3A%22Filter2%22%2C%22value%22%3A%221234%22%7D%5D%7D&signature=adcb671e8e24572464c31e8f9ffc5f638ab302a0b673f72554d3cff96a692740"  # noqa: E501
}

TEST_LIST_SHARED_DASHBOARDS = [
    "https://app.periscopedata.com/shared/abc",
    "https://app.periscopedata.com/shared/def",
]

TEST_DELETE_SHARED_DASHBOARD = {"success": True}

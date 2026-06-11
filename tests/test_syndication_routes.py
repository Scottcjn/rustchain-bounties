import pytest
from yourapplication import app

@pytest.mark.parametrize("route, query, expected_status", [
    ('/api/syndication/runs', {'limit': 'not-an-int'}, 400),
    ('/api/syndication/report/outbound', {'page': 'not-an-int'}, 400),
    ('/api/syndication/report/export', {'export_id': 'not-an-int'}, 400),
    ('/api/syndication/runs', {'limit': '10'}, 200),
    ('/api/syndication/report/outbound', {'page': '1'}, 200),
    ('/api/syndication/report/export', {'export_id': '1'}, 200),
])
def test_syndication_routes(client, _insert_agent, route, query, expected_status):
    response = client.get(route, query_string=query)
    assert response.status_code == expected_status
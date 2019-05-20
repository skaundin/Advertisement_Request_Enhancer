import os
import tempfile

import pytest
import json

from app import app


@pytest.fixture(scope='module')
def client():
    app.testing = True
    client = app.test_client()
    yield client

# Test for valid status code (200) if the server receives a valid request with
# all the required fields, i.e., site.id, site.page, device.ip and publisher.id


def test_valid_request(client):
    response = client.post('/inject_ad', json={
        "site": {
            "id": "foo123",
            "page": "http://www.foo.com/why-foo"},
        "device": {
            "ip": "69.250.196.118"
        }, "user": {
            "id": "9cb89r"}
    }

    )
    assert response.status_code == 200

# Test for server error (400) if the server receives a request with site.id
# missing, i.e, either empty or null


def test_invalid_siteid(client):
    response = client.post('/inject_ad', json={"site":
                                               {"page": "http://www.foo.com/why-foo"}, "device": {
                                                   "ip": "69.250.196.118"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400

# Test for server error (400) if the server receives a request with site.page
# missing, i.e., either empty or null


def test_invalid_sitepage(client):
    response = client.post('/inject_ad', json={"site": {"page": ""},
                                               "device": {"ip": "69.250.196.118"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400

# Test for server error (400) if the server receives a request with site.page
# invalid, i.e., malformed URL


def test_invalid_sitepage_address(client):
    response = client.post('/inject_ad', json={"site": {"page": "// www.foo.com/why-foo"}, "device": {
        "ip": "69.250.196.118"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400


# Test for server error (400) if the server receives a request with device.ip
# missing, i.e., either empty or null
def test_invalid_sitepage_address_null(client):
    response = client.post('/inject_ad', json={"site": {"page": "// www.foo.com/why-foo"}, "device": {
        "ip": ""}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400


# Test for server error (400) if the server receives a request with device.ip
# invalid, i.e., not a valid IP
def test_invalid_device_ip(client):
    response = client.post(
        '/inject_ad', json={"site": {"page": "// www.foo.com/why-foo"}, "device": {"ip": "69.250.196."}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400


def test_invalid_device_ip_address(client):
    response = client.post(
        '/inject_ad', json={"site": {"page": "// www.foo.com/why-foo"}, "device": {}, "user": {"id": "9cb89r"}})
    assert response.status_code == 400


# Test for server aborting request (500) (and not continuing with demographics
# or geolocation) if the server receives a request with site.id valid, i.e.,
# not null but the remote call failed as invalid
def test_server_aborting(client):
    response = client.post('/inject_ad', json={"site": {"id": "", "page": "http://www.foo.com/why-foo"}, "device": {
        "ip": "69.250.196.118"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 500
    assert response.get_json() is None


def test_invalid_request(client):
    response = client.post('/inject_ad', json={'key': 'value'})
    assert response.status_code == 400


# Testing for ip address outside USA


def test_invalid_geo_ip(client):
    response = client.post('/inject_ad', json={"site": {"id": "foo123", "page": "http://www.foo.com/why-foo"}, "device": {
        "ip": "204.101.161.58"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 404

# Publisher.id is a requred field in response


def test_publisher_id_isReq(client):
    response = client.post('/inject_ad', json={"site": {"id": "", "page": "http://www.foo.com/why-foo"}, "device": {
        "ip": "204.101.161.58"}, "user": {"id": "9cb89r"}})
    assert response.status_code == 500

# Testing a valid json


def test_valid_json(client):
    response = client.post(
        '/inject_ad', json={"site": {"id": "foo123", "page": "http://www.foo.com/why-foo"}})
    assert response.status_code == 400

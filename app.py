from flask import Flask, json, jsonify, Response, request
import requests
import time
import threading
import concurrent.futures
from concurrent.futures import CancelledError
import geoip2.webservice

app = Flask(__name__)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=200)

rpc_timeout = 0.5


@app.route("/inject_ad", methods=['POST'])
def inject_ad():
    start_time = time.time()
    if request.is_json is False:
        return Response(response="Expecting JSON input", status=400)
    content = request.get_json()
    if content is None:
        return Response(response="Expecting JSON input", status=400)
    try:
        site = content['site']
        id = site["id"]
        page = site["page"]
        device = content['device']
        ip = device['ip']
    except KeyError:
        return Response(
            response="A required field is missing in request", status=400)
    try:
        f1 = executor.submit(inject_publisher, id)
    except Exception as exc:
        print('%r generated an exception for inject_publisher : %s'
              % (id, exc))
        return Response(response="Unable to obtain publisher id", status=500)
    try:
        f2 = executor.submit(inject_demographics, id)
    except Exception as exc:
        print('%r generated an exception for inject_demographics: %s'
              % (id, exc))
    try:
        f3 = executor.submit(inject_geo_location, ip)
    except Exception as exc:
        print('%r generated an exception for inject_geo_Location: %s'
              % (id, exc))

    # Injecting publisher details
    publisher_response = handle_invocation("Publisher", f1)
    if publisher_response is None:
        return Response(response="Unable to fetch publisher id", status=500)
    pub = publisher_response.get('publisher')

    response = {
        "site": {
            "id": id,
            "page": page,
            "publisher": pub
        },
        "device": {
            "ip": ip,
        },
        "user": content["user"]
    }

    # Inject the country of Origin
    geo_location_response = handle_invocation("GeoLocation", f3)
    if geo_location_response is not None:
        # Aborting transaction if request originated outside United States
        if geo_location_response != "United States":
            return Response(response="IP address disallowed", status=404)
        else:
            geo = {"country": geo_location_response}
            response['device']['geo'] = geo

    # Injecting the site demographics
    demo_response = handle_invocation("Demographics", f2)
    demo = None
    if demo_response is not None:
        demo = demo_response.get('demographics')
        try:
            demo['pct_male'] = 100 - demo['pct_female']
            demo_format = {
                'female_percent': demo['pct_female'],
                'male_percent': demo['pct_male']}
        except KeyError as ex:
            print(f"Unable to obtain demographics info in response: {ex}")
        response['site']['demographics'] = demo_format
    # Building the response

    duration = time.time() - start_time
    print("Served page in {duration} seconds")

    return jsonify(response)


def handle_invocation(actor, actor_future):
    response = None
    try:
        response = actor_future.result(timeout=rpc_timeout)
    except CancelledError as e:
        print(f"{actor} future was cancelled: {e}")
    except TimeoutError as t:
        print(f"Invoking {actor} timed out: {t}")
    except Exception as ex:
        print(f"Caught exception while invoking {actor}: {ex}")
    return response


def inject_publisher(site_id):
    payload = {
        "q": {
            "siteID": site_id
        }
    }
    try:
        response = requests.post(
            "http://159.89.185.155:3000/api/publishers/find", json=payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def inject_demographics(site_id):
    baseUrl = "http://159.89.185.155:3000/api/sites/"
    url = baseUrl + site_id + "/demographics"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def inject_geo_location(ip):
    client = geoip2.webservice.Client(141233, 'keNPNwmRB1WR')
    try:
        response = client.insights(ip)
        return (response.country.name)

    except requests.exceptions.RequestException as e:
        print(e)
        return None


if __name__ == "__main__":
    app.run(threaded=False, processes=50)

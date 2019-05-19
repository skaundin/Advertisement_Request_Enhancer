from flask import Flask, json, render_template, url_for, jsonify, Response, request
import requests, omdb, time, threading, concurrent.futures
import geoip2.webservice
app = Flask(__name__)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

@app.route("/inject_ad", methods=['POST'])
def inject_ad():
    start_time = time.time()
    if (request.is_json == False):
        return "Not a json input"
    content = request.get_json()
    site = content['site']
    id = site["id"]
    device = content['device']
    ip = device['ip']
    f1 = executor.submit(inject_publisher,id)
    f2 = executor.submit(inject_demographics,id)
    f3 = executor.submit(inject_geo_location,ip)
    
    publisher_response = f1.result()
    if publisher_response is None:
        return Response(response="Unable to fetch publisher id", status=500)
    pub = publisher_response.get('publisher')

    demo_response = f2.result()
    demo = None
    if demo_response is not None:
        demo = demo_response.get('demographics')

    geo_location_response = f3.result()
    #if geo_location_response is None:
        #return Response(response="Unable to fetch Geo_Location id", status=500)
    
    response = {
                    "site": {
                        "id": id,
                        "page": site["page"], 
                        "demographics": demo,
                        "publisher": pub
                    },
                    "device": {
                        "ip": ip, 
                        "geo": {
                            "country": "US" 
                        }
                    }, 
                    "user": content["user"]
    }
    duration = time.time()  - start_time
    print(f"Served page in {duration} seconds")

    return jsonify(response)
    #Response(jsonify(response), content_type="application/json", status=200)
    

def inject_publisher(site_id):
    payload = {
        "q": { 
            "siteID": site_id
        }
    }
    try:
        response = requests.post("http://159.89.185.155:3000/api/publishers/find", json=payload)
        if response.status_code == 200 :
            return json.loads(response.text)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None 

def inject_demographics(site_id):
    baseUrl = "http://159.89.185.155:3000/api/sites/" 
    url = baseUrl + site_id +  "/demographics"
    try:
        response = requests.get(url)
        if response.status_code == 200 :
            return json.loads(response.text) 
        else :
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None 

def inject_geo_location(ip):
    url = "https://geoip.maxmind.com/geoip/v2.1/country/" + ip
    try:
        response = requests.get(url)
        if response.status_code == 200 :
            return json.loads(response.text) 
        else :
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None 

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()        
@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == "__main__":
    app.run()
    
    
# Advertisement_Request_Enhancer

This is a microservice endpoint that enhances an incoming advertisement request with additional contextual information 
This has been implemented using python3 

Files included :
- app.py - microservice
- post_data.txt - incoming request 
- curl_format.txt - To measure the latency 

## Prerequisites for Installations/tools 
- pip install python3
- pip install flask 
- pip install requests
- A free trail account at https://www.maxmind.com/en/home
- pip install geoip2
- pip install curl 
- pip install pytest 

## Running the web server 
- python3 app.py  
- To measure latency :
curl -w "@curl-format.txt" -d@post_data.txt -H "Content-Type:application/json" http://localhost:5000/inject_ad

## Testing 
pytest 

### Resources 
 - Publisher Lookup Service
Documentation:
http://159.89.185.155:3000/apidoc/
 
API:
POST ​http://159.89.185.155:3000/api/publishers/find
The Site -> Publisher Mapping rarely changes. In fact, it basically only changes when one Publisher buys out another Publisher.
 
- Demographics Lookup Service
Documentation:
http://159.89.185.155:3000/apidoc/
API:
GET ​http://159.89.185.155:3000/api/sites/SITE_ID/demographics
The per-Site demographics data is typically refreshed on a weekly basis.
  
- Geo-IP Lookup
We recommend using a library that is based upon the MaxMind data (free trial account should work):
https://dev.maxmind.com/geoip/


### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

#### Authors
Suchita Kaundin






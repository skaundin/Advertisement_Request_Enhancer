# Advertisement_Request_Enhancer

This is a microservice endpoint that enhances an incoming advertisement request with additional contextual information 
This has been implemented using python 

Files included :
- publisher_lookup_service.py - microservice
- post_data.txt - incoming request 
- curl_format.txt - To measure the latency 

## Prerequisites for Installations/tools 
- pip install flask 
- pip install requests
- A free trail account at https://www.maxmind.com/en/home
- pip install geoip2
- pip install curl 
- pip install pytest 

## Running the web server 
- python publisher_lookup_service.py 
- To measure latency :
curl -w "@curl-format.txt" -d@post_data.txt -H "Content-Type:application/json" http://localhost:5000/inject_ad

## Testing 
pytest 

### Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

#### Authors
Suchita Kaundin






var express = require('express');
var bodyParser = require('body-parser');
var req = require('request');
var app = express();
var rp = require('request-promise');

app.use(express.json());

var port = 8081;

app.post('/inject_ad', function (request, response) {
    console.log('POST /');
    content = request.body;
    site = content['site'];
    site_id = site["id"];
    page = site["page"];
    device = content['device'];
    ip = device['ip'];
    //response.send(site);

    payload = {
        "q": {
            "siteID": site_id
        }
    }

    var publisher_options = {
        method: 'POST',
        uri: 'http://159.89.185.155:3000/api/publishers/find',
        json: payload,


    }

    var demo_options = {
        method: 'GET',
        uri: 'http://159.89.185.155:3000/api/sites/' + site_id + '/demographics',
        json: true
    }
    var promises = [];
    var promises_result = [];
    var promise1 = rp(publisher_options).then(function (body) {
        console.log(body);
        promises_result.push(body);
    }).catch(function (err) {
        console.log("promise1  failed");
    });


    var promise2 = rp(demo_options).then(function (body) {
        demo = body['demographics'];
        demo['pct_male'] = 100 - demo['pct_female'];
        demo_format = {
            'female_percent': Math.round(demo['pct_female']),
            'male_percent': Math.round(demo['pct_male'])
        }
        resp['site']['demographics'] = demo_format
        console.log(demo_format);
    }).catch(function (err) {
        console.log("promise2 failed");
    });

    function geo_location(ip) {
        const WebServiceClient = require('@maxmind/geoip2-node').WebServiceClient;

        const client = new WebServiceClient(141233, 'keNPNwmRB1WR');

        client.insights('69.250.196.118').then(response => {
            console.log(response.country.isoCode);
            if (response.country.isoCode != "US") {
                console.log("status:404");
            }
            else {
                geo = { "country": response };
                console.log(geo);
                resp['device']['geo'] = geo
            }
        });
    }


    var promise3 = geo_location();


    promises.push(promise1);
    promises.push(promise2);
    promises.push(promise3);

    pub = promises_result.pop();

    resp = {
        "site": {
            "id": site_id,
            "page": page,
            "publisher": pub
        },
        "device": {
            "ip": ip,
        },
        "user": content["user"]
    }


    Promise.all(promises).then(function (body) {

        resp['site']['demographics'] = demo_format;
        console.log(resp);
        response.status(200).json(resp);
    }).catch(function (err) {
        console.log(`Error: ${err.message}`)
        response.status(500);
    });
});

app.listen(port);
console.log('Browse to http://127.0.0.1:' + port);
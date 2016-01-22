# PowerDNS GeoIP Weighted Round Robin plugin (pgwrr)

## Overview

Pgwrr is a [pipe backend](https://doc.powerdns.com/md/authoritative/backend-pipe/) for [PowerDNS](https://www.powerdns.com/opensource.html) which can geographically locate the incoming DNS request, and load balance it with the weighted round robin algorithm.

## Example usage

### PowerDNS configuration
```pipe-command=/usr/bin/pgwrr -g geoip2.mmdb -z zones.yml -s sites.yml```

Three databases are required:

* [GeoLite2](http://dev.maxmind.com/geoip/geoip2/geolite2/) or [GeoIP2](https://www.maxmind.com/en/geoip2-city) City database from [MaxMind](https://www.maxmind.com/)
* `zones.yml` file which defines the mapping between countries and arbitrary geographical zones
* `sites.yml` file which holds the DNS records for given zones with weights

### zones.yml

```yaml
'default': eu        # Default zone for the world is "eu"
'US':
  'default': us-east # Default zone for the US is "us-east"
  'CA': us-west      # Map California to "us-west"
'CN': asia           # Map China to "asia"
```

### sites.yml
```yaml
'*.example.com':
  IN:
    A:
      content:
        ttl: 300
        default:
          10.0.0.1: 100 # default for all zones
        us-east:
          10.0.0.2: 30  # 30% of requests
          10.0.0.3: 70  # 70% of requests
        us-west:
          10.0.0.4: 20  # 20% of requests
          10.0.0.5: 20  # 20% of requests
          10.0.0.6: 60  # 60% of requests
```

In the above example, any request going to `*.example.com` from

* California will resolve to either `10.0.0.4`, `10.0.0.5`, or`10.0.0.6`
* the rest of the US will resolve to `10.0.0.2` or `10.0.0.3`
* the rest of the world will resolve to `10.0.0.1`

## Recommendations

### Specify a zone for every country

For best performance it is highly recommended to specify a zone for every single country using the [ISO 3166-1 alpha-2 country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2). If you want to have country regions in different zones, you must use the [ISO 3166-2 country subdivision code](https://en.wikipedia.org/wiki/ISO_3166-2) under the country code. You must also specify a `default` zone both for countries and, if applicable, subdivisions in case GeoIP does not return a country or subdivision code.

### Use the plugin only when necessary

It would be best if this plugin is used only when needed, as in only for domain names that you actually _can_ load balance. This is easy to set up in PowerDNS with:
```
launch=pipe,bind
pipe-regex=^filter_regex;(A|ANY)$
pipe-command=/usr/bin/pgwrr -g geoip2.mmdb -z zones.yml -s sites.yml
```
The above configuration will use the pipe backend only if it passes the pipe-regex. In all other cases it will use the bind backend.

## Testing
### Download the GeoLite2 City database
```sh
sh geoip/download.sh
```
### Set up the Python path
```sh
export PYTHONPATH=$(pwd)
```
### Run tests
```sh
nosetests
```
### Run tests on change
```sh
sniffer
```
### Build and test rpm install
```sh
vagrant up
```

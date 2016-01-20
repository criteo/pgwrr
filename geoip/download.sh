#!/usr/bin/env sh

# Download GeoLite2 City database from:
# http://dev.maxmind.com/geoip/geoip2/geolite2/
wget -P geoip/ http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz

# Extract
gunzip geoip/GeoLite2-City.mmdb.gz

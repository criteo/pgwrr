# PowerDNS GeoIP Weighted Round Robin pipe backend plugin (pgwrr)

## Testing

### Download GeoIP2 City database
        sh geoip/download.sh
### Set up the python path
        export PYTHONPATH=$(pwd)
### Run tests
        nosetests
### Run tests on change
        sniffer
### Build and test rpm install
        vagrant up

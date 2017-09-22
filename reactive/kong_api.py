from charms.helpers import hookenv, unitdata
from charms.reactive import when, when_not, set_state


@when('http.available')
@when_not('kong-api.connected')
def connect_http_service(http):
    db = unitdata.kv()
    services = http.services()
    for service in services:
        for host in service['hosts']:
            db.set('service', services['service_name'])
            db.set('hostname', host['hostname'])
            db.set('port', host['port'])
            hookenv.log('{} has a unit {}:{}'.format(
                services['service_name'],
                host['hostname'],
                host['port']))
    set_state('kong-api.connected')

@when('kong-api.connected', 'apis.available')
@when_not('kong-api.installed')
def install_kong_api(apis):
    db = unitdata.kv()
    conf = hookenv.config()

    service = hookenv.service_name()
    upstream_url = "http://{}:{}".format(db.get('hostname'), db.get('port'))
    hosts = conf.get('hosts').split(',')
    uris = conf.get('uris').split(',')
    methods = conf.get('methods').split(',')

    apis.add_api(service, upstream_url, hosts, uris, methods)
    set_state('kong-api.installed')

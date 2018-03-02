from flask_restful import fields, marshal, Resource, abort
from modules.openstack_controller.controller import OpenStackController

import logging
LOGGER = logging.getLogger(__name__)

## this is not really needed anymore. We can marshall with server_resource_fields if needed
rule_resource_fields = {
    'qos_policy_id': fields.String,
    'id': fields.String,
    'type': fields.String,
    'direction': fields.String,
    'max_burst_kbps': fields.Integer,
    'max_kbps:': fields.Integer
}

qos_policy_resource_fields = {
    'description': fields.String,
    'id': fields.String,
    'name': fields.String,
    'rules': fields.List(fields.Nested(rule_resource_fields))
}

fixed_ip_resource_fields = {
    'subnet_id': fields.String,
    'ip_address': fields.String
}

port_resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'fixed_ips': fields.List(fields.Nested(fixed_ip_resource_fields)),
    'qos_policy': fields.Nested(qos_policy_resource_fields)
}

server_resource_fields = {
    'name': fields.String,
    'id': fields.String,
    'project_id': fields.String,
    'ports': fields.List(fields.Nested(port_resource_fields))
}

OSController = OpenStackController()

class qos(Resource):
    def get(self):
        servers = OSController.getQoSPolicies(filter_ip=None)
        return servers

class qosDetail(Resource):
    def get(self, ip_address):
        servers = OSController.getQoSPolicies(filter_ip=ip_address)
        return servers